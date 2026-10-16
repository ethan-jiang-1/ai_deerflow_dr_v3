# Design

## Context

动机见 `proposal.md` — Why。这里只记塑造了方案形态的现状与约束。

**现状（实测）**

| 事实 | 位置 |
|---|---|
| 九条规则 = 8 个 `_rule_*` + 1 个范围规则 | `_rule_adr_index:163`、`_rule_links:191`、`_rule_encoding_newline:220`、`_rule_docs_scope:240`、`_rule_backlog_underscore:254`、`_rule_doc_budgets:382`、`_rule_ledger_consistency:453`、`_rule_stale_markers:678`、`_rule_root_counts:638` |
| 调度手列九个调用 | `violations:713-725` |
| 30 个模块级声明表/常量，规则直接读 | `check_doc_hygiene.py:60-145`（+ 正则常量散落其后） |
| 一条被测试就地改写的全局量 | `MARKER_ALLOWLIST:376`；self-test 在 `:1158-1166` `clear()` + `update()` + 还原 |
| 442 行内联电池，31 条负例 | `_self_test:727-1168`；`errors.append("self-test: …")` 计数 = 31 |
| 电池的唯一入口 | `--self-test`（`main:1171`） |

**约束**

- **路径契约**：只有一条命令字符串出现在 CI 与 hook 中——
  `python3 openspec/governance/check_doc_hygiene.py`（`.github/workflows/governance.yml:54`、
  `.githooks/pre-commit:10`）。该文件名必须保持为可执行入口。
- **政策锚**：`--self-test` 被 `openspec/specs/doc-truthfulness/spec.md:171`（Scenario
  "The rule proves it can fail (self-test)"）、`openspec/governance/README.md:69`、
  `docs/skills/deep-research/verification-receipt.json:18-21` 引用为守卫变红的证据入口。
- **角色自述**：`openspec/governance/README.md:46-47` 声明 doc-hygiene 是 gate 之外的
  独立检查、非 `make verify` 目标——本 change 不改这个既定选择。
- **无 spec 管辖**：治理脚本的内部结构不由任何 capability 的 requirement 定义，也没有
  逐行导入矩阵扫描 `openspec/governance/*.py`（矩阵只遍历 harness 源码根）。

## Goals / Non-Goals

**Goals:**

1. 31 条负例控制进入 `python3 -m unittest discover -s openspec/tests/governance`
   的发现面，每条各有独立用例标识。
2. 规则不再直接读写模块级全局量：声明表成为显式传入的 `Scope`，被就地改写的
   `MARKER_ALLOWLIST` 变成规则入参。
3. `violations()` 从手列调用变为遍历注册表；加一条规则 = 加一个函数 + 注册表加一行。
4. CLI 契约零变化：文件路径、`--self-test` 命令、stdout 文本、退出码逐字不变。

**Non-Goals:**

- 不改任何规则的判定语义、违规文本与顺序。
- 不拆文件（三座大山拆分属下一阶段）；不引入代码体积守卫（属第三阶段）。
- 不把 doc-hygiene 纳入 gate 组件清单（保持既有独立检查角色）。
- 不改 `deep_research_harness/` 任何文件；不碰 `deerflow/`。
- 不为本次改动新增任何 required-path 登记。

## Decisions

### D-1｜`Scope` 值对象承载声明表，规则签名统一为 `check(scope) -> list[str]`

九条规则里八条其实只需要根路径；`_rule_stale_markers` 还读 `STALE_MARKER_FILES` 与
`MARKER_ALLOWLIST`，`_rule_doc_budgets` 读 `DOC_BUDGETS` 等。若把 `Scope` 做成
「只给需要的人传参数」，注册表就不能统一遍历。

- **选**：冻结的 `Scope`（含 `root` 与各声明表的冻结视图），所有规则统一吃它；
  九条里只有两条真的会读额外字段（`_rule_doc_budgets`、`_rule_stale_markers`）。
- **代价**：多数规则收到用不到的字段（ISP 上不最优）。
- **换来**：调度统一、规则可被任意测试点单独调用、声明表成为显式依赖。
- 备选：逐规则精确传参——被否，会让注册表退化成手列特例，抵消收益。

### D-2｜负例电池移入独立模块 `_battery.py`，`--self-test` 与 unittest 共用它

电池需要临时树夹具（`write_doc`、`hukou_card`、`vocab_bug_card` 等闭包），
放测试文件里会让产品模块无法委托；放产品模块里就是现在的问题。

- **选**：新增同目录 `_battery.py`，导出 `NEGATIVE_CASES`（每例 = 规则名 + 夹具构造 +
  期望违规子串 + 说明）与少量夹具构造助手。`check_doc_hygiene.py --self-test`
  遍历它并渲染**原有文本**；`tests/governance/test_doc_hygiene.py` import 同一份，
  为每例生成一个用例。
- **代价**：产品目录多一个模块（`openspec/governance/_battery.py`）。
- **换来**：31 条断言只有一份家；两个入口（CLI 与 unittest）不可能漂移。
- 备选 A：电池放测试文件、checker 反向 import 测试——被否：产品模块依赖测试目录，
  CI 与本地路径假设都会变脆。
- 备选 B：模块内保留一份、测试文件复制一份——被否：这恰是 31 条断言漂移的成因。

### D-3｜每例一个用例标识（便于 31 条对账），而非 31 条挤进一个用例

- **选**：测试类按规则分组（`class Rule1AdrIndexTests` …），类内用动态生成的用例方法
  （每例一个），使 `unittest` 报告的用例数与断言数都是 31 的可见倍数。
