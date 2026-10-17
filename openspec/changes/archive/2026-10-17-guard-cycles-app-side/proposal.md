# Proposal: guard-cycles-app-side

## Why

上一把加了"同目录内模块级导入不得成环"的守卫（`project_architecture_check/cycles.py`），但**只覆盖
治理侧**（`openspec/governance/`）——因为本会话两处环都出现在那里，且当时刻意不扩大范围（一次放行
一把）。

应用侧（`deep_research_harness/src/deerflow_deep_research/`，49 个模块、分层 `domain ← engine ←
runtime`）有它自己的分层矩阵检查，但**同样没有环检测**。分层规则管的是"谁依赖谁"，不是"有没有
环"——一个 `domain → engine → domain` 的环在分层规则下的表现取决于实现细节，而**环的症状本身是
独立的病**："有时能用、有时 ImportError"。

**取证先行**：我先用现成算法扫了应用侧的**整棵包树**（不是只按目录），49 个模块、**零环**。所以
扩围后真实树仍为绿——先取证再扩，而不是先扩再祈祷。

## What Changes

- **`cycles.py` 泛化为多 scope**：一条 scope = `(module_root, absolute_base)`，两者**可能不同**：
  - 治理侧：`module_root = openspec/governance`，`absolute_base = openspec/governance`
    （该目录在 `sys.path` 上，`from gitio import …` 直接可用）
  - 应用侧：`module_root = deep_research_harness/src/deerflow_deep_research`，
    `absolute_base = deep_research_harness/src`
    （绝对导入形如 `from deerflow_deep_research.domain import bundle`，包根在 `src/`）

  这个差别必须**显式建模**——治理侧的"绝对基准 = 模块根"是巧合（目录恰好也在 `sys.path` 上），
  照搬到应用侧会把 `deerflow_deep_research.domain` 解析成
  `…/deerflow_deep_research/deerflow_deep_research/domain` 而静默漏掉全部绝对导入。
- **应用侧的模块根在绝对基准之内**（包目录 vs `src/`），故只有落在 `module_root` 下的目标才算图内
  节点；越界的解析结果直接忽略（治理侧这一条由"键取不出来"隐含成立，泛化后必须显式）。
- **新增直接测试**：应用侧形态的红/绿用例（绝对导入构成的环必须被抓、跨子包的环必须被抓、
  合法单向依赖必须绿），外加**应用侧真实树无环**的断言。

**不变量**：既有语义一字不改——只算直接位于 `Module.body` 的导入、延迟导入与 `TYPE_CHECKING`
不算边、SCC 而非两两互导、`ContractViolation("import.cycle", …)` 形状 ·
治理侧判定结果不变（既有 9 条用例全过、真实树仍绿）· 七个 checker + closeout gate + 治理套件（230）
全绿 · `--self-test` 契约不变 · harness 面**只读**（不修改任何应用侧代码）。

## Capabilities

### New Capabilities

<!-- none: 守卫扩围，不改任何 requirement 或产品契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`project_architecture_check/cycles.py`（scope 从常量变为 `(module_root, absolute_base)` 对，
  新增应用侧 scope）· `check_code_budgets.py`（该文件上限按实测重测）· 新测试文件。
- **不动**：应用侧任何代码（只读扫描）· `imports.py` 与其余既有规则 · 两个 checker 入口 ·
  `--self-test` · 判定语义。
- **触发车道**：治理套件 · 七个门禁组件（架构 checker 自身是主关卡）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/project_architecture_check/cycles.py` ——
  它拥有"模块图是否成环"这一判定；本 change 把它的**作用域**从治理侧扩到应用侧。
- **Seam classification:** deterministic-guardrail —— 纯静态分析。
- **Question:** 同一条环检测规则能否同时服务两种导入风格（治理侧的"目录在 `sys.path`"与应用侧的
  "包根在 `src/`"）——而既有治理侧判定一字不变、应用侧真实树（先取证：零环）为绿、且两种形态
  各自都能红？
- **Necessary adjacent/external contracts:** `project_architecture_check/facade.py`（answers: 调用点
  不变，只多覆盖一个 scope）· 应用侧的分层矩阵检查（answers: 它管方向、不管环，两者互补不重叠）·
  `check_code_budgets.py`（answers: 该文件变大后上限跟实测值）。
- **Evidence seam:** 应用侧整棵包树的**先期扫描**（49 模块零环）· 应用侧形态的红/绿探针 ·
  治理侧既有 9 条用例与真实树 · 七 checker + closeout · 治理套件 230 → 更多。
- **Not in scope:** 修改任何应用侧代码（若扫描发现环，走 bug 轨报告而非顺手改）· 跨 scope 的环
  （两个 scope 各自成图；跨边界的环由分层规则管）· 任何既有规则语义 · CAS 空转。
- **Triggered review policies:** local-context, change-admission
