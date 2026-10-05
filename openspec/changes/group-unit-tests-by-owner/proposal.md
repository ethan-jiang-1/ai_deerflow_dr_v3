# Proposal: Group Unit Tests By Owner

## Why

`tests/unit/` 是 13 个文件的扁平集合，"先测哪里"必须查 tests/README 的完整文件表
才能知道 owner（2026-10-05 计划 Phase 3）。目录层面可见 owner 分组后，选择最小
测试 seam 变成浏览目录即可完成的动作。

## What Changes

- **unit 按 owner 分组**（12 个现有文件迁移，owner 判定沿 tests/README 既有
  owner 表）：
  - `unit/domain/`：test_bundle_domain
  - `unit/engine/`：test_admission_engine
  - `unit/runtime/`：test_bundle_runtime、test_state_read_diagnosis、
    test_admission_runtime、test_run_engine、test_event_stream_replay、
    test_subagent_posture
  - `unit/interaction/`：test_entry_composition、test_entry_surface、
    test_command_surface、test_agent_playbook（计划 §3.4 明示 entry composition
    归 interaction）
  - 每个子目录加 `__init__.py`（unittest 递归发现的包标记）
- **新增 collection guard**（`unit/test_collection_guard.py`）：断言四个 owner
  包标记齐全、`contract/__init__.py` 在场、`integration/` 下**任何位置**无包标记
  （默认门禁隔离不变量）、默认发现的结果不含任何 integration 测试、四个 owner
  命名空间与 contract 均被默认发现覆盖。
- **`parents[N]` 索引随深度 +1**（7 个文件的 `__file__` 相对锚点；contract 不动）。
- **登记与文档同轮**：required-paths（entry-surface 组的
  `unit/test_entry_composition.py` 路径）、quality-register / testing-and-
  evaluation / control-map / research-process / run-bundle 的测试链接、
  tests/README 目录图与 owner 表与命令示例。
- **test ID 变化 = 登记过的前缀变化**：`tests.unit.test_X` →
  `tests.unit.{owner}.test_X`，before/after 全量清单与映射入回执。
- **不变**：contract 单独且继续进 verify；integration 无包标记、smoke 独立收集；
  fixture 样本 / runtime fixture provider / recording tool 三种角色登记不变；
  Makefile 收集语义不变；不声称 fixture 证明真实研究质量。

## Capabilities

### New Capabilities

<!-- none: 测试资产目录重排，无 spec 行为变化 -->

### Modified Capabilities

<!-- none -->

## Impact

- 迁移：12 个 `tests/unit/test_*.py` → 四个 owner 子目录 + 4 个 `__init__.py`；
  新增 1 个 guard 文件。
- 修改：7 个文件的 `parents[]` 索引、`openspec/governance/required-paths.toml`
  （1 条路径）、`docs/quality-register.md`、`docs/testing-and-evaluation.md`、
  `docs/control-map.md`、`docs/research-process.md`、`docs/run-bundle.md`、
  `tests/README.md`。
- 触发 proof lane：**verify**（tests/** 变更）与 **smoke**（tests/integration/**
  变更——仅路径未动但 lane surface 覆盖，同轮执行以证明收集范围）。
- 不触碰：src/、Makefile 收集命令、COMMANDS 语义、contract/integration 文件
  位置、fixtures 内容、`deerflow/` gitlink。

## Change Focus

- **Primary module / causal owner:** `tests/unit/` 的 owner 分组——测试资产的组织语义归测试层，collection guard 与 tests/README 是其 conformance 面。
- **Seam classification:** wiring — 测试文件目录重排与锚点索引修正，不改任何被测行为、断言或收集命令；verify/smoke 全绿 + guard 红绿控制是证据。
- **Question:** 12 个 unit 文件迁入四个 owner 包后，能否在收集命令零变化、contract/integration 隔离不变的前提下，让"先测哪里"在目录层面可见，且新 collection guard 能通过 planted failure 变红？
- **Necessary adjacent/external contracts:** delivery-lanes（answers: lane surfaces 是 tests/** glob，不需要改 registry；verify+smoke 双 lane 触发）；entry-surface（answers: test_entry_composition 登记路径随 owning change 更新）；project-structure manifest（answers: required-paths 路径更新协议）；2026-10-05 计划 Phase 3（answers: 分组方案、guard 要求、"登记过的前缀变化"证据义务）。
- **Evidence seam:** guard 红先行两段——① guard 先写而 owner 包未建时红；② planted `tests/integration/__init__.py` 时红、移除后绿；`make verify` 125 项（含 guard）全绿、`make smoke` 9 项全绿、before/after test ID 清单与前缀映射、全套治理门禁。
- **Not in scope:** contract/integration/fixtures 文件迁移；tests/README 从文件清单升级为验证菜单的完整重写（本 change 只做路径与目录图同步）；测试内容或断言变更；proof-lanes registry 变更。
- **Triggered review policies:** local-context, agent-information-map, authority-and-projections, change-admission

tests/README 是路由不是权威：测试资产的事实源是文件与 Makefile 收集行为；
README 不声称 fixture 证明真实研究质量。
