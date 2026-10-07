# Tasks

> 红绿纪律：每个守卫先证红再校准绿；所有退出码直测，不用管道吞码。
> 工作目录：`deep_research_harness/`（除标注仓库根的治理命令）。

## 1. Workstream chain-lock（CHAIN-001）

- [x] 1.1 捕获基线：`PYTHONPATH=src python3 -m unittest discover -s tests -v 2>&1 | grep -c "\.\.\. ok"`
  与完整 test ID 清单（`... -v` 输出存档），记录 verify 当前计数，作 before/after 对照。
- [x] 1.2 新增 `tests/contract/test_entry_chain.py`（stdlib ast 解析，零产品 import），
  按 design 决策 1 断言六环调用签名；对现状应为绿。Verify:
  `PYTHONPATH=src python3 -m unittest tests.contract.test_entry_chain -v` 退出码 0。
- [x] 1.3 红证（守卫能变红）：临时 mutation 三连，每个 mutation 后跑 1.2 命令必须非零
  退出并命名断环，随后还原——(a) 把 `cmd_create` 改为直调 `run_engine.run_research`
  绕过 assembly；(b) 把 `run_foreground` 内 `make_stream_fn` 调用删除；(c) 把
  `_submit_final_report` 的 `submit_artifact` 改为直接落盘。记录三次红输出。
- [x] 1.4 还原后全绿：1.2 命令退出码 0，且 `make verify` 退出码 0（test ID 集合 = 基线 +
  新测试）。

## 2. Workstream vocabulary-fix（VOC-001, VOC-002）

- [x] 2.1 VOC-001 第一步（红证）：`git mv src/deerflow_deep_research/runtime/entry.py
  src/deerflow_deep_research/runtime/assembly.py`，不改任何 import。Verify:
  `PYTHONPATH=src python3 -m unittest tests.unit.interaction.test_entry_composition -v`
  捕获 ImportError 红输出（引用旧模块路径），照实记录。
- [x] 2.2 VOC-001 cutover：assembly.py 内部相对 import、`runtime/__init__.py` docstring、
  `interaction/cli.py` 的 `entrypoint` import、`tools/record_stream.py`、5 个消费测试文件
  （test_clarification_prompt / test_entry_composition / test_status_delivery /
  test_plan_prompt / test_refine_foreground）全部指向 assembly；同步
  `tests/contract/test_entry_chain.py` 中的路径引用。
  Verify: 仓库根 grep 旧引用
  `grep -rn "runtime\.entry\|runtime/entry\.py\|from \. import entry\|from \.entry" deep_research_harness/src deep_research_harness/tests deep_research_harness/tools` 零命中（openspec/changes 除外）。
- [x] 2.3 VOC-001 登记：`openspec/governance/required-paths.toml` 中 entry.py 路径改名为
  assembly.py。Verify（仓库根）: `python3 openspec/governance/check_project_architecture.py`
  退出码 0。
- [x] 2.4 VOC-002 第一步（红证）：`git mv src/deerflow_deep_research/runtime/run_engine.py
  src/deerflow_deep_research/runtime/pump.py`，不改 import。Verify:
  `PYTHONPATH=src python3 -m unittest tests.unit.runtime.test_run_engine -v` 捕获 ImportError。
- [x] 2.5 VOC-002 cutover：pump.py 自身 import、assembly 的 `from . import run_engine`
  → `from . import pump`、interaction/cli.py、tools/record_stream.py、5 个测试文件
  （test_run_engine / test_event_stream_replay / test_entry_surface /
  test_entry_composition / test_wiring_smoke）、chain-lock 测试引用、
  runtime/__init__.py docstring。
  Verify: `grep -rn "run_engine" deep_research_harness/src deep_research_harness/tools` 仅剩
  pump.py 内部合法出现（docstring 语义说明除外，逐条核对）。
- [x] 2.6 VOC-002 登记：required-paths.toml 改名同步；架构 checker 退出码 0。
- [x] 2.7 行为中性证明：重捕 test ID 清单与基线逐项 diff（必须零差异）；
  `make verify` 退出码 0；`make smoke` 退出码 0（uv 环境已备时；未备则如实标注
  UNVERIFIED 并先 `uv sync`）。
- [x] 2.8 文档 cutover：README 链条图改为 assembly/pump 并指向锁链测试；control-map §4
  瘦身为路由（链条六环 + 锁链测试指针，删除逐行复述）、§7 路由表链接更新；
  tests/README.md 登记新 contract 资产；run-bundle.md / research-process.md 模块链接更新。
  Verify（仓库根）: `python3 openspec/governance/check_doc_hygiene.py` 退出码 0，且所有
  移动模块链接在盘上可解析。

## 3. Workstream skill-slot（SKL-001, SKL-002）

- [x] 3.1 SKL-002 先行（红证）：在 `tests/contract/` 新增 guard——声明缺省必须解析为
  `None` 并透传 `build_client`（FakeClient 记录构造参数 + mirror 常量比对）。此时 config
  无 skills 段、build_client 硬编码，guard 对「binding 从声明取值」断言必红。记录红输出。
- [x] 3.2 SKL-001 实现：`config/base.yaml`、`config/fixture.yaml` 增 `skills:` 声明段
  （两梯均缺省未声明）；assembly 增声明解析（缺省严格返回 `None`，不吞类型错误）；
  `build_client` 改为接收解析结果透传 `available_skills`（默认参数仍是 None）。
  Verify: 3.1 guard 退出码 0。
- [x] 3.3 SKL-002 负例控制：临时把 build_client 硬编码为非 None 值 / 让解析吞错误类型，
  guard 必须红并命名被破坏的 seam，随后还原。记录红输出。
- [x] 3.4 全绿：`make verify` 退出码 0；`make smoke` 退出码 0；test ID 清单 = 基线 +
  chain-lock + skill guard，零意外增删。真实梯下 skill 实际加载行为**不证明**，回执标注
  UNVERIFIED（激活语义另立项）。

## 4. Program 收口（全 workstream 达标后）

- [x] 4.1 三 workstream 共享不变量复核：`make verify`、`make smoke`、架构 checker、
  doc 卫生 checker、`openspec validate 2026-10-07-surface-runtime-structure --strict`
  （仓库根）全部退出码直测为 0，逐条记录。
- [x] 4.2 git 证据（仓库根）：`git status --porcelain=v1 --untracked-files=all`、
  `git ls-files --stage deerflow`、`git submodule status -- deerflow`、
  `git -C deerflow status --porcelain=v1 --untracked-files=all`、
  `git diff --submodule=short`——确认 gitlink 指针未动、无 deerflow 工作树污染。
- [x] 4.3 对照 Program Focus 复核实际 diff 与批准范围一致（三个 workstream 外无越界
  文件）；verification-receipt 记录全部命令/退出码/revision，回执新于最后一次改动。
