# Proposal: Split Runtime Into Bundle and Adapters

## Why

`runtime/` 顶层平铺 12 个模块，操作者无法从目录名区分持久化、宿主适配、装配与
执行职责（2026-10-05 计划 Phase 2）。import graph 勘察证实两个高内聚簇：
持久化六件套（atomic 被 5 个内部模块消费；bundle_state 被 4 个；配有 4 个专属
unit 测试文件）与 DeerFlow binding 四件套（client ← contracts + 懒加载 snapshot；
posture 独立 checker）。同时 `entry.py`（64 行装配 seam）与 `run_engine.py`
（304 行执行 seam）名字已自说明，`fixtures/` 被 config 机器引用
（`deerflow_deep_research.runtime.fixtures:...`）不可轻动。

## What Changes

- **新增 `runtime/bundle/`**（Bundle 持久化簇）：迁入 `atomic.py`、
  `bundle_state.py`、`bundle_actions.py`、`journal.py`、`ledger.py`、
  `admission.py`，配 `__init__.py`（职责 docstring）。簇内相对 import 原样保留；
  仅 `..domain`/`..engine` 变 `...domain`/`...engine`。
- **新增 `runtime/adapters/`**（DeerFlow binding 簇）：迁入 `client.py`、
  `contracts/`（整目录）、`snapshot_middleware.py`、`subagent_posture.py`，配
  `__init__.py`。client 对 contracts/snapshot 的相对 import 原样保留。
- **保留在 runtime 顶层**：`entry.py`（装配 seam）、`run_engine.py`（执行
  seam）、`interaction/`、`fixtures/`——计划明示允许保留命名 seam；单文件目录
  的收益不抵 churn，且 fixtures 挪动会强制 config 路径 cutover。
- **外部消费者 import 直接 cutover（无兼容 shim）**：`run_engine.py`、
  `entry.py`、`interaction/cli.py`（含函数级懒 import 两处）、9 个 unit 测试
  文件、1 个 contract 测试、1 个 integration 测试、`tools/record_stream.py`。
- **登记与文档同轮更新**：`required-paths.toml`（deerflow-wiring 组的
  client/snapshot/contracts 路径、repo-skeleton 增两个 `__init__.py`）、
  `runtime/__init__.py` docstring、`control-map.md` §4/§7 与
  `research-process.md` 的模块链接。
- **不变**：四层 ownership 与 import 方向、CLI 与 Bundle schema、测试文件位置
  与 test ID、config provider 路径、`domain/`、`engine/`、任何 spec 行为。

## Capabilities

### New Capabilities

<!-- none: 包内结构移动，无 spec 行为变化 -->

### Modified Capabilities

<!-- none -->

## Impact

- 迁移：`src/deerflow_deep_research/runtime/{atomic,bundle_state,bundle_actions,journal,ledger,admission}.py`
  → `runtime/bundle/`；`runtime/{client,snapshot_middleware,subagent_posture}.py`
  与 `runtime/contracts/` → `runtime/adapters/`。
- import 更新：`runtime/run_engine.py`、`runtime/entry.py`、
  `runtime/interaction/cli.py`、`tests/unit/` 9 文件、
  `tests/contract/test_wiring_mirror.py`、`tests/integration/test_wiring_smoke.py`、
  `tools/record_stream.py`。
- 登记/文档：`openspec/governance/required-paths.toml`、
  `runtime/__init__.py`、`docs/control-map.md`、`docs/research-process.md`。
- 触发 proof lane：**verify**（src/** 变更）与 **smoke**（cli.py/entry.py/
  interaction/** 变更）都必须执行；迁移前 test ID 清单已捕获（125 项）作
  before/after 对照。
- 不触碰：`deerflow/` gitlink、config/、domain/、engine/、tests 文件位置。

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/` 的包组织——持久化与宿主适配两个内聚簇的物理归属；import/registry/doc 更新是其 conformance 面。
- **Seam classification:** wiring — 包内文件重排与 import cutover，不改认知、状态规则、准入语义或任何可观察行为（基线 125 unit + 9 smoke 全绿，迁移后必须原样全绿）。
- **Question:** 以 import graph 证实的两个内聚簇迁入命名子包后，能否在零 test ID 变化、零行为变化、config 路径不动的前提下，让 runtime 目录从名字直接区分 interaction、assembly（entry.py）、execution（run_engine.py）、persistence（bundle/）、adapters（adapters/）、fixtures？
- **Necessary adjacent/external contracts:** project-structure manifest（answers: 四层 ownership 与 import 方向不变，required-paths 增删按登记协议）；deerflow-wiring（answers: client/contracts/snapshot 的绑定行为与接口不变，仅路径变）；delivery-lanes（answers: src/** 与 interaction/** 触发 verify+smoke 双 lane）；2026-10-05 计划 Phase 2（answers: 迁移原则——两个以上消费者或独立测试 seam 才建目录、直接 cutover 不留 shim）。
- **Evidence seam:** 迁移中途 ImportError 红证（证明测试 seam 咬合结构变更）→ 修复后 `make verify` 125 项全绿；`make smoke` 9 项全绿；before/after test ID 清单逐项相同；architecture/doc-hygiene/closeout 全绿；回执记录全部直测退出码。
- **Not in scope:** tests/ 目录重排（Phase 3）；`entry.py`/`run_engine.py` 改名或并入子包（计划允许保留命名 seam）；config provider 路径迁移；任何行为/语义变更。
- **Triggered review policies:** local-context, agent-information-map, authority-and-projections, change-admission

模块 docstring 只描述 interface 与职责，不把地图写成第二权威；`domain/bundle.py`
仍是 Bundle 路径合同唯一权威，`engine/` 仍是确定性裁决 owner。
