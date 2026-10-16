# Proposal: split-control-battery

## Why

`openspec/governance/_battery.py` 是 **724 行、顶在体积闸上限**的单文件：57 个函数、1 个类
（`NegativeCase`）、46 个声明（45 个用例 ID + `NEGATIVE_CASES`）、**104 个顶层名**。它是
doc-hygiene 的**正典控制电池**——43 条控制（31 负例 + 12 绿色）都在里面，`--self-test` 也靠它。

上一把（`split-doc-hygiene-module`）把 `check_doc_hygiene.py` 拆成薄入口 + 包，并让电池改从包
导入——**环断了，但电池自身仍是那个 724 行的单文件**。本把拆它，是同一目标的第二半。

## What Changes

- **`_battery.py` 变薄再导出**（文件名不变——`--self-test` 与治理测试按名 import 它），实现移入
  `openspec/governance/doc_hygiene_battery/`：
  - `fixtures.py`（419 行）：56 个 fixture 构造器 + 它们私用的两个片段常量
  - `registry.py`（378 行）：`NegativeCase` · `_c` · 45 个用例 ID · `NEGATIVE_CASES` ·
    `run_rule` / `run_case` / `case_holds` / `failing_controls`
  - `__init__.py`（226 行）：整面门面
- **包内依赖是干净 DAG**：`registry → fixtures`（注册表引用构造器），反向无依赖——这与上一把在
  两个顶层文件之间发现的环形成对比。
- **体积表按实测重测**：`_battery.py` 724 → **118**；3 个新模块各按其实测值入表。
- **登记补齐**：`_battery.py` **此前从未登记**，本次与包目录、3 个模块一并入册。

**不变量**：43 条控制全部成立（`failing_controls()` 为空）· 清单 pin **31/12/43 不变** ·
`--self-test` 输出与退出码逐字不变 · **104 个原始顶层名在 `_battery` 零缺失** ·
治理套件 221 条不增不减 · 七 checker + closeout gate 全绿 · harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 实现位置整理，不改任何控制、夹具、消息或契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`_battery.py`（724 → 118 行薄再导出）· `check_code_budgets.py`（电池上限下调 + 3 个新模块）
  · `required-paths.toml`（`_battery.py` 首次登记 + 包目录 + 3 个模块）。
- **新增**：`openspec/governance/doc_hygiene_battery/`（3 个模块）。
- **不动**：43 条控制的内容与语义 · `NEGATIVE_CASES` 顺序（声明顺序 = CLI 报告顺序 = 测试用例顺序）
  · `--self-test` 契约 · `deerflow/` · `deep_research_harness/`。
- **触发车道**：治理套件（含 43 条控制与清单 pin）· 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/_battery.py` —— 它拥有 doc-hygiene 的
  全部负例控制与夹具；本 change 只改实现位置。
- **Seam classification:** wiring —— 拆分；控制语义零变化。
- **Question:** 一个 724 行、顶格、承载 43 条控制与 104 个顶层名的电池，能否拆成薄再导出 + 包
  ——而控制全部成立、清单 pin 不变、`--self-test` 逐字不变、104 个名零缺失？
- **Necessary adjacent/external contracts:** `doc_hygiene_check/cli.py`（answers: `--self-test`
  按名 `import _battery`，故 `_battery.py` 必须保留且可导入）· `openspec/tests/governance/
  test_doc_hygiene.py`（answers: 逐条控制测试与清单 pin 31/12/43，不改，是判据）·
  `required-paths.toml`（answers: 新模块须入册，否则 `path.missing`）·
  `check_code_budgets.py`（answers: 上限跟实测值，且"最大脚本须在表内"的测试会抓漏）。
- **Evidence seam:** `failing_controls()` 前后为空 · 104 个名可达性 · 清单 pin · `--self-test`
  输出与退出码 · 治理套件 221 · 七 checker + closeout · 登记变红实测。
- **Not in scope:** 新增或修改任何控制 · 重构 `NegativeCase` · 治理模块互导的**自动化守卫**
  （本会话两次手工断环，但没有 checker 防止它再生——见"未执行的检查"）· CAS 空转。
- **Triggered review policies:** local-context, change-admission
