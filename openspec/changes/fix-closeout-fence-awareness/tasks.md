# Tasks

## 1. Make the parser fence-aware

- [x] 1.1 Implement `_iter_outside_code_fences()` per CommonMark 4.5 (marker character, minimum three, info string allowed on opening but no backtick inside a backtick fence, closing requires the same character at least as long with only whitespace after, unclosed runs to the end); verify it compiles
- [x] 1.2 Route `_unchecked_task_labels()` through it; verify the probe matrix behaves (closed fence, unclosed fence, tilde fence, longer closing fence, info string, four-space indentation, closing fence with trailing text)
- [x] 1.3 Confirm the scope decision explicitly: four-space indentation stays a task (nested task lists), only fences are skipped

## 2. Invert the locking tests

- [x] 2.1 Replace `FencedCheckboxDefectTest` (the two tests written to be inverted) with `FencedCodeBlockTest` and flip both assertions
- [x] 2.2 Add the boundary cases: unclosed fence, tilde fence, shorter closing fence, closing fence with trailing text, opening info string, scanning resumes after a closing fence
- [x] 2.3 Assert the defect no longer reaches `_validate_review`: a fenced-only label now yields `unknown-unchecked-task`

## 3. Prove the new guard can fail

- [x] 3.1 Mutate the parser to be fence-blind and verify the fence tests fail; record the count
- [x] 3.2 Restore and verify they all pass again, with the tool's mutation reverted

## 4. The budget guard, and the card's graduation

- [x] 4.1 Run the code-budget checker: read its own instruction for a file over its ceiling
- [x] 4.2 Raise the entry to the measured value with a one-line justification naming BUG-003 and the split follow-up; verify the checker exits 0 and the three budget tests pass again
- [x] 4.3 Flip the card to `已修`, fill its fix-association section with the criteria evidence, `git mv` it into `_archived/_fixed_bugs/`, and sync both indexes plus the counter declarations; verify the doc-hygiene checker exits 0

## 5. Closeout evidence

- [x] 5.1 Run the full gate set: the governance suite, the seven checkers, the closeout gate, and the harness lanes; verify every exit code is 0 read directly
- [x] 5.2 Confirm the command line and the recorded schema are unchanged (`--help` plus the subcommand exit codes), and that `git diff --stat -- deep_research_harness/` is empty
- [x] 5.3 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（流程顺序，如实记录）：与上一把同样的问题——我先实现并验证了修复，之后才补
  `proposal.md` / `design.md` / `tasks.md`。原因是预算只够把风险最高的一步（解析改动 + 反转
  测试 + 变异检查）先做完。落地结果不受影响（文档在归档前补齐、门禁全绿），但顺序偏差属实。
- 偏差 2（上限被抬起，如实记录并留痕）：修复给 `selected_change_closeout.py` 加了 39 行，而它原为
  256/256 **顶格**。体积闸与三条预算测试同时变红。按闸自己给出的出路第二条处理——上限更正为实测
  295 并在表内写明理由（含"该拆了"的 follow-up）。**这不是把闸关掉**：长函数上限未动，下一次增长
  仍会触发；但该文件的棘轮确实被抬起一次，故记在此处。
- 偏差 3（刻意的范围决定，就地写明）：四空格缩进在 CommonMark 里属"缩进代码块"，但本工具
  **不跳过**它——`tasks.md` 的任务项合法地可以缩进四格。若按规范严格处理会**漏掉真任务**，
  比原缺陷更糟。已由一条测试锁定该边界。
- none: 除上述三项外无其他设计偏离。

## Delivery Record

- **外部行为**: 修复前后**唯一**的行为差异是"围栏代码块内的 checkbox 不再被当作任务"——这正是缺陷本身。命令行契约逐字不变（`--help` 与两个子命令的 usage/退出码：0 / 2 / 2）· `SCHEMA_VERSION` 仍为 `selected-change-closeout/v1` · harness 面零改动（`git diff --stat -- deep_research_harness/` 为空）。
- **影响面**: `openspec/governance/selected_change_closeout.py`（+围栏感知：新函数 `_iter_outside_code_fences` + 正则 `FENCE_LINE`，256 → 295 行）· `openspec/governance/check_code_budgets.py`（该文件上限 256 → 295 + 一行理由）· `openspec/tests/governance/test_closeout_decisions.py`（`FencedCheckboxDefectTest` 2 条 → `FencedCodeBlockTest` 11 条）· 卡片 `git mv` 入 `_archived/_fixed_bugs/` 并翻 `已修` · 两处索引 + `_fixed_bugs` 计数声明（2 → 3）。
- **实际跑了什么**: 治理套件 exit 0（190 → **198**）· 七个 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· **变异检查**：让解析器对围栏失明 → **9 条失败**；恢复 → 全过 · **围栏探针 7 例**（闭合 / 未闭合 / 波浪号 / 更长闭合 / info string / 四空格 / 闭合带尾随文字）行为全部与规范一致 · **体积闸**：越限时报 `295 > 256` 并给出两条出路；按第二条处理后 exit 0，三条预算测试恢复通过 · **文档卫生**：登记过程被计数守卫抓出两处不完整（`_fixed_bugs` 计数 2→3、索引行不能跟着批量改名），修正后 exit 0。
- **未执行的检查**: 拆这个 295 行的文件**未做**（登记为 follow-up；它自 2026-10-16 起可 import，故拆分前提已具备）· 缩进代码块按规范跳过**刻意未做**（偏差 3）· 其他治理脚本的同类解析盲区未排查（本 change 只修这一个）· 真实模型梯未跑（纯治理工具修复）。

## 交付给 owner 的 follow-up

1. **拆 `selected_change_closeout.py`**（现 295 行、顶格）。前提已具备：可 import、可单测（本会话两把已建 39 条直接覆盖）。
2. **同类盲区排查**：其他治理脚本若有"逐行匹配 Markdown"的解析，可能共享同一盲区；本 change 未排查。
