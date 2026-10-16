# Proposal: split-doc-hygiene-module

## Why

`openspec/governance/check_doc_hygiene.py` 是 **901 行、顶在体积闸上限**的单文件：22 个顶层函数、
1 个类（`Scope`）、16 个声明、39 个公共名，最大的 `_ledger_roster_problems` 69 行。上限顶格意味着
**对它的任何改动都被闸挡住**——本会话已经为它抬过两次棘轮（895 → 901）。

更关键的是它的**结构病**：`check_doc_hygiene.py` 与 `_battery.py` 在**顶层互相 import**：

```
_battery   ← check_doc_hygiene: 10 个声明常量 + Scope + RULES + violations
check_doc_hygiene ← _battery:   顶层 import（供 --self-test 与可导入面）
```

这个环现在"能用"只是因为**定义顺序恰好**让回环导入取到了已初始化的名字——它是一颗定时炸弹
（阶段 1 的记录里就写着这是当时**刻意避开包化**的原因："避免与 `_battery.py` ↔ `RULES` 的循环
导入陷阱"）。**把声明与规则挪进双方都导入的包，环就消失了**——这才是本次拆分的真正收益。

## What Changes

- **`check_doc_hygiene.py` 变薄入口**（文件名不变——CI、pre-commit 与 `required-paths.toml`
  按精确路径引用它），实现移入 `openspec/governance/doc_hygiene_check/`：
  `constants.py`（16 个声明：路径表、预算表、标记表、正则）、`scope.py`（`Scope`）、
  `rules.py`（`RULES` + 各 `_rule_*` + `violations`）、`ledger.py`（账本/计数/户口/放置类判定）、
  `cli.py`（`main` 与 `--self-test`）、`__init__.py`（整面门面）。
- **环被打破**：`_battery.py` 改为从 `doc_hygiene_check` 取那 12 个名字（而不是从入口文件取），
  入口与电池都单向依赖包。
- **入口保持公共面**：显式再导出 + `__getattr__` 兜底，使既有调用方式（`import check_doc_hygiene`
  后取 `RULES` / `Scope` / `run_rule` / `violations` 等）逐字不变。
- **体积表按实测重测**：入口变小、6 个新模块入表。

**不变量（本 change 的验收核心）**：
1. **命令行契约逐字不变**——`--self-test` 的 stdout 行、违规消息文本、退出码 0/1。
2. **43 条电池控制全部保持成立**（`failing_controls()` 为空），清单 pin **31/12/43 不变**。
3. **公共面零缺失**（39 个公共名逐一可达）。
4. 治理套件用例数不减（221），七个 checker + closeout gate 全绿。
5. harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 实现位置与依赖方向的整理，不改任何 requirement、规则或契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`check_doc_hygiene.py`（901 行 → 薄入口）· `_battery.py`（改导入来源；其自身的拆分是
  同一目标的第二把，见下）· `check_code_budgets.py`（入口与 6 个新模块的上限）·
  `required-paths.toml`（包与新模块入册）。
- **新增**：`openspec/governance/doc_hygiene_check/`（6 个模块）。
- **不动**：规则集、消息文本、退出码、`SCHEMA_VERSION`、43 条控制的内容、`deerflow/`、
  `deep_research_harness/`。
- **触发车道**：治理套件（含 43 条控制与清单 pin）· 七个门禁组件（`check_doc_hygiene` 自身也在内）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` —— 它拥有
  "文档层卫生"的全部规则；本 change 只改**实现位置与依赖方向**。
- **Seam classification:** wiring —— 拆分与依赖倒置；判定语义零变化。
- **Question:** 一个 901 行、顶格、且与测试电池**顶层互相 import** 的门禁，能否拆成薄入口 + 包
  ——而命令行契约逐字不变、43 条控制全部成立、39 个公共名零缺失、环被消除？
- **Necessary adjacent/external contracts:** `.github/workflows/governance.yml` 与
  `.githooks/pre-commit`（answers: 按精确路径调用 `check_doc_hygiene.py`，故入口名不可变）·
  `openspec/tests/governance/test_doc_hygiene.py`（answers: 清单 pin 31/12/43 与 CLI 契约测试，
  它们不改，是本 change 的判据）· `_battery.py`（answers: 其导入来源必须改向包，否则环仍在）·
  `required-paths.toml`（answers: 新模块须入册，否则 `path.missing`）。
- **Evidence seam:** `--self-test` 输出与退出码的前后逐字对照 · `failing_controls()` 前后为空 ·
  清单 pin 不变 · 39 个公共名逐一可达 · 治理套件（221）· 七个 checker + closeout gate。
- **Not in scope:** `_battery.py` 自身的拆分（724 行，同一目标的**第二把**，本 change 只改它的
  导入来源）· 任何规则语义 · `Scope` 冻结值对象的重构 · CAS 空转。
- **Triggered review policies:** local-context, change-admission
