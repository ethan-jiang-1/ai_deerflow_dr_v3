# Proposal: Establish Operator Control Map

## Why

四份文档同时部分声称"总图"角色：`repository-map.md`（72 行，目录+owner 路由）、
`runtime-map.md`（336 行，运行/发布/质量三关注点混载）、`runtime-architecture.md`
（21 行，边界摘要）、`research-process.md`（95 行，认知过程）。操作者核心问题——
从哪启动、谁驱动 agent loop、skill 是否实际加载、Bundle 状态在哪、想改行为先测
哪里——的答案分散、重复且无唯一入口。这是 2026-10-05 架构计划 Phase 1 的明确
要求：先建立唯一控制地图，再做任何物理迁移。

## What Changes

- **新增 `docs/control-map.md`**：唯一控制总图——问题到报告主链、**两种 loop 的
  图示与职责表**（DeerFlow 宿主 agent loop vs Harness run loop，本 change 核心新增）、
  三层职责与目录、六动词真实语义与易误解动作、配置两梯、"改什么→找哪个
  owner→先测哪里"路由表（合并 repository-map 与 runtime-map §7 两张表）、权威
  边界（吸收 runtime-architecture）、发布形态与**未实现清单**（skill 不强制、
  refine 不自动重跑、无 worker/多用户/认证/备份、真实质量无自动评估）、最小
  车道选择。
- **新增 `docs/run-bundle.md`**：Run Bundle 持久化合同与 artifact 权属表——
  每个对象谁写、是什么、能看出什么、不能推出什么；生命周期与状态权威
  （revision CAS/lease）；"终态 ≠ 交付 ≠ 质量"展开。
- **删除 `repository-map.md`、`runtime-map.md`、`runtime-architecture.md`**：内容
  归并（映射表见 design）；质量车道表与冷启动 lane 并入
  `testing-and-evaluation.md`；不留降级指针文件（会复活第二总图）。
- **`research-process.md` 定点补强**：skill **三列状态表**（声明可用/运行中实际
  加载证据/质量评估）；Bundle 对象观察表去重改指 run-bundle.md。
- **路由面同步**：docs 索引、应用 README Reading Map、AGENTS Information Map
  （净负编辑并**下调预算棘轮**至实测值）、根 README、change-guidance local
  policy 的 Reader Roles 行。
- **治理声明表同步**：`check_doc_hygiene.py`（DOC_LAYER_DOCS/STALE_MARKER_FILES/
  自测 fixture 名/AGENTS 预算棘轮）、`check_change_guidance.py`
  （FOCUSED_DOC_PATHS 与 policy anchors：runtime-architecture → control-map）、
  `required-paths.toml`、`test_project_gate.py` fixture 源。
- **无 spec 行为变化**（`skip_specs: true`）、无运行时代码变化、无命令语义变化。

## Capabilities

### New Capabilities

<!-- none: doc-layer consolidation; declaring-table edits only -->

### Modified Capabilities

<!-- none -->

## Impact

- 新增：`deep_research_harness/docs/control-map.md`、`docs/run-bundle.md`。
- 删除：`docs/repository-map.md`、`docs/runtime-map.md`、`docs/runtime-architecture.md`。
- 修改：`docs/research-process.md`、`docs/testing-and-evaluation.md`、
  `docs/README.md`、应用 `README.md`、`AGENTS.md`（Information Map 净负 +
  DOC_BUDGETS 棘轮下调）、根 `README.md`、
  `openspec/change-guidance/local/deep-research.md`、
  `openspec/governance/check_doc_hygiene.py`、
  `openspec/governance/check_change_guidance.py`、
  `openspec/governance/required-paths.toml`、
  `openspec/tests/governance/test_project_gate.py`。
- 不触碰：运行时 `src/` 与 `tests/` 代码、`COMMANDS.md` 语义、playbook、
  capability specs、`deerflow/` gitlink（只读，本 change 不读其内部）。
- 普通下游工作不修改、不深读 `deerflow/` gitlink；本 change 不涉及该边界。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/docs/` 声明层——控制问题的路由语义归文档层，机器注册表（doc-hygiene / change-guidance / manifest）是其 conformance 面。
- **Seam classification:** wiring — 信息面路由重组与内容归并，不改认知、状态规则、准入或任何运行时行为。
- **Question:** 新 Agent 只读应用 README + control-map + tests/README，能否定位 create 入口、两种 loop 的分界、skill 实际加载证据、Bundle artifact 与最小测试 seam，且链接全通、没有第二套业务规则？
- **Necessary adjacent/external contracts:** `doc-truthfulness`（answers: markers/ledger 规则不变，声明表编辑保持可见——新文档不得含 stale markers）；`entry-surface`（answers: 六动词语义在 control-map 中原样引用不得重定义）；project-structure manifest（answers: required-paths 增删的登记协议）；2026-10-05 架构计划 Phase 1（answers: 验收判据——三跳内找到稳定启动命令、两种 loop 可分辨、链接检查通过）。
- **Evidence seam:** `check_doc_hygiene.py`（含 `--self-test`）红先行（新文档未注册时必须红）、change-guidance focused-doc 链、architecture checker、`make verify`、根/应用 README 路由逐条人工核对、`git diff --check`；回执记录全部直测退出码。
- **Not in scope:** 运行时与测试目录的物理迁移（计划 Phase 2/3）；tests/README 重写（Phase 3）；skill 强制加载、refine 自动重跑、worker/服务化等产品语义；COMMANDS 命令语义变化；spec 行为变化。
- **Triggered review policies:** local-context, agent-information-map, authority-and-projections, change-admission

地图是投影不是权威：control-map 只路由到 owning code/spec/test，不复制
state/checkpoint/ledger 事实成第二事实源；"当前未实现"清单必须显式成文而非暗示。
