# Proposal: split-governance-checkers

## Why

阶段 1（`extract-doc-hygiene-test-battery`）把负例电池搬出产品模块后，治理检查器的体量分布
变得很不均匀：`openspec/governance/` 共 6,016 行、13 个文件，其中两个文件占了 **2,497 行**
（`check_change_guidance.py` 1,473、`check_project_architecture.py` 1,024），而其余 11 个
文件平均约 320 行。最大的两个文件里又各有一个「三段揉一起」的巨型函数
（`load_manifest` 269 行 = TOML 解析 + 契约校验 + 对象构造；
`_validate_change_guidance_tree` 137 行）。

这是"定位成本"问题，不是"风格"问题：想改 arch checker 里"忽略路径"那一条规则，得先在
1,024 行里分清哪段是 manifest 解析、哪段是校验、哪段是渲染；想查"某条 review policy 在
哪被校验"，得在 1,473 行里翻找三处并行的 if 块。**改一处要先读懂一千行**，正是本卡
（CLS-025）要收敛的债。

现在做，是因为阶段 1 已经把"规则 = `check(scope)` 纯函数 + 注册表"这层接缝建好，拆分
不再需要同时改语义；且这一步是阶段 3（去重收敛 + 体积守卫）的前置——没有子包结构，
共享工具没有落点。**本 change 只搬不改：零语义变化。**

## What Changes

- **`check_change_guidance.py` 拆为「薄入口 + 子包」**：入口保留文件名与 CLI（`main`），
  规则实现移入 `openspec/governance/change_guidance_check/`，按职责分模块
  （guidance 树/产品上下文、Focus 卡与提案、预算与信息地图、policy 注册表、审查表校验 ×3）。
  入口**继续 re-export** 现有测试直接 import 的符号（`ContractViolation`、
  `_validate_change_tasks` 等）。
- **`check_project_architecture.py` 拆为「薄入口 + 子包」**：规则实现移入
  `openspec/governance/project_architecture_check/`（manifest 装载、guide 生成块、required-paths
  与忽略路径、导入矩阵、上游 gitlink），入口保留文件名、CLI、以及 `test_split_manifest.py`
  经 `importlib` 使用的公共名。
- **`load_manifest` 269 行拆为三段**：`_parse_manifest_document`（TOML → 原始字典）、
  `_validate_manifest_contract`（契约与封闭集合校验）、`_build_manifest`（构造冻结对象）。
- **`check_doc_hygiene.py` 只做函数级分解**：把 182 行的 `_rule_ledger_consistency`
  拆成命名的子规则函数（名册/索引、计数与 Next-ID、声明一致性、行放置、户口与居住），
  **不做包级拆分**（该文件已降至 864 行、仅此一个超长函数；再拆包会给
  `_battery.py` 与 `RULES` 注册表引入循环 import 风险，收益为负）。
- **登记同步**：`required-paths.toml` 增补新子包与其模块；`architecture-policy.md` 的
  Import Matrix Authority 段落补一句"治理脚本自身的内部结构不在该矩阵管辖内"的现状说明
  （该矩阵只遍历 harness 源码根）。
- **文档同步**：`openspec/governance/README.md` 的组件表补"实现位于子包、入口为薄壳"一句。

**不变量（本 change 的验收核心）**：每个 checker 的 CLI 文本与退出码逐字不变；
违规文本逐字不变；CI/hook 的命令字符串与文件路径不变；`test_project_gate.py` 的临时树
夹具（按路径复制组件脚本与 kernel）继续工作；`change_guidance_kernel.py` **保持顶层文件名
与位置**（测试夹具按该路径复制它）。

## Capabilities

### New Capabilities

<!-- none: 治理 checker 的内部结构不被任何 capability 的 requirement 管辖；本 change
     不改变任何可观察行为，也不新增契约面。不为凑 validates 发明需求。 -->

### Modified Capabilities

<!-- none: 同上。checker 的职责与输出均不变，只有实现文件的组织方式改变。 -->

## Impact

- **改**：`openspec/governance/check_change_guidance.py`（1,473 → 薄入口）、
  `openspec/governance/check_project_architecture.py`（1,024 → 薄入口）、
  `openspec/governance/check_doc_hygiene.py`（内部函数分解）。
- **新增**：`openspec/governance/change_guidance_check/`（子包）、
  `openspec/governance/project_architecture_check/`（子包）。
- **登记**：`openspec/governance/required-paths.toml`（子包目录 + 模块文件）。
- **文档**：`openspec/governance/README.md`、`openspec/governance/architecture-policy.md`。
- **不动**：`change_guidance_kernel.py`（文件名与位置保持，测试夹具依赖）、
  `_battery.py`、`check_doc_hygiene.py` 的文件级结构、其余 9 个 checker、
  `.github/workflows/governance.yml`、`.githooks/pre-commit`、
  `deep_research_harness/`（零改动）、`deerflow/` gitlink。
- **触发车道**：治理 unittest 套件（145 用例）与 `check_project_gate.py --phase closeout`；
  harness 的 `make verify` / `make smoke` 不受影响（本 change 不含 harness 文件）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/` —— 治理检查器目录自身；
  它拥有"规则代码放在哪、入口暴露什么"这个决定。
- **Seam classification:** deterministic-guardrail —— 纯机械判定引擎的内部重组；
  无模型参与，判定语义零变化。
- **Question:** 两个千行级 checker 能否拆成「薄入口 + 职责子包」而让 CLI 文本、退出码、
  违规文本、测试夹具可达性全部逐字不变——即使测试会把组件脚本复制到临时树里独立执行？
- **Necessary adjacent/external contracts:** `openspec/tests/governance/test_project_gate.py`
  （answers: 临时树夹具按路径复制组件脚本与 kernel 的假设是否被破坏？答：入口文件名与
  kernel 位置均不变，故夹具继续工作）；`openspec/tests/governance/test_split_manifest.py`
  （answers: 经 importlib 使用的公共名是否仍需在入口可用？答：需要，入口 re-export）；
  `openspec/tests/governance/test_change_authority.py`（answers: 直接 import 的
  `ContractViolation` 与 `_validate_change_tasks` 是否仍可达？答：入口 re-export）；
  `.github/workflows/governance.yml` 与 `.githooks/pre-commit`（answers: 精确路径与退出码
  契约是否保持？答：不变，故零改动）；`openspec/governance/required-paths.toml`
  （answers: 新子包如何登记？答：`directories` 与 `files` 各增条目，过架构 checker）。
- **Evidence seam:** 六条门禁退出码直测 + 每个 checker 的 stdout 改造前后逐字比对 +
  治理套件用例数不减（基线 145）+ 变异探针（临时移走子包某模块，入口必须红而非静默降级）。
- **Not in scope:** 去重收敛（6 份 git 包装、5 套 path 解析、3 种 finding 形状）与死码清偿
  （kernel 的 ~157 行未用导出）——属阶段 3 的 `establish-code-budgets`，与本 change 的
  "只搬不改"边界冲突；任何规则的语义修改；`check_doc_hygiene.py` 的包级拆分；
  `_battery.py` 的拆分；harness 侧任何改动。
- **Triggered review policies:** local-context, change-admission
