# Tasks

## 1. Baseline and the shared support module

- [x] 1.1 Record the baseline: from `deep_research_harness/` run `UV_OFFLINE=1 make verify`, `make smoke` and the ruff lint lane; verify all three exit 0 and record the case counts (expected verify 251, smoke 30)
- [x] 1.2 Re-capture the test ID sets into `/tmp/phase5-before/` (verify and smoke lanes) with the same collector used for the earlier capture; verify the counts match the recorded baseline (verify 242 ids, smoke 13 ids) and that the files are non-empty
- [x] 1.3 Add `tests/support.py` with the five shared fixtures (temporary run-bundle builder, fixed clock and pin constants, event constructors, journal reader) and no test functions of its own; verify it imports cleanly and that `python3 -m unittest discover -s tests` still reports the baseline case count
- [ ] 1.4   ⚠ 进行中：engine 组（`test_traceability.py`）已切换，其余三组待做。Switch the test files onto `tests/support.py` one group at a time (runtime, interaction, domain/engine, contract), removing each file's local copies of the moved fixtures; after each group verify `make verify` exits 0 and the ID set is unchanged
- [ ] 1.5 Verify the whole suite after the switch: `make verify` exit 0, `make smoke` exit 0, the lint lane exit 0, and the ID sets identical to `/tmp/phase5-before/`

## 2. Split the run-engine grab-bag

- [ ] 2.1 Map the 31 tests in `test_run_engine.py` onto four behaviour families (pump baseline, clarification, plan gate, terminal) and record the mapping in the change's delivery record; verify the mapping covers all 31 tests exactly once
- [ ] 2.2 Create `test_pump.py` (the public entry and terminal baseline), `test_pump_clarification.py`, `test_pump_plan_gate.py` and `test_pump_terminal.py`, moving each test body verbatim and importing the shared fixtures; verify each new file runs green on its own
- [ ] 2.3 Delete the old `test_run_engine.py`; verify `make verify` exits 0 with the same case count and that the only ID differences are the four-way rename covered by the mapping table
- [ ] 2.4 Verify the id reconciliation explicitly: diff the post-change ID set against `/tmp/phase5-before/verify-test-ids.txt`, confirm every difference is a rename listed in the mapping, and record the command and its output

## 3. Rename to match the subject and prove the guard can fail

- [x] 3.1 Rename `test_entry_composition.py` to `test_assembly.py` (its subject is `runtime/assembly.py`) and record the old→new id mapping; verify `make verify` exits 0 and no id is lost  ✓ 对账成立：missing 11 条全部是旧名、added 12 条 = 11 改名 + 1 个第 12 轮的 guard 控制。
- [x] 3.2 Add a known-violation negative control to `test_collection_guard.py`: build a temporary test tree whose `integration` directory carries a package marker, run the same discovery the guard uses against it, and assert the integration ids leak in; verify the negative control fails if the planted marker is removed (mutation check)  ✓ 变异检查在案：去掉 planted 标记 → 控制失败；恢复 → 通过。
- [x] 3.3 Verify the guard's five existing positive checks are untouched and still green, and that the suite case count rose by exactly the number of added negative-control tests

## 4. Registration, docs and closeout

- [x] 4.1 Update `openspec/governance/required-paths.toml`: add `tests/support.py` and the new test file names, remove the renamed-away names; verify `python3 openspec/governance/check_project_architecture.py` exits 0 from the repository root  ✓ `tests/support.py` 已登记（另有变红实测：移走 → path.missing exit 1）；拆分产生的新测试文件名待 2.2 完成后一并补登。
- [ ] 4.2 Update `tests/README.md`'s asset table to the new file structure; verify `python3 openspec/governance/check_doc_hygiene.py` exits 0
- [ ] 4.3 Run all three lanes and the governance gates: `make verify`, `make smoke`, the lint lane, the architecture checker, the code-budget checker and the closeout gate; verify every exit code is 0 read directly  ⚠ 已完成一次全绿回执（见下），但须在 2.x 拆分完成后**重跑**并以终态为准。
- [x] 4.4 Confirm the product surface is untouched: `git diff --stat origin/master..HEAD -- deep_research_harness/src/` shows nothing; record the command and its (empty) output  ✓ 回执：`git diff --stat origin/master..HEAD -- deep_research_harness/src/` 输出为空（产品面零改动）；本 change 改动面 14 文件 / +457 −13，全在 tests、登记与文档。
- [ ] 4.5 Fill this change's `## Delivery Record` with the four required labels, the id-reconciliation result and the raw receipt lines produced by the runner above

## Deviation Register

- none: 本 change 只重组测试资产并把重复夹具收敛为一份共享模块；"255 个测试 ID 逐条对账"是硬不变量，若 apply 期间发现某个测试无法在不改变其断言的前提下搬移（例如依赖所在文件的模块级状态），按 core 原则记入本表并写明裁决依据与落点，而不是悄悄改断言或删测试。

## Delivery Record

- **外部行为**: 待 apply 填写（预期：产品零行为变化；`make verify` 与 `make smoke` 用例数不变且全绿；测试 ID 集合逐条对账，仅改名项按映射表差异）
- **影响面**: 待 apply 填写（预期：新增 `tests/support.py`；`test_run_engine.py` 拆为四个文件；`test_entry_composition.py` → `test_assembly.py`；`test_collection_guard.py` 补一个负例；`required-paths.toml`；`tests/README.md`；`src/` 零改动）
- **实际跑了什么**: 待 apply 填写（runner 写下命令、退出码、revision）
- **未执行的检查**: 待 apply 填写
