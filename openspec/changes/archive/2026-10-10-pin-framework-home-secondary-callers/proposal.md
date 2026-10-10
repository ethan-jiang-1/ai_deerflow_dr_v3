# Proposal: pin-framework-home-secondary-callers

## Why

主干 deerflow-wiring 已批 requirement「The framework home is pinned outside the
application subtree」（2026-10-07-pin-framework-home 归档，2026-10-10 补 sync 进主干
ca82507）：框架运行态只许落在仓库根 `.deer-flow/`。但 pin 只在 `run_foreground`
（create/refine 前台路径）生效——`make smoke` 的直连 `build_client`
（`test_wiring_smoke.py` 两处、`test_complete_graph_replay.py` 一处）与
`make record-stream`（`tools/record_stream.py`）未 pin，框架按 cwd 默认把运行态写进
`deep_research_harness/.deer-flow/`。2026-10-10 实测：该子树第二运行态家有 15 个
thread、0 个能对上仓库 bundle（smoke bundle 在 tempdir），当日上午仍有活写入——
文档宣称"应用子树外"与实际行为相左，且删除后下次 smoke 再生。

## What Changes

- `tests/integration/test_wiring_smoke.py`、`tests/integration/test_complete_graph_replay.py`、
  `tools/record_stream.py` 三处直连 `build_client` 前调用 `pin_framework_home()`
- `tests/contract/test_framework_home.py`（`@impl HOME-001`）新增 AST 断言：上述三个
  文件内每个 `build_client` 调用前必须已 pin——红先绿后
- 文档同步：应用 README 与控制地图中"smoke/record 未 pin、落第二家"的 caveat 改为
  "全入口已 pin"（与实现同轮）
- pin 落地后删除 `deep_research_harness/.deer-flow/`（gitignored 本地状态），并以
  `make smoke` 复跑证明不再再生
- 无 spec delta：本 change 使代码符合已批 requirement，不改任何规范语义

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

（无）

## Impact

- 影响：3 个调用方 + 1 个 contract 测试扩展 + 2 处文档行 + 1 个 gitignored 本地目录删除
- 风险：低——smoke/record 的框架运行态改落仓库根 `.deer-flow/`（gitignored，既有 88
  线程同址）；失败模式 = pin 对子树内解析响亮拒绝（既有语义，非本 change 新增）
- 边界：不改 pin 语义/拒绝行为（owning change 2026-10-07-pin-framework-home 已定）；
  不动 `runs/`、`.uv-cache` 等其他本地盘面

## Change Focus

- **Primary module / causal owner:** 三个直连 client 调用方（smoke ×2 文件 +
  `tools/record_stream.py`）——pin 的接线点；语义 owner 是已批的 deerflow-wiring
  framework-home requirement
- **Seam classification:** wiring — 纯接线事实：既有 pin 函数接到三个漏网调用方，pin 语义零改动
- **Question:** 未走 `run_foreground` 的直连 `build_client` 调用方，能否在不改 pin
  语义的前提下同样钉住框架 home，使应用子树不再出现第二个运行态家？
- **Necessary adjacent/external contracts:** deerflow-wiring「framework home pinned」
  requirement（主干已 sync）；`tests/contract/test_framework_home.py` 的 AST 锁模式
  （复用，不新造机制）
- **Evidence seam:** contract 测试红（AST 断言缺 pin，3 文件全红）→ 接线绿 →
  `rm -rf deep_research_harness/.deer-flow && make smoke` exit 0 且目录不再出现 →
  `make verify` + `make lint` 全绿
- **Not in scope:** pin 语义变更；`check_release_face.py`/`delivery-lanes` 面改动；
  本地盘其他清理；把 pin 改成 Makefile env（见 design 备选否决）
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 直连 client 调用方在 `build_client` 前 pin 框架 home | 无——纯接线事实 | `pin_framework_home()` 调用点 + `test_framework_home.py` AST 断言 | non-bypassable | 框架运行态不落应用子树（deerflow-wiring 已批 requirement）；子树内解析响亮失败 | 复用既有 pin 函数与 contract AST 模式，不新增机制 | contract 红→绿 + smoke 后子树无 `.deer-flow/` + verify/lint 全绿 |
