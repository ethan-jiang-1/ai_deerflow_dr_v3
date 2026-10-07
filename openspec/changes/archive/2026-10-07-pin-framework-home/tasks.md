# Tasks

> 红绿纪律：退出码直测。工作目录 `deep_research_harness/`（除标注仓库根）。

## 1. guard 先行（红证）

- [x] 1.1 新增 `tests/contract/test_framework_home.py`：(a) `assembly.pin_framework_home()`
  返回仓库根 `.deer-flow/` 且 env 已设；(b) 解析路径不在 HARNESS_ROOT 内；(c) AST 断言
  `run_foreground` 在 `build_client` 前调用 pin。此时函数不存在 → import 红。记录红输出。

## 2. pin 实现

- [x] 2.1 `assembly.py`：`FRAMEWORK_HOME = REPO_ROOT / ".deer-flow"` 常量 +
  `pin_framework_home()`（设 env、子树内即 SystemExit、返回路径）+ `run_foreground`
  在 `build_client` 前调用。Verify: 1.1 全绿，
  `PYTHONPATH=src python3 -m unittest tests.contract.test_framework_home -v` 退出码 0。
- [x] 2.2 全量 verify：`make verify` 退出码 0（test ID +3，无意外增删）。

## 3. 数据搬迁与登记

- [x] 3.1 搬迁（仓库根）：`mv deep_research_harness/.deer-flow .deer-flow`；核对
  `users/default/memory.json` 与 facts 随迁、`skills_view/.projection-manifest.json` 完整。
- [x] 3.2 忽略登记：仓库根 `.gitignore` 增 `.deer-flow/`；app `.gitignore` 移除该条目；
  manifest `[ignored_paths]` entries 同步移除。Verify（仓库根）:
  `python3 openspec/governance/check_project_architecture.py` 退出码 0，且
  `git status` 不出现 `.deer-flow/` 未跟踪项。

## 4. 实证与收口

- [x] 4.1 smoke 实证：`make smoke` 退出码 0；随后检查仓库根 `.deer-flow/.retrieval/`
  存在（或框架 home 内容被框架刷新）且应用子树内无 `.deer-flow/`。回执记录观察。
- [x] 4.2 文档：control-map §3 目录树与 README 各加一句（框架 home 在仓库根）；
  tests/README 登记 guard 资产。Verify（仓库根）:
  `python3 openspec/governance/check_doc_hygiene.py` 退出码 0。
- [x] 4.3 收口门禁（仓库根）：change-guidance / architecture / project-specs /
  `openspec validate --strict` / closeout gate / `git diff --check` 全部退出码直测 0；
  回执记录 revision 与全部退出码；归档后根 README 计数 ritual 同步。
