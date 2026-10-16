# Tasks

## 1. Baseline and the shared journal helpers

- [x] 1.1 Record the baseline: from `deep_research_harness/` run `UV_OFFLINE=1 make verify`, `make smoke` and the ruff lint lane; verify all three exit 0 and record the case counts (expected verify 252, smoke 30)  ✓ verify 252 · smoke 30 · lint 0，三条全绿。
- [x] 1.2 Capture the pre-change evidence: the `pump` module's public surface (names starting with `_` included) and one exhaustion path's `unanswered-questions` file bytes, into `/tmp/cjw-before/`; verify both captures are non-empty  ✓ 公共面与重复计数均已捕获/核对（计数用 AST 精确名，不用前缀 grep）。
- [x] 1.3 Count the duplication to be removed: `grep -rn "def _now_iso\|def _journal\|def _msg_field"` over `src/` and the inline questions write in `gates.py`; verify the counts match the proposal's table (3 / 2 / 2 / 1 inline)  ✓ 实测与提案表一致：`_now_iso` 3 · `_journal` 2 · `_msg_field` 2 · gates.py 内联写 1 · `write_unanswered_questions` 调用者 0。**口径修正**：首版用 `grep "def _journal"` 得 5，那是前缀匹配（含 `_journal_result` 等不同函数），改用 AST 精确名后为 2。
- [x] 1.4 Add `now_iso()` and `journal_entry(handle, category, event, detail)` to `runtime/bundle/journal.py`, the latter validating through `JournalEntry(...).validate()`; verify `make verify` exits 0 (the strict contract is now the single implementation)  ✓ `journal.py` 增 `now_iso()` 与 `journal_entry()`（走 `.validate()`）；verify 252 绿。
- [x] 1.5 Switch `bundle_actions.py`, `admission.py` and `pump_parts/turn.py` onto the shared helpers and re-export the three names from `pump.py`; verify `make verify` exits 0, the public surface has no missing names, and the helper counts in `src/` dropped to one each  ✓ 三处改 import + `pump.py` 再导出；**探针结果：严格版未触发任何 RuleViolation**——既有调用方写的 journal 条目全部合规。

## 2. One framework-message adapter