- **代价**：动态生成的方法名在失败时不如手写方法直观（用 `subTest` 的消息补足）。
- **换来**：对账可机械化——「改造后测试数 ≥ 99 + 31」是一条可直测的判据。

### D-4｜保持 `--self-test` 为薄委托（owner 2026-10-13 决策 D1）

- **选**：保留命令与输出；退役它是政策变更，须由政策 owner 另外拍板。
- **代价**：负例多一个入口（有意的冗余）。
- **换来**：doc-truthfulness 的 Scenario、governance README 的自述、既有
  verification receipt 全部继续成立，本 change 无需改任何 spec 文本。

### D-5｜逐规则绿地对照作为"零行为变化"的强探针

只跑门禁绿不能证明规则语义没被动过（旧实现与新实现可能同时对同一棵树给出不同违规）。

- **选**：任务里为每条规则安排一次**绿地对照**——对同一临时树，旧实现与新实现的
  违规文本与顺序必须相同；`_rule_docs_scope` 同样纳入（它与其余八条同契约）。
- **代价**：一次性对照成本。
- **换来**：把"重构"与"顺手改规则"在证据层分开；这是本 change 唯一能证明
  「语义零变化」的手段。

## Alternatives

- **A-1 用 pytest 风格重写电池**：本仓测试栈是 stdlib `unittest`（`make verify`、
  治理套件、CI 全部基于它）。引入新依赖只为改测试形态，收益为负。否。
- **A-2 用 dataclass 注册表替换整个 checker 框架（"现代化"重写）**：31 条负例与 99 个
  既有测试方法是全绿的既有资产，重写等于把它们降级为未验证。本 change 只搬不重写。否。
- **A-3 把 doc-hygiene 提升为 gate 组件，借 closeout gate 的聚合能力**：会改变
  `openspec/governance/README.md:44-47` 声明的组件清单与 ci-governance 的 canonical
  命令面，属规范语义/治理形态变更，与本 change 的"零行为变化"目标冲突。否。
- **A-4 趁拆分之机同时消除 `MARKER_ALLOWLIST` 的全局可变性并顺手拆分
  `_rule_ledger_consistency`（179 行）**：D-1 已消除"规则读全局"，而 179 行函数的内部
  分解属下一阶段；混入会让本 change 的"零语义变化"边界变模糊。否。

## Risks / Trade-offs

- [31 条断言在搬运中悄悄丢失或被合并] → 改造前后各生成一次断言标识全集并对账；
  数量不足 31 或出现集合差即判失败。任务内预置该命令。
- [规则语义被顺手改动] → D-5 逐规则绿地对照；对照不过即回滚该步，不"修着看"。
- [`--self-test` 双轨漂移] → 委托只调 `_battery.py`，checker 内不得留第二份断言代码
  （单一事实家）；review 时把这条当硬验收。
- [新测试文件过大（预计 ~450 行）] → 本阶段接受：拆会破坏负例注册表的单源性；
  第三阶段的体积守卫落地后连同预算一起重访。
- [规则函数的 8 个 `_rule_*` 名字进入测试标识，未来改名会牵动测试] → 可接受：名字是
  规则的稳定标识，改名本就该在 diff 里可见。
- [Scope 抽取改变"规则可单独调用"的既有假设（现在它们依赖模块全局）] → 这正是目标；
  对模块外的既有调用方无影响。**实施更正（apply 步骤 1.3–1.5）**：模块内的调用方不止
  `violations()`——内联电池自身就是规则的直接调用方（28 处 `_rule_x(<temp-tree>)` 传
  `Path`）。设计原假定"电池此步不动"是错的，实际必须让电池跟着签名走，否则 `--self-test`
  立即红。落点：`_self_test` 顶部的局部适配器 `scope(var) -> Scope.from_defaults(Path(var))`，
  28 处调用机械改写；它**不是兼容层**（模块导出面无第二套签名，规则仍只有一种入口），且随
  电池体在迁移第 3 步一并删除。依据、落点与验证见 `tasks.md` 的 Deviation Register 偏差 1。
- [Scope 的 `docs`/`limits`/`regexes` 是字符串键映射] → 打错键名是运行期 `KeyError` 而非
  静态错误。本阶段接受（映射把"声明随测试改变"变成可能，是 D-1 的代价）；电池清除后
  （迁移第 3 步完）这三个映射已无自定义需求，应在下一阶段改为具名类型化字段并把键名打错
  变成 `AttributeError`——记在 `_backlog` 的阶段 2/3 视野内，不在本 change 扩张。

## Migration Plan

按 8 个原子步子推进，每步以"该步结束时的树 + 四条门禁绿"为提交边界；任何一步红则回滚该步，
不做"部分保留 + 继续"。

1. `Scope` + 注册表（规则签名切换；**内联电池经局部 `scope()` 适配器跟进**——设计更正，
   见 Risks 第二条；行为不变）
2. `_battery.py`：31 条负例迁入（此时两处并存，逐条对账）
3. `--self-test` 委托 + 删除内联电池体与 `scope()` 适配器
4. `tests/governance/test_doc_hygiene.py` 接入同一注册表
5. `openspec/governance/README.md` 自述同步
6. 全门禁 + 断言对账 + 绿地对照复跑（收口证据）

**回滚**：本 change 不产生运行时状态、不迁移数据、不改任何登记路径，所以回滚 = git 层面
撤销该步的 diff；无数据面或路径面的残留需要清理。
