# Tasks

## 1. Evidence first

- [x] 1.1 Probe the three candidate parses at function level (section boundary, review table collection, program-mode heading count) and record each outcome
- [x] 1.2 Prove it end to end: plant a fenced heading inside a *valid* change's proposal and confirm the checker rejects it (`focus.field_missing`), then restore

## 2. Adopt the one fence rule

- [x] 2.1 Add `_without_fences()` to `helpers.py` (the shared rule masks fenced lines, preserving line count) and keep the existing regexes unchanged
- [x] 2.2 Rewrite `_section_after_heading()` as a line walk that skips fenced lines, returning a slice of the *original* text (masking would shift offsets)
- [x] 2.3 Route the review table-line collection and the program-mode heading counts through the mask
- [x] 2.4 Do the same for the product document's `> authority:` count (same line-regex shape, same risk)

## 3. Prove it both ways

- [x] 3.1 All three probes flip: the section keeps its later fields, the fenced table is no longer the header, the fenced program heading no longer counts
- [x] 3.2 The end-to-end planted-fence case now passes instead of being falsely rejected
- [x] 3.3 Legal shapes still behave: a real heading still ends the section, a real program heading still counts
- [x] 3.4 Mutation check: make `_without_fences()` a no-op and verify the new tests fail; restore byte-identically

## 4. Fixture closure, ratchet, closeout

- [x] 4.1 Add the shared module to the end-to-end fixture's hand-maintained source list (the copied tree must carry the package's dependency closure)
- [x] 4.2 Re-measure the three touched files and update their ceilings; verify the budget checker and its three tests pass
- [x] 4.3 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0
- [x] 4.4 Confirm the application side is untouched: `git diff --stat -- deep_research_harness/` is empty
- [x] 4.5 Flip BUG-006 to `已修`, fill its fix association with the criteria evidence, move it into `_archived/_fixed_bugs/`, and sync both indexes plus the counter
- [x] 4.6 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（缩进假设，重复犯）：`proposals.py` 的计数块我按 10 空格缩进写替换串，实际是 8 空格 ⇒
  断言失败（第一次）。**同一类错误（假定缩进/假定锚点形态）本会话已多次出现**，修法是先把目标
  文本打出来再写替换（repr 打印），而不是凭记忆。
- 偏差 2（手维护的依赖闭包，测试响亮失败）：`change_guidance_check` 新增对 `markdown_fences.py`
  的模块级导入后，`test_project_gate.py` 的端到端植入负例把仓库**按固定清单**拷贝到临时树，
  而清单里没有那个共享模块 ⇒ 拷贝树里 `ModuleNotFoundError`。**它失败得很响亮**（正是该测试的
  价值），修法是把新依赖加进清单。**教训：那份清单是依赖闭包，任何新导入边都必须同步它**——
  而它是手维护的，没有任何守卫会提醒（除测试本身）。
- 偏差 3（上限第三次被抬，按规则留痕）：`proposals.py` 460→462、`guidance.py` 405→408、
  `reviews.py` 243→248。加的行是**守卫与其接线**，缩回等于删修复；三处均已写明理由。
- 偏差 4（`> authority:` 那一处只做了机制同构判断）：`guidance.py` 的计数修法与另三处相同、风险
  同形，但我**没有**为它单独做端到端探针。判据是"同一函数、同一形状、同一后果"，属机制同构而
  非独立证据，如实记在此处并列入未执行检查。

## Delivery Record

- **外部行为**: 修的是**假拒绝**。端到端实测：在合规 proposal 里种入围栏标题，修复前 `[focus.field_missing]` exit 1，修复后 `Change Guidance governance passed.` exit 0。真实树既有判定逐字不变（`Change Guidance governance passed.`）· 三条探针全部翻转（章节含后续字段、表格首行仍是真表头、`program_count` 为 0）· 既有规则语义与消息文本未改（四处只改"喂给正则的文本"）· 七个 checker + closeout gate 全绿 · harness 面零改动（`git diff --stat -- deep_research_harness/` 为空）。
- **影响面**: `change_guidance_check/helpers.py`（+`_without_fences`、`_section_after_heading` 改行遍历）· `reviews.py` · `proposals.py` · `guidance.py`（三处改接遮蔽）· 新增 `openspec/tests/governance/test_guidance_fences.py`（5 条）· `test_project_gate.py`（夹具依赖闭包补 `markdown_fences.py`）· `check_code_budgets.py`（三处上限按实测）。
- **实际跑了什么**: 治理套件 exit 0（236 → **241**）· 七个 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· **三条探针**函数级前后对照 · **端到端**植入/恢复对照（修复前 exit 1、修复后 exit 0）· **变异检查**：`_without_fences()` 变成恒等函数 → 新测试 2 条失败 → 恢复后与备份**字节一致** · **夹具闭包**验证（补入后拷贝树正常工作，端到端负例仍有效）· 体积闸与三条预算测试全过 · harness 改动行数 0。
- **未执行的检查**: `guidance.py` 的 `> authority:` 计数**未单独做端到端探针**（判据是机制同构，见偏差 4）· 本 change 未把围栏规则**声明进 spec**（仍属工具内部解析）· 未系统排查其他治理脚本的逐行 Markdown 解析（`check_doc_hygiene`/`check_project_specs`/closeout 工具三处已在此前各把收敛）· 真实模型梯未跑（纯静态解析）。
