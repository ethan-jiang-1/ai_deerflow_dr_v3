# Design

## Context

动机见 `proposal.md` — Why。这里只记塑造方案形态的现状与约束（阶段 1 之后的实测）。

**规模与形态（实测）**

| 文件 | LOC | 顶层函数 | >50 行函数 | 最长函数 |
|---|---|---|---|---|
| `check_change_guidance.py` | 1,473 | 37 | 6 | 137（`_validate_change_guidance_tree`） |
| `check_project_architecture.py` | 1,024 | 33 | 3 | 269（`load_manifest`） |
| `check_doc_hygiene.py` | 864 | 21 | 1 | 182（`_rule_ledger_consistency`） |
| 其余 10 个文件 | ~2,655 | — | 4 | ≤79 |

**四条硬约束（决定"薄入口"这一形态）**

1. **CI 与 hook 按精确路径调用**：`.github/workflows/governance.yml:54` 与
   `.githooks/pre-commit:10` 调用 `check_doc_hygiene.py`；`check_project_gate.py:44` 的组件
   清单按文件名调用 `check_project_architecture.py`、`check_change_guidance.py` 等。入口
   文件名不可动。
2. **测试会把组件脚本复制到临时树执行**：`test_project_gate.py` 的
   `_make_repo`（:59-72）与 `RealChangeGuidancePlantedNegativeTest._FIXTURE_SOURCES`
   （:429-445）按**路径**复制 `check_change_guidance.py` 与 `change_guidance_kernel.py`
   到隔离树，然后以子进程执行。→ 入口必须**自足**（不依赖调用方的 `sys.path` 设置），
   且 kernel 必须留在顶层原位置。
3. **测试直接 import 入口符号**：`test_change_authority.py:26` 取
   `ContractViolation` 与 `_validate_change_tasks`；`test_split_manifest.py:100` 经
   `importlib` 装载 arch checker 并调用其公共名。→ 入口必须 re-export 现有可达面。
4. **kernel 是独立登记文件**：`required-paths.toml:75` 列 `change_guidance_kernel.py`，
   `test_project_gate.py:439-440` 按该路径复制它。→ 不并入子包。

## Goals / Non-Goals

**Goals:**

1. 两个千行级 checker 各自变成「入口（CLI + 文档字符串 + re-export，≤120 行）+
   职责子包」；`load_manifest` 与 `_rule_ledger_consistency` 拆成命名子步骤。
2. 每个 checker 的 CLI 文本、退出码、违规文本**逐字不变**；测试可达面不变。
3. 新子包进 manifest 登记，架构 checker 保持绿。

**Non-Goals:**

- 不动任何判定语义、违规文本、规则顺序。
- 不做去重与死码清偿（阶段 3）；不拆 `check_doc_hygiene.py` 的文件级结构；
  不拆 `_battery.py`；不碰 kernel 的文件名与位置；不碰 harness 与 CI。
- 不引入新依赖、不做"现代化"重写。

## Decisions

### D-1｜子包命名带 `_check` 后缀，避免与 guidance 文档树混淆

`openspec/governance/` 下新增子包时，`change_guidance/` 会与仓库既有文档树
`openspec/change-guidance/`（连字符）在口头与搜索中互相干扰。

- **选**：`change_guidance_check/` 与 `project_architecture_check/`。
- **代价**：名字略长。
- **换来**：搜索 `change_guidance_check` 只会命中代码；`change-guidance` 仍专指文档。
- 备选：`change_guidance/`（更短，但与文档树混淆）；把实现塞进 `check_*.py` 同名的包
  （Python 包名不能与模块名相同而共存于一处，需改名入口，撞约束 1）。否。

### D-2｜入口是薄壳，且**自足**：自己把 governance 目录挂上 `sys.path`

子进程可能从任意 cwd 执行入口（测试夹具即如此），且不会预设 `PYTHONPATH`。

- **选**：入口顶部做一次幂等的 `sys.path` 插入（`Path(__file__).resolve().parent`），
  然后 `from change_guidance_check import ...`。这与 `_battery.py` 被
  `check_doc_hygiene.py` 导入的既有形态一致（阶段 1 已验证可行）。
- **代价**：入口多三行引导代码。
- **换来**：临时树夹具、CI、hook、裸跑四种调用方式全部无需环境变量。
- 备选：`python -m` 包执行（改变 CI 命令字符串，撞约束 1）；相对导入（脚本直接执行时
  不成立）。否。

### D-3｜入口 re-export 现有测试可达面（迁移期契约）

