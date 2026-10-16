# Design

## Context

动机见 `proposal.md` — Why。这里只记塑造方案形态的现状、约束与实测数字。

**去重目标的实测形态**

| 重复面 | 份数 | 差异（决定了"能共享什么"） |
|---|---|---|
| git 调用 | 6 | 抛 `ContractViolation`（`gitlink.py:14`）／吞 `OSError` 返 `None`（`check_release_face.py:53`）／无护栏（`check_proof_receipts.py:34`）／返回 bytes（`selected-change-closeout.py:80`）／测试侧一份 |
| 仓库根解析 | 5 | `parents[2]`／`parents[3]`／`Path.cwd()`／argv 优先 + `parents[2]` 兜底／`__file__` 派生 |
| finding 形状 | 3 | 抛出 `ContractViolation`（多数）／返回 `tuple[ValidationIssue, ...]`（kernel）／返回 `list[str]`（若干净查器） |

**硬约束**

1. **ci-governance 钉死命令集**：`check_ci_governance.py:43`（workflow 必需 marker 列表）与
   `:69-82`（hook 允许行 + 必需 marker）是封闭集合；新增守卫步必须**同改声明**，
   否则该 checker 红。
2. **doc-hygiene 钉死 specs 计数**：`_rule_root_counts` 要求根 `README.md` 声明
   `specs 主干 N 个能力`；新建 capability 让 N 从 13 变 14。
3. **阶段 2 刚建立的形态**：两个 checker 已是薄入口 + 子包；新共享层放 `governance/` 顶层
   （与 `change_guidance_kernel.py` 同级，同属"被多个 checker 复用"的角色）。
4. **失败路径不在逐字比对的覆盖内**：阶段 2 抓到过 `facade.py` 漏 `import sys` ——成功路径
   全绿、失败路径才炸。故本 change 的验证必须**额外跑一轮种植违规的失败路径比对**。

## Goals / Non-Goals

**Goals:**

1. 6 份 git 调用与 5 个根解析变体复用共享层，**各自默认值与错误处理不变**。
2. kernel 删 88 行零引用定义（可达性分析确认，非引用计数猜测）。
3. `load_manifest` 171 → 三段式（解析 / 校验 / 构造）。
4. 新增 `code-budgets` capability：声明式上限、超限点名、缺失失败、棘轮、自带可失败负例。
5. 六个既有 checker 的 stdout 与退出码在成功与失败两条路径上逐字不变。

**Non-Goals:**

- 不改任何判定语义、违规文本、退出码。
- 不强行统一 finding 形状（见 D-5 与 Alternatives）。
- 不碰 harness、不碰 `deerflow/`、不拆 `check_doc_hygiene.py` 的文件结构。
- 不引入新依赖（stdlib only）。

## Decisions

### D-1｜`gitio.py` 只共享"怎么调 subprocess"，不共享"出错怎么办"

六份包装的**差异正是各自 checker 的错误语义**（抛/吞/无护栏、bytes/str）。统一错误处理会
改变失败路径的可观察行为，撞本 change 的不变量。

- **选**：`run_git(arguments, *, cwd=None, text=True) -> CompletedProcess`——显式 `cwd`、
  可切 `text`、`check=False`、**从不抛**。调用点各自判断 `returncode` 并保留原有反应。
- **代价**：调用点仍有几行各自的错误分支（这是语义，不是重复）。
- **换来**：共享的是真正重复的部分（argv 拼法、`cwd` 传递、捕获设置），失败行为逐字不变。
- 备选：统一成"git 不可用即抛 `ContractViolation`"——会让 `check_release_face.py` 从
  返回 `None` 变成抛异常，退出码与消息都变。否。

### D-2｜`roots.py` 提供参数化的根解析，不统一默认值

五个变体的默认值（`parents[2]`／`parents[3]`／`Path.cwd()`／argv 优先）**是各自 CLI 契约的
一部分**：`selected-change-closeout.py` 从 cwd 解析是它的用法（操作者在仓库里跑），
`check_project_gate.py` 从 `__file__` 派生是它的独立性要求。

- **选**：`resolve_root(argv_value: str | None, *, default: Path) -> Path`——请求方传自己的
  默认值，共享 argv 优先 + `resolve()` 的这段逻辑。
- **代价**：调用点各写一行默认值表达式。
- **换来**：解析语义一致，默认值契约不漂移。
- 备选：统一为 `__file__` 派生——会改变 `check_ci_governance.py`（`Path.cwd()` 默认）与
  `selected-change-closeout.py`（cwd）的可观察行为。否。

### D-3｜`code-budgets` 是声明驱动的薄 checker，自带 `--self-test` 负例

- **选**：一份 `CODE_BUDGETS` 声明表（`path -> (max_lines, max_over_length_functions,
  over_length_threshold)`），checker 读表测量；`--self-test` 在临时树里种一个超限文件与一个
  超长函数，两者都必须被报出。棘轮纪律写进表注释（review 级，checker 只管当前边界）。
- **代价**：声明表要人工维护（这正是"可见变更"的设计意图）。
- **换来**：体积回归第一次有了机器闸，且闸本身可被证明会红。
- 备选：并入 `check_project_architecture.py`——否，那会让"结构枚举"与"代码预算"两种语义
  混在一个 capability（阶段 1 的评估已把此点列为 B2 决策，owner 选了独立 capability）。

### D-4｜`load_manifest` 三段式用一个中间值对象承载 19 个校验产物

