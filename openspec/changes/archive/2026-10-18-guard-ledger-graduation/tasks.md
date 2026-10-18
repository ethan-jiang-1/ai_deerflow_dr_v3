# Tasks

## 1. Evidence first

- [x] 1.1 Enumerate what the ledger guards already cover (status vocabulary per surface, roster, counters, next-ID declarations, table placement) and what they do not
- [x] 1.2 Grep for any check of the fix-association section or of the change it names (expected and confirmed: none)
- [x] 1.3 Measure the discipline itself with git: for every card under `_archived/_fixed_bugs/`, find the commit that first added it and whether that commit touched anything outside `_backlog/` (measured 6/6 compliant)

## 2. The rule

- [x] 2.1 Add `project_architecture_check/graduation.py`: for each graduated card, resolve its adding commit and require at least one touched path outside `_backlog/`
- [x] 2.2 Stay silent when history cannot answer — no git binary, a failing git call, an untracked card — because the governance fixtures build temporary trees with no history, and failing there would report a blind spot as a violation
- [x] 2.3 Document the rule's boundary in the module docstring: co-landing is necessary, not sufficient; card-to-change correspondence stays a review question
- [x] 2.4 Wire it into `validate_project()` next to the other non-import rules, deliberately not into `--imports-only`

## 3. Prove it both ways

- [x] 3.1 Red: a card committed alone (only ledger paths) is reported, with the card name and the commit in the detail
- [x] 3.2 Green: a card committed together with an implementation file is accepted
- [x] 3.3 Skipped: an untracked card, and a tree with no git repository at all
- [x] 3.4 The real repository's history passes (all six graduated cards)
- [x] 3.5 Mutation check: remove the outside-the-ledger test and verify the red case stops being caught; restore byte-identically

## 4. Ratchet, registration, closeout

- [x] 4.1 Add the new module to the budget table at its measured value; verify the budget checker and its three tests pass
- [x] 4.2 Register it in `required-paths.toml`; verify the architecture checker exits 0
- [x] 4.3 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0
- [x] 4.4 Confirm no existing judgement changed and the application side is untouched
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（流程顺序，第五次）：又是**先实施验证、后补 propose/design/tasks**。前四把我把它记成"已知取舍"（用文档顺序换"先拿到可验证的实质结果"），这次是第五次——**它已经成为我的稳定模式，而不是例外**。落地不受影响（归档前补齐、门禁全绿），但它值得被当成一个**事实**记下来：在有预算压力的连续作业里，我会把"能验证的实质结果"排在"工件顺序"前面。
- 偏差 2（测试里留下草稿残句）：`test_ledger_graduation.py` 初稿留了一行 `self.commit(...) if False else None`，是我起草时的占位残句。它不影响断言（恒不执行），但属明显的草稿痕迹，已清除。**教训：占位句要么立刻删、要么写成真断言，不要留在交付物里。**
- none: 除上述两项外无其他设计偏离。

## Delivery Record

- **外部行为**: **只增不改**——`validate_project()` 追加 1 步；`imports.py`/`cycles.py`/`markdown_grammar.py` 与其余步骤未触碰，clean tree 的 stdout 与退出码逐字不变。新增失败面只有一条：`ERROR [ledger.graduation_without_implementation] <卡> was graduated by <sha>, a commit that touched only _backlog/; …` + exit 1。真实历史（6 张卡）绿。
- **影响面**: 新增 `project_architecture_check/graduation.py`（**75 行**）与 `openspec/tests/governance/test_ledger_graduation.py`（5 条）· `facade.py` +2 行（导入与一处调用，并更新了那段"两条非导入规则"的注释）· `check_code_budgets.py`（新模块入表 75/0）· `required-paths.toml`（登记）。
- **实际跑了什么**: **先期 git 实测**（6/6 已修卡由含实现的提交移入）· 治理套件 exit 0（250 → **255**）· 七 checker 逐个 exit 0 · closeout gate exit 0 · **四例探针**（卡片独自提交红 · 卡片+实现绿 · 未跟踪跳过 · 无 git 树跳过）逐条实测 · **真实树绿** · **变异检查**：去掉"是否动了 `_backlog` 之外"的判定 → 红例不再被捕获（1 条失败）→ 恢复后与备份**字节一致** · 体积闸与三条预算测试全过 · harness 改动行数 0。
- **未执行的检查**: **未校验 `修复关联` 点名的 change 是否存在**——取证显示这项目前**零检查**，但它需要从自由文本里解析 change 名（判据比本条的"提交共同落地"弱且更易误报），留作 follow-up，已写进提案的 Not in scope——**追记（2026-10-18）：已由 change `machine-readable-fix-reference`（2026-10-18）落地：卡片新增 `> 修复:` 字段并由账本规则校验其存在** · 未校验状态**时序**（如 `已落修` → `已修` 的先后）· 历史被 rebase/squash 改写后的行为未测 · 真实模型梯未跑（纯历史分析）。
