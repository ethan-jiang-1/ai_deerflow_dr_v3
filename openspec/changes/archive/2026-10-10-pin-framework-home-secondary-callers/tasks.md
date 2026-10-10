# Tasks: pin-framework-home-secondary-callers

## 1. 红：AST contract 锁（红先行）

- [x] 1.1 扩展 `tests/contract/test_framework_home.py`：新增测试方法——对
      `tests/integration/test_wiring_smoke.py`、`tests/integration/test_complete_graph_replay.py`、
      `tools/record_stream.py` 三个文件逐一解析 AST，凡函数（含方法）体内出现
      `build_client` 调用，则同函数体内必须存在 AST 序更早的 `pin_framework_home`
      调用；缺者点名文件与函数。Verify: `PYTHONPATH=src python3 -m unittest
      tests.contract.test_framework_home -v` 先红（3 文件 0 pin，断言逐一点名）。
- [x] 1.2 负例控制：临时在任一目标文件末尾追加"pin 在 build_client 之后"的形状跑红
      再还原——证明断言按序而非仅在场。Verify: 红→还原→绿，记录退出码。

## 2. 绿：三处接线

- [x] 2.1 `tests/integration/test_wiring_smoke.py`：两个 `build_client` 调用所在
      setUp/函数体前加 `assembly.pin_framework_home()`（import 从
      `deerflow_deep_research.runtime`）。Verify: contract 测试转绿。
- [x] 2.2 `tests/integration/test_complete_graph_replay.py`：同上处理 :95 调用点。
- [x] 2.3 `tools/record_stream.py`：`record()` 内 `bundle_checkpointer` 前（已有
      `assembly` import）加 `assembly.pin_framework_home()`。
- [x] 2.4 全量回归：`make verify` exit 0（250+ tests）。

## 3. 文档同步与本地清理

- [x] 3.1 应用 README 运行与观察节：caveat 句改为"全部入口已 pin：create/refine 前台
      路径与 smoke/record 直连 client 都钉在仓库根 `.deer-flow/`（gitignored，应用
      子树外）"。
- [x] 3.2 控制地图目录树注：同步为"全入口 pin"，删除"第二家"描述。
- [x] 3.3 `rm -rf deep_research_harness/.deer-flow/`（gitignored，删前 `git status`
      确认无 tracked 内容混入）。

## 4. 回执与收口

- [x] 4.1 证明不再再生：`make smoke` exit 0（集成 lane 全绿）且
      `test ! -d deep_research_harness/.deer-flow`；回执记录命令、退出码、时长。
- [x] 4.2 `make lint` exit 0；`python3 openspec/governance/check_doc_hygiene.py` exit 0。
- [x] 4.3 closeout gate（`check_project_gate.py --phase closeout`）exit 0 →
      `openspec archive`（strict validate）→ 知识归位（无 spec delta，主干不动）。

## Deviation Register

- 2026-10-10：任务 1.2 的排序负例首跑无效（把 pin 插在 `events = []` 后——仍在 build_client 之前，负例未真正反转前提）；发现后改插到 build_client 调用块之后复跑，红→还原→绿闭环达成。任务顺序偏差：完整排序证明在 green（2.1–2.4）之后补做，非 tasks 原序——理由：绿树上的负例才有「唯一变量是顺序」的解释力。

## Delivery Record

- **外部行为**: 框架运行态只落仓库根 `.deer-flow/`（应用子树内不再出现第二运行态 home）：create/refine 前台路径 + smoke 两个直连 client + record 工具共 4 个 build_client 调用点全部先 pin（AST contract 锁，源码序敏感）。
- **影响面**: `tests/contract/test_framework_home.py`（+1 AST 测试）、`tests/integration/test_wiring_smoke.py`（+2 pin）、`tests/integration/test_complete_graph_replay.py`（+1 pin）、`tools/record_stream.py`（+1 pin）、应用 README 与 docs/control-map.md（caveat 反转为「全入口已 pin」）；删除 gitignored 本地目录 `deep_research_harness/.deer-flow/`。
- **实际跑了什么**: （退出码直读）红：`PYTHONPATH=src python3 -m unittest tests.contract.test_framework_home` → 1（点名 smoke 两方法缺 pin）；绿：同命令 → 0；`python3 -m unittest discover -s tests` → 0；排序负例（pin 移到 build_client 后）→ 1、还原 → 0；`make smoke` → 0（30 tests, 23.5s）且 `deep_research_harness/.deer-flow` 未再生；`make lint` → 0；`check_doc_hygiene` → 0；`check_change_guidance` → 0。
- **未执行的检查**: none。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）。