- [x] 2.1 Add `runtime/adapters/messages.py` with `message_field()` and switch `pump_parts/turn.py` and `interaction/render.py` onto it; verify `make verify` exits 0 and `grep -c "def _msg_field"` over `src/` is 1 (the adapter)  ✓ 新增 `runtime/adapters/messages.py`；`_msg_field` 定义数降至 1。
- [x] 2.2 Verify the architecture checker exits 0 (the new module's layer and imports) and that the lint lane exits 0 (no unused re-exports)  ✓ 架构 checker exit 0 · lint exit 0。

## 3. The dead writer becomes the only writer

- [x] 3.1 Replace the inline questions write in `pump_parts/gates.py` with a call to `bundle_actions.write_unanswered_questions`; verify `grep -n "write_text" ` no longer appears in that branch and that `make verify` exits 0  ✓ 内联写替换为调用既有写入器；`gates.py` 不再有裸 `write_text`。
- [x] 3.2 Verify the writer is no longer dead: `write_unanswered_questions` now has exactly one caller, and the exhaustion path still lands the file  ✓ `write_unanswered_questions` 调用者 1（原为 0）；exhaustion 仍落地文件。
- [x] 3.3 Compare the exhaustion path's questions-file bytes against the capture from 1.2; verify identical, and verify `make smoke` exits 0  ✓ **字节级前后对照**：HEAD（改前）与当前树各驱动一次 exhaustion，同为 `failed-resume`/`auto_proceed_count=2`/56 字节/sha256 `e5581fd7d54c45d1`；smoke exit 0。

## 4. Closeout evidence

- [x] 4.1 Register the new module in `openspec/governance/required-paths.toml`; verify the architecture checker exits 0 from the repository root (including a mutation check: temporarily move the new module and confirm the checker reports the missing path, then restore)  ✓ 已登记 `runtime/adapters/messages.py`；含**变红实测**（移走 → `path.missing` exit 1 → 恢复 exit 0）。
- [x] 4.2 Run the full gate set: `make verify`, `make smoke`, the lint lane, the architecture checker, the code-budget checker, the doc-hygiene checker and the closeout gate; verify every exit code is 0 read directly  ✓ verify 252 · smoke 30 · lint 0 · arch 0 · budgets 0 · doc-hygiene 0 · closeout 0（全部退出码直测）。
- [x] 4.3 Confirm no test file changed: `git diff --stat origin/master..HEAD -- deep_research_harness/tests/` is empty; record the command and its output  ✓ `git diff --stat origin/master..HEAD -- deep_research_harness/tests/` 输出为空。
- [x] 4.4 Fill this change's `## Delivery Record` with the four required labels, the byte-comparison result and the raw receipt lines produced by the runner above  ✓ 见下 `## Delivery Record`。

## Delivery Record

- **外部行为**: journal 条目内容与顺序不变（套件里逐字断言的用例全绿）· exhaustion 的 questions 文件**字节级不变**（同 sha256 `e5581fd7d54c45d1`、56 字节、同终态 `failed-resume`/`auto_proceed_count=2`）· 产品公共面零缺失（`pump._journal` / `_now_iso` / `_msg_field` / `run_research` / `tail_journal` 全部可达）· **行为上唯一的有意差异**：exhaustion 的 questions 写入从裸 `write_text` 变为 `atomic_write_text`（同一份 JSON、同一路径，但不再可能写半个文件）。
- **影响面**: `runtime/bundle/journal.py`（新增 `now_iso()` 与 `journal_entry()`，严格校验）· `bundle_actions.py` / `admission.py` / `pump_parts/turn.py`（去掉本地副本，改 import）· `runtime/interaction/render.py`（改用共享适配器）· `runtime/pump_parts/gates.py`（内联写 → 调用既有原子写入器）· `runtime/pump.py`（再导出）· 新增 `runtime/adapters/messages.py` · `required-paths.toml` 登记 · **测试零改动**。
- **实际跑了什么**: `make verify` exit 0（Ran 252）· `make smoke` exit 0（Ran 30）· ruff lint exit 0 · 架构 checker exit 0（含变红实测：移走新模块 → `path.missing` exit 1 → 恢复 exit 0）· 体积闸 exit 0 · doc-hygiene exit 0 · closeout gate exit 0 · **重复计数（AST 精确名）**：`now_iso` 3→1、`journal_entry` 2→1、`message_field` 2→1、`write_unanswered_questions` 调用者 0→1、`gates.py` 内联 `write_text` 1→0 · **字节对照**：改前（`git worktree` @ HEAD）与改后同 sha256。
- **未执行的检查**: CAS 空转（事实 12）**未动**——它是行为正确性问题，按 CLS-025 裁决走 bug 轨、需 owner 授权 · 真实模型梯未跑（本 change 是接线合并，窄证据政策下不整跑）· `make smoke` 只覆盖脚本模型车道。

## Deviation Register

- 偏差 1（口径修正，如实记录）：任务 1.3 首版用 `grep "def _journal"` 计数得 **5**，与提案的 2 不符——那是**前缀匹配**污染（把 `_journal_result`/`_journal_turn`/`_journal_tool_calls` 也算进来了）。改用 AST 精确名后为 2，与提案一致。**教训：计数用的是"名字"就必须按名字精确匹配，前缀 grep 会把测量本身变成错误来源。**
- 偏差 2（有意的语义赌注，结果为正）：D-3 把 `_journal` 统一到**带 `.validate()`** 的严格版，原 `bundle_actions` 那份不校验。若既有调用方写不合词汇的条目，统一后会当场抛 `RuleViolation`。**实测结果：套件 252 全绿、smoke 30 全绿，零违规**——既有的 bundle 生命周期事件全部合规，于是两条写入路径现在获得同等的词汇守卫（这是**增强**，不是行为回退）。
- 偏差 3（首次实现时的一处真错误）：把 `admission.py` 的 `from .journal import append_entry` 换成新导入时删掉了它，而 `admission.py:90` 仍在调用 `append_entry` → `NameError`，由 verify 抓红后补回。**教训：替换导入行前先查该名字在本文件的全部用处，而不是只看我正要删的那个函数。**
- 偏差 4（再导出的家变了）：`turn.py` 不再使用 `_now_iso`（它的用法随 `_journal` 一起移走），lint 正确地把该导入移除，于是 `pump.py` 的再导出断了。修法：`_now_iso` 改从真正的家 `bundle.journal` 再导出，并入 `__all__`。**教训同阶段 4：跨层再导出的"来源模块"会随实现搬家而失效，必须让再导出指向实现的家。**
- none: 除上述四项外无其他设计偏离。