- **选**：入口显式 re-export `ContractViolation`、`_validate_change_tasks`（guidance）与
  arch checker 的公共名；并在入口文档字符串注明"这些名字为迁移期兼容面，测试仍按其
  寻址"。
- **代价**：入口多几行 import。
- **换来**：测试零改动；若测试零改动而全绿，就等于"拆分没有偷偷改掉可达面"的证据。
- 备选：改测试的 import 指向子包（测试改动会削弱"零行为变化"这一验收信号）。否。

### D-4｜`check_doc_hygiene.py` 只做函数级分解，不做包级拆分

- **选**：把 182 行的 `_rule_ledger_consistency` 拆成命名的子步骤函数，仍留在原文件；
  864 行的文件不再切分。
- **代价**：该文件仍是本目录第 3 大。
- **换来**：避开真风险——`_battery.py` 依赖 `check_doc_hygiene.py` 的 `RULES`/`Scope`，
  反过来入口又要 import `_battery`（`--self-test`），包级拆分会把这条已有的双向引用
  变成循环 import 的温床，而收益（864 行 → 若干小文件）远小于风险。
- 备选：拆成 `doc_hygiene_check/` 包（收益小、风险实；若将来体积回升，由阶段 3 的
  `code-budgets` 守卫带着预算重启此议题）。

### D-5｜拆分顺序：先 arch checker（依赖面最小），再 guidance checker（依赖面最大）

- **选**：先做 `check_project_architecture.py`（被 import 的公共名少、无复制型夹具），
  验证"薄入口 + 自足引导 + re-export"这套形态在门禁与套件下成立；再做
  `check_change_guidance.py`（有复制型夹具 + 两处直接 import），最后做 doc-hygiene 的
  函数分解。
- **代价**：无法并行两个拆分。
- **换来**：形态风险在第一个目标上暴露，而不是在最复杂的那个上。

## Alternatives

- **A-1 用 `python -m` 包入口替换脚本入口**：会改变 CI/hook/文档的命令字符串（约束 1）。
  否。
- **A-2 把实现放进与入口同名的包（`check_change_guidance/`）**：Python 不允许同一目录下
  同名模块与包共存，必须改入口名，撞约束 1。否。
- **A-3 把 kernel 并入新子包"顺手收拾干净"**：kernel 是独立登记文件且被测试夹具按路径
  复制（约束 4），并入会同时触发 manifest 改动、policy 文档改动与夹具改动三处——属阶段 3
  的收敛议题。否。
- **A-4 借拆分顺带做去重（6 份 git 包装合 1、finding 形状统一）**：那会引入语义等价性
  判断（例如六份包装的错误处理差异哪一份才是对的），与"只搬不改"的验收边界冲突。
  阶段 3 专做此事。否。

## Risks / Trade-offs

- [拆分后某条规则在入口与子包之间出现双份实现] → 入口只做 CLI + re-export，规则体全部
  在子包；验收行明确"入口不得包含规则逻辑"（以入口行数上限 + 评审双查）。
- [子进程调用找不到子包] → D-2 的自足引导 + 任务里的"临时树夹具仍工作"验收行（直接跑
  治理套件，其中就含复制型夹具用例）。
- [re-export 遗漏某符号导致测试红] → 这是**期望的**失败信号：测试零改动，红了就说明可达面
  变了，补齐即可；不得改测试来绕过。
- [迁移期 import 路径变化引入循环] → 约束 4 已把 kernel 排除在子包外；子包内部只向
  kernel 与 stdlib 取依赖，不反向 import 入口。
- [拆分让 diff 巨大、review 成本高] → 用"纯搬移可验证"的方式降本：每个 checker 的 stdout
  在改造前后逐字比对 + 套件用例数不减 + 违规文本由绿地对照复核。

## Migration Plan

按 D-5 的顺序分三步推进，每步以"该步结束时的树 + 六条门禁绿 + 套件用例数不减"为提交边界。

1. arch checker：建 `project_architecture_check/`，移入规则体，入口改薄壳并 re-export，
   `load_manifest` 拆三段；登记 manifest；跑门禁与套件。
2. guidance checker：建 `change_guidance_check/`，移入规则体，入口改薄壳并 re-export；
   登记 manifest；跑门禁与套件。
3. doc-hygiene：分解 `_rule_ledger_consistency`；跑门禁与套件（含 `--self-test` 与
   `_battery.py` 的 39 条控制）。

**回滚**：本 change 不产生运行时状态、不迁移数据；回滚 = 撤销该步 diff（manifest 的登记
条目随同撤销）。无数据面残留。
