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

- [ ] 5.1 Measure the current size of every governance script (total lines and count of functions above the declared length threshold) with a script, and write the `CODE_BUDGETS` declaring table in the new checker using the measured values as ceilings, with the ratchet discipline stated in the table comment; verify every measured file lands at or under its declared ceiling
- [ ] 5.2 Add `openspec/governance/check_code_budgets.py`: read the declaring table, measure each managed file, fail loudly naming the file, measured value, ceiling and offending function when over, fail as a missing managed path when absent, and enforce no budget for undeclared files; verify it exits 0 on the real tree
- [ ] 5.3 Add the checker's `--self-test`: build a temporary tree with a planted over-limit file and a planted over-length function and verify both are reported; verify the self-test exits 0 on the clean case and that removing either planted defect makes the corresponding assertion fail (planted-negative control)
- [ ] 5.4 Add `openspec/tests/governance/test_code_budgets.py` driving the checker's declared table, its over-limit path, its missing-file path and its self-test; verify the governance suite count rises above the 145 baseline and still exits 0

## 6. Wiring, registration and closeout evidence

- [ ] 6.1 Wire the new gate into the acceptance path: add the checker step to `.github/workflows/governance.yml`, the same command line to `.githooks/pre-commit`, and synchronise `check_ci_governance.py`'s required-marker and allowed-hook-line declarations; verify `check_ci_governance.py` exits 0 and that removing the workflow step makes it red (then restore)
- [ ] 6.2 Register the new paths in `openspec/governance/required-paths.toml` (checker, test, and the two shared modules) and add the checker row to `openspec/governance/README.md`; verify the architecture checker exits 0 and fails loudly when a registered module is briefly moved away
- [ ] 6.3 Sync the capability count: update the root `README.md` status line from 13 to 14 capabilities; verify `check_doc_hygiene.py` exits 0 with the new count and would fail with the old one
- [ ] 6.4 Prove the new gate can go red on the real tree: temporarily inflate one managed file past its ceiling, verify the checker exits non-zero naming that file and its measured value, then restore and verify exit 0
- [ ] 6.5 Run the full gate set from the repository root (governance suite, both doc-hygiene modes, the new budget checker and its self-test, the closeout gate, the architecture checker, strict validation) and re-run the success-path and failure-path captures; verify every exit code is 0 read directly and that all captures are unchanged from `/tmp/dedup-before*/`
- [ ] 6.6 Confirm the untouched surfaces: verify `git diff --stat` shows no changes under `deep_research_harness/` and that the `deerflow/` gitlink is untouched; record the result
- [ ] 6.7 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines produced by the runner above

## Deviation Register

- none: 本 change 的边界是"共享底层 + 清偿死码 + 新增体积闸"，三者都不改既有判定语义；若 apply 期间发现某处去重必须改变失败路径才能共享（例如两处包装的错误语义无法在不改行为的前提下共存），按 core 原则记入本表并写明裁决依据与落点，而不是在实现文件里静默决定。

## Delivery Record

- **外部行为**: 待 apply 填写（预期：六个既有 checker 的成功路径与失败路径 stdout/退出码逐字不变；治理套件用例数不减；新增体积闸按实测值全绿且能被证明会红）
- **影响面**: 待 apply 填写（预期：新增 `gitio.py`/`roots.py`/`check_code_budgets.py`/其测试/`specs/code-budgets`；改 kernel 删死码、`manifest.py` 三段式、6 处 git 调用点、5 处根解析、workflow 一步、hook 一行、ci-governance 三处声明、required-paths、governance README、根 README 计数；无 harness 改动、无 spec 语义改动）
- **实际跑了什么**: 待 apply 填写（runner 写下命令、退出码、revision）
- **未执行的检查**: 待 apply 填写
