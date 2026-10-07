# Design

## Context

- 探针实证（本 goal 前轮）：smoke 期间框架把 `.retrieval/memory-fts5.sqlite3(+shm/wal)`
  写进了 `DEER_FLOW_HOME` override 目录——公开缝在嵌入式绑定下有效。初判"未验证"是探针
  `ls` 漏看隐藏目录，已在 D 项提交前修正并清除误提交二进制。
- 现状：应用不设 `DEER_FLOW_HOME`，框架落在 checkout 相对默认位；本仓库的实际落点是
  `deep_research_harness/.deer-flow/`（1MB：`skills_view/public/` 上游 skill 投影 +
  `users/default/` 用户记忆 memory.json + agents facts）。
- `build_client` 已有先例：框架 import 前设 `DEER_FLOW_CONFIG_PATH` 钉配置解析——home pin
  是同一模式在目录维度的应用。
- manifest `[ignored_paths]` 声明 app `.gitignore` 的 `.deer-flow/` 条目；仓库根 `runs/`
  忽略是既有前例。

## Goals / Non-Goals

**Goals:**

- 框架运行态永远落在仓库根 `.deer-flow/`（应用子树外），pin 在框架 import 前生效。
- 历史残留一次性完整搬迁（含用户记忆），零内容损失。
- guard 把"pin 存在 + 子树外"钉进 contract 车道。

**Non-Goals:**

- 不读/不清/不脱敏 memory 内容；不动 skill 激活语义（B 项）；不改框架 home 内部结构；
  不做备份/多租户。

## Decisions

1. **pin 位置 = `assembly.pin_framework_home()`**：assembly 拥有 checkout 位置常量
   （HARNESS_ROOT/REPO_ROOT），home 解析与边界检查（不在 HARNESS_ROOT 内，否则
   SystemExit）都在这里；`run_foreground` 在 `build_client` 前调用。client.py 不动——
   它只管框架构造参数，目录策略归 assembly（与 `DEEP_RESEARCH_RUNS_ROOT` 解析同层）。
2. **固定仓库根 `.deer-flow/`**：沿用框架自己的目录命名（迁移后框架幂等投影可直接
   对上签名），gitignore 与 `runs/` 同款。不做 env 覆盖（无需求；测试直接调 pin 函数）。
3. **guard 三断言**：(a) `pin_framework_home()` 返回路径 == 仓库根 `.deer-flow/` 且设了
   env；(b) 解析路径不在 HARNESS_ROOT 内；(c) AST：`run_foreground` 函数体在
   `build_client` 调用前出现 `pin_framework_home` 调用（顺序是行为合同——pin 必须先于
   框架 import）。
4. **搬迁用 `mv` 一次完成**：目录整体搬，`users/` 记忆原样；搬完应用子树内不再有
   `.deer-flow`。app `.gitignore` 移除该条目 + manifest `[ignored_paths]` 同步移除；
   仓库根 `.gitignore` 增 `.deer-flow/`。
5. **smoke 实证写入落点**：apply 后跑 `make smoke`，检查仓库根 `.deer-flow/.retrieval/`
   出现、应用子树无新 `.deer-flow`——回执记录该观察（这同时是 delta 第三个 scenario
   的 smoke 车道证据）。

## Alternatives

- **C2 并入 B**：被否（用户裁决 C1）——pin 是 B 的前置守卫，先钉住目录策略，B 激活时
  写入落点已被约束；且搬迁与激活是两个证据等级（接线 vs 认知），分开立项各自可审。
- **pin 放 `client.build_client`**：否——client 只管构造参数；`DEER_FLOW_CONFIG_PATH`
  在那里是因为它是构造行为，home 是 checkout 级目录策略，assembly 是位置 owner。
- **允许 env 覆盖 home**：否——无需求；多一个覆盖面多一分漂移可能，YAGNI，B 若需要
  再经 owning change 加。
- **只搬数据不 pin**：否——不 pin 则框架下次仍写回应用子树默认位，搬迁白做。

## Unresolved Questions

- 仓库根 `.deer-flow/` 是否会与未来 deerflow 后端式布局冲突：不存在——本仓库框架是
  embedded 绑定，无 backend/ 目录。
