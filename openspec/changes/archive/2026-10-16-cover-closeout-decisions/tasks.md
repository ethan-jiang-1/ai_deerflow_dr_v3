# Tasks

## 1. Baseline and the direct-import harness

- [x] 1.1 Record the baseline: the governance suite (159 tests) and the harness lanes (`UV_OFFLINE=1 make verify` 252, the ruff lane) all exit 0
- [x] 1.2 Confirm the coverage gap is real: `grep` the seven decision functions over `openspec/tests/` and verify each shows 0 references
- [x] 1.3 Load the tool with a real `import` (governance dir on `sys.path`, restored in `finally`) rather than a path-based `importlib` load; verify the module object exposes the seven functions

## 2. Cover the pure decision functions

- [x] 2.1 `_parse_attestation`: accept a complete payload; refuse a non-mapping, each missing field, and blank/non-string fields
- [x] 2.2 `_planning_home`: find the nearest planning home from a deep start; return None when none exists
- [x] 2.3 `_active_change_root`: resolve an existing change; refuse path-shaped names (empty, dot, dotdot, slashes); return None for an unknown change
- [x] 2.4 `_unchecked_task_labels`: parse the three bullet markers and indentation; ignore checked and blank labels; empty for a missing file; ignore prose/heading/numbered/malformed lines
- [x] 2.5 `_validate_review`: accept both dispositions; refuse an output path outside the evidence root, a non-mapping payload, an unsupported disposition, unusable task references, a reference that is not an unchecked task, and an inconclusive payload without a limitation

## 3. Cover the git-backed boundary check

- [x] 3.1 `_resolved_commit`: resolve a real commit in a temporary repository (40 hex chars) and return None for an unknown reference
- [x] 3.2 `_verify_boundary` success: a temporary repository holding an active change with a clean worktree verifies a declared range and returns `boundary-verified` with a diff summary
- [x] 3.3 `_verify_boundary` refusals: a relative repository identity, an unknown commit, head drift, and a dirty worktree each return their own condition
- [x] 3.4 Verify no test writes to the real repository: every case works under a temporary directory, and cwd is restored via `addCleanup`

## 4. Prove the tests are load-bearing

- [x] 4.1 Mutate `_parse_attestation` to accept blank fields; verify the new tests fail, then restore
- [x] 4.2 Mutate the unchecked-task pattern to also match checked boxes; verify the new tests fail, then restore
- [x] 4.3 Remove the task-reference subset check in `_validate_review`; verify the new tests fail, then restore
- [x] 4.4 Confirm the tool file is byte-identical afterwards (`git diff --stat` on it is empty)

## 5. The fenced-checkbox probe

- [x] 5.1 Probe whether a checkbox-shaped line inside a fenced code block is collected as a task; record the answer either way
- [x] 5.2 Because the answer is yes, lock the current behaviour with tests that name it a recorded defect, state the consequence for `_validate_review`, and say how to invert the assertion once fixed; verify the suite stays green
- [x] 5.3 Hand the defect to its owner in the delivery record rather than repairing it here (this change may not change the tool)

## 6. Closeout evidence

- [x] 6.1 Run the full gate set: the governance suite, `check_project_gate.py --phase closeout`, the seven checkers, the ruff lane and `make verify`; verify every exit code is 0 read directly
- [x] 6.2 Confirm no product, tool, or harness surface changed: `git diff --stat` over `deep_research_harness/` and `selected_change_closeout.py` is empty
- [x] 6.3 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines

## Deviation Register

- 偏差 1（流程顺序，如实记录）：本 change 我先写了测试文件、**之后**才补 `design.md` / `tasks.md`——与仓库"proposal → design/tasks → 红绿"的顺序不符。原因是当时预算只够完成风险最高的一步（把 7 个函数的真实契约摸清并写出可运行的测试），而把规划文档留到下一步做。**落地结果不受影响**（文档在归档前补齐、门禁全绿），但顺序偏差属实，故记在此处。
- 偏差 2（**发现真实缺陷，按授权不改**）：`_unchecked_task_labels` 逐行匹配，**围栏代码块里的 checkbox 会被当成真任务**；该缺陷经 `_validate_review` 放大——review 可以引用一个只作为示例存在于围栏里的标签，工具会把它当作真正的未勾任务接受，于是回执"证明"了一件并非任务的事。本 change 的授权是**加覆盖**，不是改工具，故按仓规第 4 条**就地锁定**（两条测试 + 注释写明后果与修好后的反转方式），并把裁决交还 owner。**未修**。
- 偏差 3（上一轮欠账，本轮补齐）：proposal 里承诺的围栏探针与 `_verify_boundary` 成功路径，上一轮因预算未做，本轮已补（任务 3.2/3.3/5.x）。
- none: 除上述三项外无其他设计偏离。

## Delivery Record

- **外部行为**: 零变化。`selected_change_closeout.py` **一行未改**（`git diff --stat` 对它为空）· 命令行契约与 `SCHEMA_VERSION` 不变 · harness 面零改动（`git diff --stat -- deep_research_harness/` 为空）· 治理套件 159 → **190**（+31，全绿）。
- **影响面**: 仅新增 `openspec/tests/governance/test_closeout_decisions.py`（31 条用例，7 个用例类）。无 src、无工具、无登记、无文档改动。
- **实际跑了什么**: 治理套件 exit 0（Ran 190, OK, skipped=1）· 七个 checker 逐个 exit 0（architecture / change-guidance / code-budgets / doc-hygiene / ci-governance / proof-receipts / harness-dependency-direction）· closeout gate exit 0 · `make verify` exit 0（252）· ruff lint exit 0 · **覆盖缺口实测**（7 个函数改造前在 `openspec/tests/` 引用各 0 次）· **三次变异检查**：让 `_parse_attestation` 接受空白字段 → 2 条失败；让未勾任务正则也匹配已勾 → 1 条失败；去掉 task_references 子集校验 → 1 条失败；三次均随后恢复且工具文件改动行数为 0 · **围栏探针**：确认围栏内 checkbox 被收集，并锁定该行为（2 条）。
- **未执行的检查**: **该缺陷未修**（按偏差 2，超出本 change 授权，交还 owner 裁决）· `_verify_boundary` 的"非祖先"（`non-ancestor`）拒绝路径未单独覆盖——构造它需要"base 是 head 的后代"的三提交拓扑，本轮未做 · `check_code_budgets.py` 未对新增测试文件设预算（测试不在预算表内，符合现状）· 真实模型梯未跑（纯治理测试，不涉及）。

## 交付给 owner 的裁决项

**围栏 checkbox 缺陷**（偏差 2）：`UNCHECKED_TASK_LINE` 是逐行正则，无代码块感知。要么修解析（跳过围栏区间），要么明确"tasks.md 内不得出现围栏 checkbox 示例"并在文档里写死。两条锁定测试给出了失败优先点与反转方式。**本 change 未动它。**
