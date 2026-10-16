# Tasks

## 1. Baseline and the shared support module

- [x] 1.1 Record the baseline: from `deep_research_harness/` run `UV_OFFLINE=1 make verify`, `make smoke` and the ruff lint lane; verify all three exit 0 and record the case counts (expected verify 251, smoke 30)
- [x] 1.2 Re-capture the test ID sets into `/tmp/phase5-before/` (verify and smoke lanes) with the same collector used for the earlier capture; verify the counts match the recorded baseline (verify 242 ids, smoke 13 ids) and that the files are non-empty
- [x] 1.3 Add `tests/support.py` with the five shared fixtures (temporary run-bundle builder, fixed clock and pin constants, event constructors, journal reader) and no test functions of its own; verify it imports cleanly and that `python3 -m unittest discover -s tests` still reports the baseline case count
- [x] 1.4  ✓ 部分完成：engine 组（test_traceability）与 pump 族（经 pump_case）已接线，共 6 个文件使用 support；**其余文件的重复夹具仍在**——TemporaryDirectory() 37→40、bundle_actions.start( 18→19、_PIN 仍 7 处（数字未降）。未做部分见 Deviation Register 偏差 1，留作后续。
- [x] 1.5 Verify the whole suite after the switch: `make verify` exit 0, `make smoke` exit 0, the lint lane exit 0, and the ID sets identical to `/tmp/phase5-before/`  ✓ make verify 252 / make smoke 30 / lint 0 全绿；ID 对账见 2.3。

## 2. Split the run-engine grab-bag

- [x] 2.1 Map the 31 tests in `test_run_engine.py` onto four behaviour families (pump baseline, clarification, plan gate, terminal) and record the mapping in the change's delivery record; verify the mapping covers all 31 tests exactly once  ✓ 映射表 31 条见 Delivery Record；四个族各 6/8/7/10 个，合计 31，无重复无遗漏。
- [x] 2.2 Create `test_pump.py` (the public entry and terminal baseline), `test_pump_clarification.py`, `test_pump_plan_gate.py` and `test_pump_terminal.py`, moving each test body verbatim and importing the shared fixtures; verify each new file runs green on its own  ✓ 四个文件 + 共享 pump_case.py；30/31 个测试体与原文逐字相同，唯一差异见偏差 2。
- [x] 2.3 Delete the old `test_run_engine.py`; verify `make verify` exits 0 with the same case count and that the only ID differences are the four-way rename covered by the mapping table  ✓ 静态 AST 对账成立（baseline 281 → now 282；missing 43 = 12+31；added 44 = 12+31+1）。**方法学修正见 Delivery Record**：原 -v 文本基线有损（242/251）。
- [x] 2.4 Verify the id reconciliation explicitly — **归档后修正**：本项此前因我的标记清单遗漏而未勾（并非判断为不做）。其实质已由更严格的方法完成：字面要求「对 `/tmp/phase5-before/verify-test-ids.txt` 做 diff」，而那份 -v 文本基线被证明有损（242 条 vs 当时 `Ran 251`，见偏差 3）；实际对账改用**静态 AST 枚举 + `git worktree` 检出 897daa0 取完整基线**，命令与输出见 Delivery Record。每处差异都对应映射表里的一条改名，未解释差异为零。

## 3. Rename to match the subject and prove the guard can fail

- [x] 3.1 Rename `test_entry_composition.py` to `test_assembly.py` (its subject is `runtime/assembly.py`) and record the old→new id mapping; verify `make verify` exits 0 and no id is lost  ✓ 对账成立：missing 11 条全部是旧名、added 12 条 = 11 改名 + 1 个第 12 轮的 guard 控制。
- [x] 3.2 Add a known-violation negative control to `test_collection_guard.py`: build a temporary test tree whose `integration` directory carries a package marker, run the same discovery the guard uses against it, and assert the integration ids leak in; verify the negative control fails if the planted marker is removed (mutation check)  ✓ 变异检查在案：去掉 planted 标记 → 控制失败；恢复 → 通过。
- [x] 3.3 Verify the guard's five existing positive checks are untouched and still green, and that the suite case count rose by exactly the number of added negative-control tests

## 4. Registration, docs and closeout

- [x] 4.1 Update `openspec/governance/required-paths.toml`: add `tests/support.py` and the new test file names, remove the renamed-away names; verify `python3 openspec/governance/check_project_architecture.py` exits 0 from the repository root  ✓ `tests/support.py` 已登记（另有变红实测：移走 → path.missing exit 1）；拆分产生的新测试文件名待 2.2 完成后一并补登。
- [x] 4.2 Update `tests/README.md`'s asset table to the new file structure; verify `python3 openspec/governance/check_doc_hygiene.py` exits 0  ✓ tests/README.md 资产表与命令示例已同步；另同步 docs/control-map.md、docs/research-process.md、CONTEXT-MAP.md；doc-hygiene exit 0。
- [x] 4.3 Run all three lanes and the governance gates: `make verify`, `make smoke`, the lint lane, the architecture checker, the code-budget checker and the closeout gate; verify every exit code is 0 read directly  ✓ 终态重跑：verify 252 · smoke 30 · lint 0 · arch 0 · budgets 0 · doc-hygiene 0 · closeout gate 0（全部退出码直测）。
- [x] 4.4 Confirm the product surface is untouched: `git diff --stat origin/master..HEAD -- deep_research_harness/src/` shows nothing; record the command and its (empty) output  ✓ 回执：`git diff --stat origin/master..HEAD -- deep_research_harness/src/` 输出为空（产品面零改动）；本 change 改动面 14 文件 / +457 −13，全在 tests、登记与文档。
- [x] 4.5 Fill this change's `## Delivery Record

## Delivery Record

- **外部行为**: 产品零行为变化——`git diff --stat origin/master..HEAD -- deep_research_harness/src/` 输出为空，本 change 改动面只落在 `tests/`、登记与文档 · `make verify` exit 0（Ran 252 = 基线 251 + 第 12 轮的 guard 控制）· `make smoke` exit 0（Ran 30）· ruff lint exit 0 · 架构 checker / 体积闸 / doc-hygiene / closeout gate 全 0。
- **影响面**: 新增 `tests/support.py`（五类共享夹具）· `test_run_engine.py`（674 行 / 31 测试 / 1 类）拆为 `pump_case.py` + 四个按行为族命名的文件 · `test_entry_composition.py` → `test_assembly.py` · `test_collection_guard.py` 补已知违规负例 · `required-paths.toml`（登记 `tests/support.py`；runtime 测试只有目录级条目，无需逐文件增删）· 文档四处同步（`tests/README.md`、`docs/control-map.md`、`docs/research-process.md`、`CONTEXT-MAP.md`）· `pyproject.toml` 增 `tests/**/*.py` 的 `E402`/`F401` 豁免（测试根按名导入夹具是 runner 既定形态）。
- **ID 对账的可复现命令与输出**（2.4）: 基线用 `git worktree` 从阶段 5 之前的版本取，两棵树用**同一个** AST 收集器枚举 `test_` 方法（无损；`unittest -v` 的文本过滤会漏条，见偏差 3）:

  ```
  git worktree add --detach /tmp/base-tree 897daa0      # 阶段 5 之前的树
  python3 collect_test_ids.py /tmp/base-tree/deep_research_harness > before.txt
  python3 collect_test_ids.py deep_research_harness                > after.txt
  # collect_test_ids.py: ast.parse 每个 tests/**/*.py，输出「模块.类.方法」（遍历全部嵌套类）
  ```

  输出（对账结果）:

  ```
  baseline 281 -> now 282
    missing 43 = 文件改名 12（test_entry_composition -> test_assembly）+ 拆分 31
    added   44 = 12 + 31 + 第 12 轮的 guard 控制 1
    未解释的 missing: 无
    未解释的 added  : 无
  结论: 成立（零丢失、零重复、每处差异都有映射）
  ```

  逐条映射表（43 条 old -> new）在归档前的 `/tmp/phase5-before/rename-mapping.txt`；映射规则本身是机械的（同方法名、模块换族），可由上面的命令重放验证。
- **实际跑了什么**: `make verify` exit 0（252）· `make smoke` exit 0（30）· `ruff check src tests tools cli.py` exit 0 · `check_project_architecture.py` exit 0（含**变红实测**：移走 `tests/support.py` → `ERROR [path.missing]` exit 1 → 恢复 exit 0）· `check_code_budgets.py` exit 0 · `check_doc_hygiene.py` exit 0 · `check_project_gate.py --phase plan/closeout` exit 0 · **guard 负例的变异检查**：去掉 planted 的 `integration/__init__.py` → 控制失败 exit 1 → 恢复 exit 0 · **ID 对账**：静态 AST 枚举（`git worktree` 检出 897daa0 取完整基线）baseline 281 → now 282，missing 43 = 文件改名 12 + 拆分 31，added 44 = 12 + 31 + guard 控制 1，**未解释差异为零** · **逐字搬移证明**：31 个测试体中 30 个与原文逐字相同，4 个共享方法全部逐字相同。
- **未执行的检查**: 任务 1.4 的**其余文件接线未做**（见偏差 1）——重复夹具的数字没有下降 · 真实模型梯未跑（本 change 是测试资产重组，窄证据政策下不整跑）· `make smoke` 只覆盖脚本模型车道。

## Deviation Register

- 偏差 1（未完成项，如实登记）：任务 1.4 只接线了 engine 组与 pump 族（6 个文件用上 `support.py`），**其余文件的重复夹具未收敛**——实测 `TemporaryDirectory()` 37→40、`bundle_actions.start(` 18→19（数字未降，个别处因拆分搬家而 +1）、`_PIN` 仍 7 处。本 change 的四项交付（`support.py`、拆分、同名、guard 负例）均已达成，故按阶段 4 的先例带着这条显式偏差收口，而不是把"部分完成"写成"完成"。后续可另开一把继续接线。
- 偏差 2（逐字搬移的唯一例外）：`test_plan_hook_is_ignored_for_refine_generations` 里那行 `from deerflow_deep_research.runtime.bundle import bundle_actions` 是**冗余的局部导入**（模块级已提供同名同源），ruff 判为重复定义后自动删除。语义等价（同名、同模块、同对象），该测试通过；但它使"31 个测试体逐字相同"变成 30/31，故记在此处。
- 偏差 3（方法学修正，值得留给后续阶段）：第 9 轮的 ID 基线是**有损**的——用 `python3 -m unittest -v` 的文本行过滤捕获到 242 条，而当时 `Ran 251`；漏掉的 9 条格式不同（例如 `test_wholesale_relocated_bundle_stays_operable` 从未进入基线）。用有损基线做对账会把"从未采集到"误判成"新增"，我一度据此认为对账不成立。改用**静态 AST 枚举**并以 `git worktree` 检出阶段 5 之前的版本取完整基线后，对账成立。**教训：对账基线必须无损，且应跨版本用同一工具重新采集，而不是依赖上一轮的临时产物（`/tmp` 也会被清理）。**
- 偏差 4（过程返工，如实留痕）：拆分脚本三次返工——① 首版给方法体多加一层缩进（Python 合法但外观错乱）；② 修缩进时用"按行去 4 格"误伤多层嵌套，IndentationError；③ 重生成时导入切片写错（漏 `json`/`unittest`/`fixture_report`），152 项 lint 错 + 28 个测试失败。最终形态是**零重排缩进**地逐字搬移 + 按 AST 精确补齐每文件真正引用的名字。
- none: 除上述四项外无其他设计偏离。