阶段 2 只提取了两个天然子块（fixture 声明、清单），因为构造段直接引用 19 个中间变量，
硬拆要加参数对象。本次补完：解析段产出原始文档，校验段产出**一个冻结的中间值对象**，
构造段由它装配 `StructureManifest`。

- **选**：新增私有 `_ManifestParts`（dataclass），校验段填它，构造段读它。
- **代价**：多一个内部类型（不出模块）。
- **换来**：三个函数各有单一职责，`load_manifest` 降到 ~25 行编排；错误码与抛出顺序逐字不变。
- 备选：继续维持 171 行——否，它是全库最长函数，且阶段 3 正是处理它的时机。

### D-5｜共享层放 `governance/` 顶层，随 `required-paths.toml` 登记

- **选**：`gitio.py`、`roots.py` 落在 `openspec/governance/`（与 `change_guidance_kernel.py`
  同级）；两者都不 import 任何 checker（依赖方向单向：checker → 共享层）。
- **代价**：顶层多两个文件。
- **换来**：子包内的 checker 与顶层 checker 都能用同一份实现，不产生包间依赖。
- 备选：放进某个子包——会让另一个子包反向依赖它。否。

### D-6｜新守卫的接入面：CI 一步 + hook 一行 + ci-governance 声明同步

- **选**：`.github/workflows/governance.yml` 增一步
  `python3 openspec/governance/check_code_budgets.py`（紧随 doc-hygiene 之后）；
  `.githooks/pre-commit` 增同一行；`check_ci_governance.py` 的
  `WORKFLOW_REQUIRED_MARKERS` / `ALLOWED_HOOK_LINES` / `HOOK_REQUIRED_MARKERS` 三处同步。
- **代价**：hook 多一次全树 AST 扫描（实测亚秒级）。
- **换来**：体积回归在**提交时**就被拦，而不是等 CI。
- 备选：只进 CI 不进 hook——否，体积回归是"改完立刻可见"的类，hook 处拦截成本最低。

## Alternatives

- **A-1 强行统一 finding 形状为一种**：三种形状各有语义——抛出型（`ContractViolation`）
  承载"点到即止的准入失败"，列表型承载"一次报全部的不卫生"，kernel 的
  `ValidationIssue` 元组承载"纯函数式的问题集合、可被任意搜集"。统一为一种必然改变至少
  两个 checker 的失败路径与退出码（例如把 `check_release_face.py` 的列表型改为抛出型，
  它就只报第一条而非全部）。与本 change 的"逐字不变"边界冲突。**只共享底层，不动形状**；
  若将来要统一，须由 owner 单独立项并接受可观察行为变更。
- **A-2 把 `code-budgets` 并进 `doc-budgets`**：`doc-budgets` 的单位是"字符/常驻指令文档"，
  语义是"每会话注入的提示厚度"；代码预算是"行数/函数长度"。合并会污染既有 capability 的
  语义边界。否。
- **A-3 顺手把 `check_doc_hygiene.py` 也拆包**：阶段 2 已裁定不做（`_battery.py` ↔
  `RULES` 的双向引用会变成循环 import 温床），本 change 不翻案。
- **A-4 删死码时连带删掉"看起来没人用"的 kernel 导出注释与 `__all__`**：kernel 没有
  `__all__`，删除即完成；不动其余注释（它们是既有解释，非死码）。

## Risks / Trade-offs

- [共享层改变某 checker 的失败路径] → D-1/D-2 明确"只共享调用、不共享反应"；验证跑一轮
  **种植违规的失败路径逐字比对**（不只跑成功路径）。
- [删死码删掉了某处动态引用（`getattr` 字符串）] → 全树活跃代码与测试的引用计数为 0，且
  kernel 内无 `getattr`/`__all__` 动态面；删除后套件与六 checker 逐字比对为准。
- [`load_manifest` 三段式改动错误抛出顺序] → 该函数抛的是 `ContractViolation`，顺序即
  首个触发者；用**种植清单缺陷**逐个触发各段的首个错误码，比对改造前后。
- [code-budgets 表一上线就把现有文件判红] → 上限按**当前实测值**设定（阶段 2 后的真实数字），
  即"今天全绿、今后只降"；表里每个数字都在 apply 时由脚本实测填入，不拍脑袋。
- [新增 CI 步破坏 ci-governance 封闭集合] → D-6 的三处声明同步，且该 checker 本身会在
  apply 中被跑（它就是"改序列必须同改声明"的守卫）。
- [hook 变慢] → 预算 checker 只做 AST 行长统计，实测亚秒；若超过 1 秒则改为只查变更文件
  （记入已知限制，不在本 change 扩张）。

## Migration Plan

按 6 步推进，每步以"该步结束时的树 + 六条门禁绿 + 套件不减"为提交边界。

1. `gitio.py` + 6 个调用点切换（成功路径 + 失败路径逐字比对）。
2. `roots.py` + 5 个解析点切换（同上）。
3. kernel 删 88 行死码（套件 + 六 checker 逐字比对）。
4. `load_manifest` 三段式（种植清单缺陷逐个触发错误码比对）。
5. `check_code_budgets.py` + 测试 + 声明表（上限按实测值填）+ `--self-test` 负例。
6. 接入面同步（workflow / hook / ci-governance 声明 / required-paths / README 组件表 /
   根 README specs 计数 13 → 14）；全门禁 + 绿地对照 + 变红证明。

**回滚**：本 change 不产生运行时状态、不迁移数据；回滚 = 撤销该步 diff（新增文件删除、
登记条目随同撤销）。无数据面残留。
