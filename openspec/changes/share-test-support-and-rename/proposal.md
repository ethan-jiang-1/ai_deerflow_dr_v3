# Proposal: share-test-support-and-rename

## Why

四个阶段的实现侧收敛（治理 checker 拆分、去重与体积闸、run pump 拆分）之后，测试面成了
唯一没被整理过的地方，而它有两类可测的债：

1. **每文件各抄一遍的夹具**。`TemporaryDirectory()` 37 处、`bundle_actions.start(` 18 处、
   固定时间戳常量 17 处（`_FIXED_NOW` / `_FIXED_BUCKET`）、`_PIN = "c" * 40` 7 处、
   `def _event` 2 份。五个 largest 测试文件里的临时 run-bundle 脚手架几乎逐字相同——
   改一次 `BundleHandle` 的构造方式要动十几个文件。仓库里唯一的共享测试资产是 25 行的
   `fixture_reports.py`。
2. **文件名与主体脱钩 + 一个大文件**。`test_run_engine.py`（674 行 / 31 测试 / **1 个类**）
   测的是 `runtime/pump.py`——那个名字在阶段 2 就已不存在（模块改名为 pump），它是全库最大
   测试文件且是杂物袋（澄清、计划闸、journal、终端转移、准入门、搜索日志混在一个类里）；
   `test_entry_composition.py` 测的是 `runtime/assembly.py`，名字对不上主体。

第三件事是政策缺口：`tests/unit/test_collection_guard.py` 有五条正向检查（包标记在场、
integration 无标记、默认发现的范围与覆盖），但**没有已知违规负例**，而
`openspec/governance/test-evidence-policy.md` 要求"新守卫必须能变红"。

现在做，是因为它是这场收敛的最后一块：实现侧已经"可按名定位、有守卫看着体积"，测试侧
还没有。做完之后"找模块 X 的测试"就是同名文件，不再依赖 `tests/README.md` 当索引。

## What Changes

- **新增 `tests/support.py`（共享夹具）**：临时 run-bundle 脚手架、固定时钟与 pin 常量、
   事件构造器（`event` / `chunk_event` / `ai` / `tool_result` / `ask_call`）、journal 读取包装
   各一份；各测试文件改为 import 它。
- **`test_run_engine.py` 按行为族拆分**：674 行的杂物袋拆成 4 个文件（澄清与自动续跑、
   计划闸、终端转移与错误回退、交付与搜索日志），每个文件一个主题。
- **测试与主体同名**：`test_run_engine.py` → `test_pump.py`（主体 `runtime/pump.py`）、
  文件名与主体不再脱钩。被拆出的子主题文件按其行为族命名（`test_pump_clarification.py`、
   `test_pump_plan_gate.py`、`test_pump_terminal.py`）。
- **补 `test_collection_guard` 的已知违规负例**：在临时树里种下"integration 带包标记"这一
   已知违规，用**同一套发现机制**证明它会让 integration 泄漏进默认门禁——即守卫关心的
   失败真的可发生、且可被观察。
- **登记与文档**：`required-paths.toml` 增 `tests/support.py` 与新测试文件；
  `tests/README.md` 的资产表随文件结构同步。

**不变量（本 change 的验收核心）**：**测试 ID 集合逐条对账**——基线 255 个 ID
（verify 面 242 + smoke 面 13，已捕获留档）在改造后**一个不少、一个不多**（同名文件的重命名
除外，那部分逐条给出新旧映射）；`make verify` 与 `make smoke` 全绿且用例数不变；`make lint`
绿；产品的 `src/` 除改名外零改动。

## Capabilities

### New Capabilities

<!-- none: 测试资产的组织方式不被任何 capability 的 requirement 管辖；本 change 不改任何
     产品行为，也不新增契约面。 -->

### Modified Capabilities

<!-- none: 同上。collection guard 的**新增负例**加强的是既有守卫的证明力，不改它锁定的
     行为（默认门禁的发现范围），故不构成 spec 变更。 -->

## Impact

- **新增**：`tests/support.py`；拆分出的测试文件。
- **改名**：`tests/unit/runtime/test_run_engine.py` → 四个按行为族命名的文件。
- **改**：各测试文件的夹具段改为 import `tests/support.py`；`test_collection_guard.py`
  补一个负例；`required-paths.toml`；`tests/README.md`。
- **不动**：`src/` 的任何行为（仅 `required-paths.toml` 登记面）；`openspec/governance/`；
  CI 与 hook 命令集；`deerflow/` gitlink。
- **触发车道**：`make verify`、`make smoke`、`make lint`（三条都要，阶段 4 的教训）。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/` —— 测试树自身；
  它拥有"共享夹具放哪、测试文件怎么按主体命名"这两个决定。
- **Seam classification:** deterministic-guardrail —— 测试资产的组织与发现合同；
  无模型参与，产品行为零变化。
- **Question:** 散在 41 个文件里的重复夹具能否收敛为一份 `tests/support.py`、674 行的
  杂物袋能否拆成按行为族命名的文件、而**255 个测试 ID 逐条不变**（改名者给出新旧映射）、
  三条车道全绿？
- **Necessary adjacent/external contracts:** `tests/unit/test_collection_guard.py`
  （answers: 默认门禁的发现范围由谁锁定？答：该守卫；补负例不得改变它的五条正向检查）；
  `tests/README.md`（answers: 资产表的权威是什么？答：它是路由不是真相，随文件结构同步）；
  `openspec/governance/required-paths.toml`（answers: 新增测试资产如何登记？答：按既有
  协议增 files 条目）；`deep_research_harness/Makefile`（answers: 三条车道怎么跑？
  答：`make verify` / `make smoke` / `make lint`，命令面不变）。
- **Evidence seam:** 测试 ID 集合的逐条对账（基线 255 个已捕获：verify 242 + smoke 13）·
  `make verify` 与 `make smoke` 用例数与退出码 · `make lint` 退出码 ·
  `git diff --stat -- src/` 只含登记面。
- **Not in scope:** 任何产品代码行为改动；新增测试覆盖（本 change 只重组既有测试，不扩面）；
  测试目录的层级重排（`unit/<layer>/` 结构保留）；`_battery.py` 与治理侧测试；把
  `test_entry_composition.py` 之外的更多文件改名（先只做主体明确脱钩的两个，避免大范围
  重命名掩盖对账）。
- **Triggered review policies:** local-context, change-admission
