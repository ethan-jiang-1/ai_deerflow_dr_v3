# Tasks

## 1. Decide the policy

- [x] 1.1 Find the readable-failure idiom the repo already uses, and the boundary where the run is invoked
- [x] 1.2 Weigh retry against raise, including the fact that the conflict's own message advises retrying
- [x] 1.3 Record the decision (raise, made readable at the boundary) and the considered alternative (bounded retry) with the reasons it was deferred

## 2. Land the readable failure

- [x] 2.1 Collapse the two verb call sites into one helper that owns both failure channels, keeping the existing environment message byte-identical
- [x] 2.2 Add the conflict channel: say another writer advanced the bundle and give a remedy
- [x] 2.3 Keep the runtime layer honest: it raises its typed exception, the CLI decides readability

## 3. Pin it

- [x] 3.1 Test: a conflict leaves as a `SystemExit` carrying both the reason and a remedy
- [x] 3.2 Test: the pre-existing environment message is unchanged, compared as a whole string
- [x] 3.3 Test (semantics): a writer landing between the gate's read and the write makes the gate **raise** rather than swallow
- [x] 3.4 Teach the entry-chain contract test one hop without weakening it: the verbs still must reach the foreground assembly

## 4. Lanes and closeout

- [x] 4.1 `make verify`, `make smoke`, the lint lane, the governance suite, all seven checkers and the closeout gate are green
- [x] 4.2 Confirm the normal path is unchanged (no journal or terminal-semantics change)
- [x] 4.3 Append the dated note to BUG-007's card, per the ledger's own annotation convention
- [x] 4.4 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（**我手搓的异常与真实异常不同**）：失败通道测试里我用 `ImportError("No module named 'deerflow'")` 构造异常，跑出来消息是 `missing module: None`——**手工构造的 `ImportError` 不设 `.name`**，真实导入错误才有。修法是补 `name="deerflow"`。**教训：用真实来源的对象做断言，手搓替身容易把"我以为的形状"当成契约。**
- 偏差 2（重构触发契约测试，**它是对的**）：抽 `_run_foreground` 后，`contract/test_entry_chain.py` 的两条用例立刻红——它用 AST 钉住"动词必须调到 `run_foreground`"，我的重构把调用挪进了一层。处置见 design D-3：**跟一跳但不放松**（既不调 `run_foreground` 也不调助手的动词照样红），而不是删断言。
- 偏差 3（lint 两次）：两个测试文件的 import 块排序被 `ruff` 判 `I001`，`--fix` 修好。同类已犯过多次，属书写习惯问题。
- none: 除上述三项外无设计偏离。

## Delivery Record

- **外部行为**: **正常路径零变化**——`make verify` 254 → **257**（+3 新用例）、`make smoke` 30 OK、journal 事件名与顺序未动、终态语义未动。**失败路径变化**：`StateRevisionConflict` 从"裸 traceback"变成带 Remedy 的 `SystemExit`（"refused to write: the bundle was advanced by another writer while this run was live (…). Remedy: make sure only one run drives a bundle at a time, then re-read the state and retry the command."）。既有的 "requires the deerflow environment" 消息**逐字保留**（有整串相等的测试钉住）。
- **影响面**: `runtime/interaction/cli.py`（新增 `_run_foreground` 助手；两个动词调用点收敛）· `tests/unit/interaction/test_refine_foreground.py`（`ForegroundFailureChannelTest` 2 条）· `tests/unit/runtime/test_pump_clarification.py`（语义 1 条）· `tests/contract/test_entry_chain.py`（跟一跳的辅助 + 两条断言改写）· BUG-007 的卡（追记）。**未动**：`bundle_state.py` 的 CAS 与 `check_lease` · `pump_parts/gates.py` · `pump.py` · `assembly.py` · 治理侧。
- **实际跑了什么**: `make verify` exit 0（**257**）· `make smoke` exit 0（30）· lint `All checks passed!`（`--fix` 修了 2 处 I001）· 治理套件 exit 0（258）· 七 checker + closeout gate 全 0 · 三条新用例各自绿（含"强制交错 ⇒ 必须抛"的语义）· 契约测试跟一跳后绿且**仍能红**（既不调 `run_foreground` 也不调助手的动词会失败）。
- **未执行的检查**: **未做有界重试**（design D-2 的备选，明确不做并写明两个必须先解决的问题）· **未把 `StateCorruption` / `LeaseViolation` 接进同一处理器**（不同失败类别，拓宽捕获是另一个决定）· **`pump.py` 终态写入的同类暴露面未处理**（它有相同形态：先读 `fresh` 再 CAS，冲突同样会抛；本把只收口了 `clarification_step` 这两条路径——BUG-007 的判据范围）· 未做真并发（多进程）压测，用例是确定性交错。
