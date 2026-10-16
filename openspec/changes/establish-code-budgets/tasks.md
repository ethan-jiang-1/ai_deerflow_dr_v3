# Tasks

## 1. Baseline and shared subprocess layer

- [x] 1.1 Record the pre-change baseline: run the governance suite, both doc-hygiene modes, the closeout gate and the architecture checker from the repository root; verify all exit 0 and record the discovered test count (expected 145)
- [x] 1.2 Capture the success-path stdout of every component/standalone checker into `/tmp/dedup-before/` (six files, one per checker); verify each capture is non-empty and each exit code is 0
- [x] 1.3 Capture the failure-path behaviour of the same checkers on a planted-violation tree copy (one planted defect per checker): record each command, exit code and stderr into `/tmp/dedup-before-failure/`; verify every capture is non-empty and every exit code is non-zero, so a later comparison has a failing shape to compare against
- [x] 1.4 Add `openspec/governance/gitio.py` with `run_git(arguments, *, cwd=None, text=True) -> CompletedProcess` that never raises and never interprets the exit code; verify `python3 -c "import sys; sys.path.insert(0, 'openspec/governance'); import gitio; print(gitio.run_git(['rev-parse','--short','HEAD'], cwd='.').stdout.strip())"` prints the current short revision
- [x] 1.5 Switch the six git call sites (`project_architecture_check/gitlink.py`, `check_release_face.py`, `check_proof_receipts.py`, `selected-change-closeout.py`, and the two remaining wrappers found by search) to `gitio.run_git`, keeping each caller's own error handling and return type byte-for-byte in behaviour; verify six success-path captures and the planted failure-path captures are identical to `/tmp/dedup-before*/`

## 2. Shared root resolution

- [x] 2.1 Add `openspec/governance/roots.py` with `resolve_root(argv_value, *, default) -> Path`: argv wins when present, otherwise the caller's default, always resolved; verify with a direct call that a passed value resolves and an absent value returns the supplied default
- [x] 2.2 Switch the five root-resolution variants to `roots.resolve_root`, keeping each caller's own default expression (`parents[2]`, `parents[3]`, `Path.cwd()`, argv-first); verify the six success-path and failure-path captures are still identical, and that `check_ci_governance.py` still exits 0 (its declared command set is unchanged)

## 3. Dead-code removal in the guidance kernel

- [x] 3.1 Delete the eight zero-reference definitions from `change_guidance_kernel.py` (`CompositionSchema`, `ProfileSchema`, `ReviewSchema`, `missing_fields`, `neutrality_issues`, `profile_completeness_issues`, `selected_policies`, `validate_review_table`) and any now-unused imports; verify the module still imports, the governance suite exits 0, and the six checker captures are unchanged
- [x] 3.2 Record the measured reduction: verify `change_guidance_kernel.py` shrank by at least 80 lines and that `grep -c` for each deleted name over `openspec/governance openspec/tests` returns 0

## 4. Three-part manifest loading

- [x] 4.1 Introduce a private frozen `_ManifestParts` value object and split `load_manifest` into `_parse_manifest_document` (TOML document + top-level schema), `_validate_manifest_contract` (all declared-set and cross-field checks, filling the parts object) and `_build_manifest` (assemble `StructureManifest`); verify `load_manifest` drops below 40 lines and the architecture checker exits 0 on the real tree
- [x] 4.2 Plant one defect per validation phase (a bad top-level schema value, an unknown ownership layer, and a missing required path) and verify each still fails with the same violation code and detail text as before the split; restore after each and verify the checker returns to exit 0
- [x] 4.3 Verify the six success-path captures and the architecture checker's planted failure capture are unchanged after the split

## 5. The code-budget gate

- [x] 5.1 Measure the current size of every governance script (total lines and count of functions above the declared length threshold) with a script, and write the `CODE_BUDGETS` declaring table in the new checker using the measured values as ceilings, with the ratchet discipline stated in the table comment; verify every measured file lands at or under its declared ceiling
- [x] 5.2 Add `openspec/governance/check_code_budgets.py`: read the declaring table, measure each managed file, fail loudly naming the file, measured value, ceiling and offending function when over, fail as a missing managed path when absent, and enforce no budget for undeclared files; verify it exits 0 on the real tree
- [x] 5.3 Add the checker's `--self-test`: build a temporary tree with a planted over-limit file and a planted over-length function and verify both are reported; verify the self-test exits 0 on the clean case and that removing either planted defect makes the corresponding assertion fail (planted-negative control)
- [x] 5.4 Add `openspec/tests/governance/test_code_budgets.py` driving the checker's declared table, its over-limit path, its missing-file path and its self-test; verify the governance suite count rises above the 145 baseline and still exits 0

## 6. Wiring, registration and closeout evidence

- [x] 6.1 Wire the new gate into the acceptance path: add the checker step to `.github/workflows/governance.yml`, the same command line to `.githooks/pre-commit`, and synchronise `check_ci_governance.py`'s required-marker and allowed-hook-line declarations; verify `check_ci_governance.py` exits 0 and that removing the workflow step makes it red (then restore)
- [x] 6.2 Register the new paths in `openspec/governance/required-paths.toml` (checker, test, and the two shared modules) and add the checker row to `openspec/governance/README.md`; verify the architecture checker exits 0 and fails loudly when a registered module is briefly moved away
- [ ] 6.3 Sync the capability count **with the archive step** (the count rule enumerates main-spec directories under `openspec/specs/`; the new capability only lands there when the archive syncs the delta, so updating it earlier makes doc-hygiene red): update the root `README.md` status line from 13 to 14 capabilities; verify `check_doc_hygiene.py` exits 0 with the new count and that the old count then fails
- [x] 6.4 Prove the new gate can go red on the real tree: temporarily inflate one managed file past its ceiling, verify the checker exits non-zero naming that file and its measured value, then restore and verify exit 0
- [x] 6.5 Run the full gate set from the repository root (governance suite, both doc-hygiene modes, the new budget checker and its self-test, the closeout gate, the architecture checker, strict validation) and re-run the success-path and failure-path captures; verify every exit code is 0 read directly and that all captures are unchanged from `/tmp/dedup-before*/`
- [x] 6.6 Confirm the untouched surfaces: verify `git diff --stat` shows no changes under `deep_research_harness/` and that the `deerflow/` gitlink is untouched; record the result
- [x] 6.7 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines produced by the runner above

