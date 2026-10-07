# Tasks

> 红绿纪律：每个守卫先证红再校准绿；退出码直测，不用管道吞码。
> 工作目录：`deep_research_harness/`（除标注仓库根的治理命令）。

## 1. 纯分类器（domain/diagnosis.py）

- [x] 1.1 红证先行：新增 `tests/unit/domain/test_diagnosis.py`，对 `domain.diagnosis`
  的 import 即红（模块不存在）。记录红输出。
- [x] 1.2 实现 `domain/diagnosis.py`：typed Diagnosis 合同 + `classify(state, entries,
  diagnostics_existence) -> Diagnosis`，按 design 决策 2/3 实现七类互斥 + ambiguous。
  Verify: 1.1 的测试文件扩到七类各一个真实形状用例 + ambiguous + active 不分类，
  `PYTHONPATH=src python3 -m unittest tests.unit.domain.test_diagnosis -v` 退出码 0。
- [x] 1.3 类间碰撞负例：构造"两类特征同时出现"的输入（如 framework_error 事件 + 死
  PID），断言 terminal 事件优先、不产生双分类；构造两条终态事件断言 ambiguous。
  Verify: 同上命令退出码 0。

## 2. diagnose 动词（interaction + render + 命令面）

- [x] 2.1 红证：`test_command_surface`（COMMANDS/Makefile/CLI 三处清单一致）先跑
  `PYTHONPATH=src python3 -m unittest tests.unit.interaction.test_command_surface -v`
  ——在 COMMANDS.md 加入 diagnose 后它应红（或按其守卫顺序先改 CLI 再看红），红证记录
  该守卫咬合命令面漂移。
- [x] 2.2 实现：`render.py` 增诊断渲染（类别/环节/证据指针三要素）；`cli.py` 增
  `cmd_diagnose`（resolve_bundle → read_state → read_entries → diagnostics 存在性 →
  classify → render）与 argparse 注册；`COMMANDS.md` 七动词菜单 + `test_entry_surface`
  渲染用例。Verify: 2.1 守卫转绿；`PYTHONPATH=src python3 -m unittest
  tests.unit.interaction.test_entry_surface tests.unit.interaction.test_command_surface
  -v` 退出码 0。
- [x] 2.3 只读边界测试：对 fixture 构造 Bundle 跑 `cmd_diagnose`（或其 verb 层函数），
  命令前快照 Bundle 全部工件哈希，命令后逐字节相同；active Bundle 输出"仍在运行"且无
  终态分类。Verify: `PYTHONPATH=src python3 -m unittest
  tests.unit.interaction.test_entry_surface -v` 退出码 0。

## 3. 集成旅程（smoke 车道）

- [x] 3.1 `tests/integration/test_cli_journey.py` 增诊断旅程：raising fixture model 驱动
  `create` 至 failed-resume（预期非零/失败输出），随后 `diagnose <bundle>` 断言
  `model_call_failed` 类别 + error_type + 证据指针出现。Verify（uv 环境）:
  `UV_CACHE_DIR="$PWD/../.uv-cache" uv run --no-sync python -m unittest discover -s
  tests/integration -p 'test_cli_journey.py' -v` 退出码 0。
- [x] 3.2 全量双车道：`make verify` 退出码 0（test ID = 基线 + 新增，逐项 diff 无意外）；
  `make smoke` 退出码 0。

## 4. 登记与收口

- [x] 4.1 manifest：`required-paths.toml` 登记 `domain/diagnosis.py` 与两个新测试文件
  （unit/domain/test_diagnosis.py 按 unit 组惯例）。Verify（仓库根）:
  `python3 openspec/governance/check_project_architecture.py` 退出码 0。
- [x] 4.2 文档：tests/README.md 资产表登记三个新资产 + "改什么测什么"行；
  docs/run-bundle.md 观察命令分工表加 diagnose 行（只读投影定位）。Verify（仓库根）:
  `python3 openspec/governance/check_doc_hygiene.py` 退出码 0。
- [x] 4.3 收口门禁（仓库根）：`openspec validate <change> --strict`、
  `python3 openspec/governance/check_project_gate.py --phase closeout`、`git diff --check`
  全部退出码直测 0；回执记录全部命令/退出码/revision，标注真实模型质量仍不在证明范围。
