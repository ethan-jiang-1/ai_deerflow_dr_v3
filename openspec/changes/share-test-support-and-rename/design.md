# Design

## Context

动机见 `proposal.md` — Why。这里只记塑造形态的实测事实与约束。

**测试面现状（实测）**

| 事实 | 数字 |
|---|---|
| 测试树规模 | 41 文件 / 5,335 行 / 281 个 `test_` 方法 |
| verify 面测试 ID | 242（`make verify` 报告 Ran 251——差值是参数化与类级 setup 的计数口径） |
| smoke 面测试 ID | 13（整棵 integration 跑出 30 个用例） |
| 最大测试文件 | `unit/runtime/test_run_engine.py` 674 行 / 31 测试 / 1 个类 |
| 重复夹具 | `TemporaryDirectory()` 37 · `bundle_actions.start(` 18 · 固定时钟常量 17 · `_PIN` 7 · `_event` 2 |
| 既有共享资产 | 只有 `tests/fixture_reports.py`（25 行） |

**四条硬约束**

1. **测试 ID 集合是契约**：基线 255 个 ID 已捕获（`/tmp/phase5-before/verify-test-ids.txt`
   与 `smoke-test-ids.txt`）。改造后逐条对账，改名者给出新旧映射。少了 = 覆盖丢失，
   多了 = 夹带了新测试（本 change 不扩面）。
2. **发现合同不能破**：`tests/integration` 故意没有 `__init__.py`（默认门禁不得导入它）；
   `unit/<layer>/` 与 `contract/` 有包标记。`test_collection_guard` 锁这五条，负例只能加强
   证明力、不能改它们。
3. **三条车道**：`make verify` / `make smoke` / `make lint`——阶段 4 的教训（漏跑 lint 由
   远端 CI 抓出 33 项）。
4. **产品面零行为改动**：`src/` 只允许 `required-paths.toml` 的登记条目变化。

## Goals / Non-Goals

**Goals:**

1. 一份 `tests/support.py` 承载五类共享夹具；重复常量与脚手架各一份。
2. `test_run_engine.py` 674 → 四个按行为族命名的文件；测试与主体同名（pump）。
3. `test_collection_guard` 有已知违规负例，且该负例真的会让守卫关心的事发生。
4. 255 个测试 ID 逐条对账不变；三条车道全绿。

**Non-Goals:**

- 不新增测试覆盖（只重组）；不改产品代码行为；不重排测试目录层级；
  不做大范围改名（只做主体明确脱钩的两个：run_engine → pump、entry_composition → assembly）。

## Decisions

### D-1｜`tests/support.py` 是普通模块，不是包

- **选**：`tests/support.py`（`tests/` 已是包），提供 `make_run_bundle(...)`、时钟与 pin 常量、
  事件构造器、`read_journal(handle)`。
- **代价**：一个共享模块的导入面。
- **换来**：18 处 `bundle_actions.start(` 与 37 处 `TemporaryDirectory()` 收敛为一次调用；
  改夹具形态只动一处。
- 备选：`tests/unit/support.py`——否决：`contract/` 也要用（它驱动真实 CLI 子进程）。

### D-2｜拆分按行为族，不按类

- **选**：`test_pump.py`（入口与终态基线）、`test_pump_clarification.py`、
  `test_pump_plan_gate.py`、`test_pump_terminal.py`。
- **代价**：跨文件的共享 fixture 要经 `support.py`。
- **换来**：每个文件一个主题；失败时文件名即线索。
- 备选：按原类拆（1 个类 → 4 个类，仍一个文件）——否决：674 行的问题不是类数量。

### D-3｜改名的对账方式：新旧映射逐条列出

- **选**：改名产生的 ID 差异用一张映射表在 `tasks.md` 的收口项里逐条对账（`old → new`），
  而不是"看起来没少"。
- **代价**：机械劳动。
- **换来**：改名与丢失被区分开——只有映射表覆盖的差异才被接受。
- 备选：只比数量——否决：数量相同可以掩盖"丢一个、多一个"。

### D-4｜guard 负例用同一套发现机制证明"泄漏真的会发生"

- **选**：负例在临时树里造一个"integration 带 `__init__.py`"的已知违规，用
  `unittest.defaultTestLoader.discover` 对**该临时树**做一次发现，断言 integration 的 ID
  确实泄漏进来。这样证明的是守卫关心的因果（标记 → 泄漏），而不是重写一遍守卫逻辑。
- **代价**：一次真实的发现调用。
- **换来**：负例与守卫同源（都依赖发现机制），不会各自漂移。
- 备选：断言"某文件存在即红"——否决：那是复述守卫的实现，不是证明失败可发生。

### D-5｜登记与文档同步的范围

- **选**：`required-paths.toml` 增 `tests/support.py` 与新测试文件名、删旧名；
  `tests/README.md` 的资产表按新结构重排。
- **代价**：两处文档改动。
- **换来**：架构 checker 与文档卫生门禁保持绿；`tests/README.md` 继续是可靠路由。

## Alternatives

- **A-1 建 `tests/helpers/` 包**：本 change 的规模不需要一个包；单模块更易读。否。
- **A-2 把 41 个测试文件全部改为与主体同名**：改名面越大，对账越难、review 成本越高，
  而收益（找测试快）只在"名字明显脱钩"的文件上兑现。先做两个。否。
- **A-3 借机补测试覆盖（例如给 pump 的新步骤补单测）**：那会改变测试 ID 集合，与本 change
  的对账不变量冲突；扩面属另一件事。否。
- **A-4 用 pytest 重写**：本仓测试栈是 stdlib unittest，`make verify` / `make smoke` 与治理
  套件都基于它。否。

## Risks / Trade-offs

- [拆分时丢测试或重复测试] → 255 个 ID 逐条对账；改名走映射表；数量相同不算证据。
- [`support.py` 的夹具与原内联夹具行为不完全一致（例如缺一次 `addCleanup`）] → 夹具集中后
  由 251 + 30 个用例集体验证；任何行为差异都会让某个用例红。
- [guard 负例在临时树上跑发现，可能与真实树行为不同] → 负例断言的是"标记 → 泄漏"这条因果，
  在临时树上同样成立；正向五条检查仍对真实树断言。
- [改名让 `required-paths.toml` 与文档暂时漂移] → 同一步内完成登记与 README 同步，并跑
  架构 checker 与 doc-hygiene。
- [漏跑某条车道] → 三条车道写进收口任务；阶段 4 的教训已在 CLS-025 卡上。

## Migration Plan

按 4 步推进，每步以"三条车道绿 + ID 对账不变"为提交边界。

1. `tests/support.py` + 各文件改 import（夹具行为不变；ID 集合必须逐条不变）。
2. `test_run_engine.py` 拆四个文件 + 改名为 `test_pump.py` 族（映射表对账）。
3. `test_entry_composition.py` → `test_assembly.py`；`test_collection_guard` 补负例。
4. 登记与文档同步；三条车道 + 全量 ID 对账；`git diff --stat -- src/` 检查。

**回滚**：测试面改动无运行时残留；回滚 = 撤销该步 diff（含登记与文档）。
