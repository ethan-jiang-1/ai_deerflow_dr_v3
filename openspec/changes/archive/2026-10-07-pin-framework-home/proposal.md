# Proposal: Pin Framework Home

## Why

框架运行态写进应用子树：`deep_research_harness/.deer-flow/`（1MB，skills_view 投影 +
`users/default/` 用户记忆与 facts）物理上混在产品代码目录里。框架公开缝
`DEER_FLOW_HOME`（文档化 env，默认 `backend/.deer-flow`）**实证有效**：探针 smoke 期间
框架把 `.retrieval/memory-fts5.sqlite3` 写进了 override home。当前应用不设它，框架便把
运行态散布在 checkout 相对路径上；B 项激活 skill 后写入量只会增加。历史残留含用户记忆，
只能搬不能删。

## What Changes

- **binding pin**：`assembly.py` 新增 `FRAMEWORK_HOME = REPO_ROOT / ".deer-flow"` 与
  `pin_framework_home()`（设 `DEER_FLOW_HOME` env 并返回路径）；`run_foreground` 在
  `build_client` 前调用——框架 import 时读到的 home 永远在应用子树外。
- **历史残留搬迁**：`deep_research_harness/.deer-flow/` 整体 `mv` 至仓库根 `.deer-flow/`
  （skills_view 投影幂等可重建；`users/` 用户记忆原样保留）。
- **gitignore**：仓库根 `.gitignore` 增 `.deer-flow/`（与 `runs/` 同款待遇）。
- **guard**：`tests/contract/test_framework_home.py`——pin 后 env 指向应用子树外、
  `run_foreground` 源码在 `build_client` 前调用 pin（AST）、home 解析不落在
  `HARNESS_ROOT` 内。
- **不变**：六动词 + diagnose 语义、Bundle 路径合同、`DEEP_RESEARCH_RUNS_ROOT` 解析、
  config 两梯。`DEER_FLOW_CONFIG_PATH` pin 保持不变。

## Capabilities

### New Capabilities

<!-- none: 落在既有 deerflow-wiring capability -->

### Modified Capabilities

- `deerflow-wiring`: ADDED requirement——框架 home 目录由 binding 显式 pin 到应用子树外
  的固定位置，不得依赖框架的 checkout 相对默认值。

## Impact

- 修改：`runtime/assembly.py`（常量 + pin 函数 + run_foreground 调用）。
- 新增：`tests/contract/test_framework_home.py`。
- 数据搬迁：`deep_research_harness/.deer-flow/` → `.deer-flow/`（仓库根，gitignored）。
- gitignore：仓库根 `.gitignore` 增一行；`deep_research_harness/.gitignore` 的
  `.deer-flow/` 条目与 manifest `[ignored_paths]` 同步移除（应用子树内不再有该目录）。
- 文档：control-map §3 目录树加一行；README 运行态一句话。
- 触发 lane：`make verify`（src+tests）与 `make smoke`（binding 变更）；smoke 后
  实证观察写入落点（回执记录）。
- **边界声明**：不修改、不深读 `deerflow/` gitlink；`DEER_FLOW_HOME` 是框架文档化的
  公开 env。所述行为均为本 change 范围，非现状。

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/assembly.py`
  的框架 home 解析与 pin——运行态目录位置的语义决策（应用子树外、固定仓库根路径）。
- **Seam classification:** wiring — env pin + 数据搬迁 + gitignore；无认知、无状态规则、
  无准入语义。
- **Question:** 框架 home 能否被 binding 显式固定到应用子树外的仓库根位置，使框架运行态
  （memory 检索库、skill 投影、用户数据）永远不落在产品代码目录里，且历史残留一次性
  完整搬迁？
- **Necessary adjacent/external contracts:** deerflow-wiring spec（answers: 绑定面新增
  pin 行为的规范权威）；project-structure manifest（answers: ignored_paths 与 app
  .gitignore 的 `.deer-flow/` 条目同步移除，新增仓库根忽略按 `runs/` 前例）；run-bundle
  路径合同（answers: Bundle 数据仍在 `runs/`，框架 home 与 Run Bundle 数据互不混淆）。
- **Evidence seam:** guard 单测红绿（先红：pin 不存在时 env 未设/路径在子树内）；smoke
  全绿后实证检查写入落点（仓库根 `.deer-flow/.retrieval` 出现、应用子树 `.deer-flow`
  不再出现）；架构/doc checker 全绿。
- **Not in scope:** skill 激活语义（B 项）；memory 内容的读取/清理/脱敏；`.deer-flow`
  内部文件格式；框架 home 的多租户/备份。
- **Triggered review policies:** local-context, change-admission, deerflow-downstream-boundary