## Deviation Register

- 偏差 1（apply 于步骤 1.3 设计）：失败路径捕获器的输出含临时树绝对路径，随机临时目录会让两次捕获因无关原因不同。**落点**：捕获器改用固定路径 `/tmp/dedup-defect-tree/repo`（每次重建），并先自证"连跑两次逐字相同"才用作判据。
- 偏差 2（apply 于步骤 5.1/6.4 抓到，计数口径）：体积表上限"取采纳时实测值"，但测量发生在同步接入面（6.1）**之前**，而 6.1 给 `check_ci_governance.py` 加了三行声明（189 → 192）——守卫首次真实运行就把这个漂移抓了出来。**裁决依据**：棘轮约束的是"文件变小后再涨回去"；此处文件在采纳测量后确实长过，上限应取最终实测值，否则守卫以一条假规则开场。**落点**：上限改为 192，并把"必须在文件最后一次编辑之后测量"写进表注释。**验证**：真实树 exit 0。
- 偏差 3（apply 于步骤 6.3 发现，时序约束）：任务书要求"根 README 计数 13 → 14"，但 doc-hygiene 的计数规则枚举主干 `openspec/specs/` 目录——新 capability 现在只在 change 的 delta 里，**归档同步时**才成为主干；提前改会让 doc-hygiene 红（实测 `declared 14 ... computed 13`）。**落点**：计数改为与归档同批执行，任务行重写并标注约束；本记录如实记为"暂留 13"。
- 偏差 4（apply 期过程记录）：`load_manifest` 三段式的拼接脚本两次出错——"前缀+尾部"拼接让旧函数桩与新函数体重叠，第二次还误删了新解析函数的体。**落点**：第三次改为单次块替换（精确取 `def load_manifest` 至文件末尾整块换掉）一次成功；教训写入提交信息。另有 `dataclass` 导入遗漏与两次自检夹具路径口径不一致，均由 `py_compile`、导入检查与自检当场抓红。
- none: 除上述四项外无其他设计偏离。ci-governance 声明面与 `test_ci_governance` 夹具的同步属 proposal 已登记的相邻契约，不另记。

## Delivery Record
- **外部行为**: 六个既有 checker 的成功路径与失败路径 stdout/退出码**逐字不变**（各六条捕获，`diff` 全等）· 治理套件 145 → 157 用例且全绿 · **新增**一个体积闸：`check_code_budgets.py` 在真实树 exit 0、`--self-test` exit 0，且能被证明会红 · CI canonical 序列与 pre-commit 各增一步/一行（由 ci-governance 的声明面钉住）· 内核死码 99 行删除后无行为变化 · `load_manifest` 三段式后错误码与文本不变 · 根 README 能力计数暂留 13（新 capability 归档时才进主干，见 6.3）。
- **影响面**: 新增 `check_code_budgets.py` 与其 12 项测试、`gitio.py`、`roots.py`、`specs/code-budgets/spec.md`（归档时成为主干）；改 6 处 git 调用点、5 处根解析点、`change_guidance_kernel.py`（214 → 107）、`project_architecture_check/manifest.py`（356 → 433，`load_manifest` 171 → 4）、`.github/workflows/governance.yml`、`.githooks/pre-commit`、`check_ci_governance.py`（三处声明）、`test_ci_governance.py` 夹具、`required-paths.toml`、`openspec/governance/README.md`；**harness 与 `deerflow/` gitlink 零改动**。
- **实际跑了什么**: 六 checker 成功路径逐字 diff 全等、exit 全 0；六 checker 失败路径（固定路径树上各植一缺陷）逐字 diff 全等、exit 全 1 · 治理套件 exit 0（157 用例）· doc-hygiene plain 与 `--self-test` exit 0 · `check_code_budgets.py` plain 与 `--self-test` exit 0 · closeout gate exit 0 · `check_project_architecture.py` exit 0 · `check_ci_governance.py` exit 0 · `openspec validate establish-code-budgets --strict` exit 0 · 体积闸真实树变红实测：把 `check_project_gate.py` 撑到 267 行 → exit 1 且点名该文件与实测值 → 恢复 exit 0 · ci-governance 变红实测：移走 workflow 中的体积步 → exit 1 点名缺该 marker → 恢复 exit 0 · 登记变红实测：移走已登记的 `gitio.py` → 架构 checker exit 1 → 恢复 exit 0 · 三阶段种植缺陷各自失败且错误码正确 · `git diff --stat -- deep_research_harness/` 为空。
- **未执行的检查**: 远端 CI Governance Gate 未跑（本地领先远端 6 个提交，待阶段 3 归档后一并推送复核）· `make smoke` 未跑（不触 harness 组合面）· 守卫的 hook 实际拦截延迟未单独测量（仅静态声明同步 + 静态检查通过）· 归档后能力计数同步（6.3）与归档动作本身属下一步，不在本记录内。
