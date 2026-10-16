# Proposal: guard-import-cycles

## Why

本会话连续两把各**手工**断掉一处顶层导入环：

| 环 | 症状 | 怎么发现的 |
|---|---|---|
| `check_doc_hygiene.py` ↔ `_battery.py` | 入口与电池顶层互相 import，靠定义顺序的巧合"能用" | 拆分前的侦察 |
| `doc_hygiene_battery/fixtures.py` ↔ `registry.py` | 抽取器按语法归属放错常量，导入即 `ImportError` | 拆分当场炸出来 |

两处都消除了，**但没有任何 checker 会阻止第三处出现**。这类环的症状是最难查的一种——"有时能用、
有时 ImportError"（取决于谁先被导入），而且它能在测试全绿的情况下潜伏（只要没有人从"错误的那侧"
先导入）。仓库已有分层方向的导入检查（`imports.py`），但**没有环检测**。

## What Changes

- **新增 `project_architecture_check/cycles.py`**：一条规则——**同一模块目录内，模块级导入不得成环**。
  - 图：目录树里的每个模块是节点；边来自**模块级**（直接位于 `Module.body`）的导入。
  - **函数/类内以及 `if TYPE_CHECKING:` 内的导入不算**——延迟导入正是本仓断环的既定手法
    （`cli._self_test` 内导入 `_battery`、`turn.py` 的 `TYPE_CHECKING` 块）。
  - 相对导入（`from .fixtures import x`）与同目录绝对导入（`from gitio import run_git`、
    `from doc_hygiene_check import X`）都解析到具体模块文件；包名解析到其 `__init__.py`。
  - 检测用**强连通分量**（不是只查两两互导）：三模块环也要抓。
- **接进既有流水线**：`facade.validate_project()` 追加一步，且 `--imports-only` 也包含它（它本就是
  导入契约）。违规以既有形状报告：`ContractViolation("import.cycle", …)` ⇒ `ERROR [import.cycle] …`。
- **范围**：`openspec/governance/` 目录树（含两个新包）。扩到 harness 侧是 follow-up——那里的
  分层矩阵已存在，但环检测同样缺失，只是本把不扩大范围。
- **体积表按实测重测**（新模块入表）· `required-paths.toml` 登记。

**不变量**：既有 checker 的判定语义**只增不改**（新规则是新的一步，不动任何现有规则）·
七个 checker + closeout gate + 治理套件（221，含 43 条电池控制）全绿 ·
`--self-test` 契约不变 · harness 面零改动 · **真实树上必须绿**（本会话两把已把环清零）。

## Capabilities

### New Capabilities

<!-- none: 加的是架构守卫的一步，不改任何 requirement 或产品契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **新增**：`openspec/governance/project_architecture_check/cycles.py` · 该规则的直接测试
  （治理套件内，含临时树里的两模块环与三模块环）。
- **改**：`project_architecture_check/facade.py`（追加一步）· `check_code_budgets.py`（新模块入表）·
  `required-paths.toml`（登记）。
- **不动**：`imports.py` 与其余既有规则 · 两个 checker 入口 · `--self-test` · 任何被检查的代码。
- **触发车道**：治理套件 · 七个门禁组件（架构 checker 自身是本 change 的主要关卡）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/project_architecture_check/cycles.py` ——
  它拥有"模块图是否成环"这一判定；此前该判定**不存在**。
- **Seam classification:** deterministic-guardrail —— 纯静态分析，无模型参与。
- **Question:** 一条"同目录内模块级导入不得成环"的守卫，能否在真实树上绿、而**在临时树里种下的
  两模块环与三模块环上都能红**——且不误报本仓既有的合法形态（facade 再导出、包 `__init__`
  对子模块的依赖、`TYPE_CHECKING` 与函数内延迟导入）？
- **Necessary adjacent/external contracts:** `project_architecture_check/facade.py`（answers: 检查的
  编排与 `imports_only` 分支）· `contract.py` 的 `ContractViolation`（answers: 违规的报告形状与
  退出码）· 两个新包（answers: 相对导入与包 `__init__` 的解析形态）· `check_code_budgets.py`
  （answers: 新模块入表）。
- **Evidence seam:** 真实树绿 · 临时树里两模块环与三模块环各自被报出（**能变红**）·
  合法形态不误报（facade 再导出、`TYPE_CHECKING`、函数内延迟导入）· 七 checker + closeout ·
  治理套件 221 · 体积闸。
- **Not in scope:** 扩到 harness 侧 · 环的自动修复 · 检测"跨目录"的环（分层方向已由既有规则管）·
  任何现有规则的语义 · CAS 空转。
- **Triggered review policies:** local-context, change-admission
