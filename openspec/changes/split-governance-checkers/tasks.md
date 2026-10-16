# Tasks

## 1. Baseline and split of the architecture checker

- [x] 1.1 Record the pre-change baseline: run the governance suite, both doc-hygiene modes, the closeout gate and the architecture checker from the repository root; verify all exit 0 and record the discovered test count (expected 145)
- [x] 1.2 Capture the pre-change stdout of every component checker for byte comparison: run `check_project_architecture.py`, `check_change_guidance.py`, `check_project_specs.py`, `check_harness_dependency_direction.py`, `check_ci_governance.py` and `check_doc_hygiene.py` from the repository root, redirecting stdout+stderr to per-checker files under `/tmp/split-before/`; verify each capture is non-empty and the exit codes are 0
- [x] 1.3 Create the `openspec/governance/project_architecture_check/` package and move the rule bodies into it by responsibility (manifest loading, guide block, required paths and ignored paths, import matrix, upstream gitlink), leaving only the CLI and re-exports in `check_project_architecture.py`; verify `python3 openspec/governance/check_project_architecture.py` still exits 0 and its stdout matches the `/tmp/split-before/` capture byte for byte
- [x] 1.4 Decompose `load_manifest` into `_parse_manifest_document`, `_validate_manifest_contract` and `_build_manifest`, with the entry point delegating to them; verify the architecture checker still exits 0 on the real tree and that a planted manifest defect still fails loudly (temporarily add an unknown ownership layer, expect non-zero naming the removed grammar, then restore)
- [x] 1.5 Register the new package and its modules in `openspec/governance/required-paths.toml` (a `directories` entry for the package plus a `files` entry per module); verify `python3 openspec/governance/check_project_architecture.py` exits 0 with the registration in place and fails loudly when one registered module is briefly renamed away
- [x] 1.6 Prove the entry point stays self-sufficient for the copied-script fixture: run the governance suite and verify `test_project_gate.py` (which copies the component scripts into an isolated tree and executes them) passes without any `PYTHONPATH` being set by the caller

## 2. Split of the change-guidance checker

- [ ] 2.1 Create the `openspec/governance/change_guidance_check/` package and move the rule bodies into it by responsibility (guidance tree and product context, focus card and proposals, budgets and information map, policy and profile registry, the three review-table validators), leaving only the CLI and re-exports in `check_change_guidance.py`; verify stdout matches the `/tmp/split-before/` capture byte for byte and the exit code is 0
- [ ] 2.2 Re-export the migration-period surface the tests address directly (`ContractViolation`, `_validate_change_tasks`) from the entry point, with a docstring note that these names are the compatibility surface; verify `python3 -m unittest openspec.tests.governance.test_change_authority` style discovery through the suite passes unchanged
- [ ] 2.3 Keep `change_guidance_kernel.py` at its top-level path and file name, with the package importing it by module name; verify the planted-negative fixture test in `test_project_gate.py` passes (it copies the checker and the kernel by path into an isolated tree)
- [ ] 2.4 Replace the three parallel review-policy if-blocks with one registry-driven dispatch table inside the package, preserving the order and the violation text of each; verify each of the three review policies still fails loudly when its required table is removed from a planted proposal (one planted defect per policy, restored after each)
- [ ] 2.5 Register the new package and its modules in `required-paths.toml`; verify the architecture checker exits 0 and the plan and closeout gates still pass for this change

## 3. Function-level decomposition of the doc-hygiene ledger rule

- [ ] 3.1 Decompose the 182-line `_rule_ledger_consistency` into named sub-rule functions (roster and index, counters and Next-ID, declaration consistency, row placement, card hukou and residency) called by the rule in the same order; verify the plain-mode violation text on a planted-violation tree is identical before and after by re-running the change's green-field comparison
- [ ] 3.2 Verify the whole battery still holds after the decomposition: `python3 openspec/governance/check_doc_hygiene.py --self-test` exits 0 and the governance suite still reports at least 145 tests
- [ ] 3.3 Confirm no rule logic leaked into the entry points: verify each of the three touched entry points stays within a declared line ceiling and contains no rule body, by measuring their line counts and reviewing their contents

## 4. Closeout evidence and receipt

- [ ] 4.1 Byte-compare every checker's post-change stdout against its `/tmp/split-before/` capture; verify each file is identical (`diff` reports nothing) and every exit code is 0
- [ ] 4.2 Run the full gate set from the repository root: the governance suite, both doc-hygiene modes, the closeout gate, `check_project_architecture.py` and `openspec validate split-governance-checkers --strict`; verify every exit code is 0 read directly (no pipes), and that the suite count did not drop below the baseline
- [ ] 4.3 Prove the split cannot silently degrade: temporarily rename one package module away and verify the corresponding checker exits non-zero naming the failure rather than passing with reduced coverage; restore and verify green
- [ ] 4.4 Confirm the untouched surfaces: verify `git diff --stat HEAD -- deep_research_harness/ .github/ .githooks/` is empty, that `check_ci_governance.py` exits 0, and that no checker command string in CI or the hook changed
- [ ] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines (command, exit code, revision) produced by the runner above

## Deviation Register

- 偏差 1（apply 于步骤 1.4 发现）：任务书写 `load_manifest` 拆为「解析 / 校验 / 构造」三段，实测构造段直接引用 19 个中间变量，硬拆需要引入参数对象、会改变错误路径与代码形状。**裁决依据**：本 change 的验收边界是"只搬不改、零语义变化"，为了形式上的三段而重排控制流与之冲突。**落点**：取两个天然子块为具名函数——`_parse_fixture_declaration`（fixture 声明校验，最长子块）与 `_parse_inventory`（清单校验+摊平，并把文件加载留在调用方，使助手成为解析后文档的纯函数）；`load_manifest` 保留"解析 + 编排 + 构造"的职责，269 → 171 行。**验证**：CLI 输出逐字相同、治理套件 145 用例全绿。
- 偏差 2（apply 期过程记录，如实留痕）：步骤 1.3/1.4 的搬移由脚本按行范围拼接完成，中途三次拼接边界/缩进出错（把 `package`/`source_root` 赋值搬走、块缩进加减方向弄反、两个新助手缺 return），每次都**由 CLI 逐字比对与套件立即抓红**，未进入任何提交；最终形态经同一对探针验证。教训：按行范围搬运必须先断言切片首行与缩进，再断言助手返回值。
- 偏差 3（apply 于步骤 1.5 设计）：包内每个模块都被 `facade`/`__init__` import，因此"移走一个已登记模块"总是先炸在 import 上，无法精确命中"登记路径缺失"这条规则。**落点**：新增 `project_architecture_check/notes.py`（已登记、故意不被 import 的说明性模块），使该规则可被移走-恢复动作直接验证；红点实测 `ERROR [path.missing] required file is missing: …/notes.py`。
- 偏差 4（apply 于步骤 1.5 抓到的真 bug，非设计偏离而是必须记录的缺陷）：搬移时 `facade.py` 漏了 `import sys`，正常路径不触发、**只有失败路径打印违规时炸**，而"stdout 逐字比对"永远走不到那里。**落点**：补 `import sys`；教训写入下方"未执行的检查"——**拆包必须验证失败路径，正常路径逐字绿不构成证据**。
- none: 除上述四项外无其他设计偏离；若后续步骤再发现须偏离，按 core 原则追加条目并写明裁决依据与落点。

## Delivery Record

- **外部行为**: 待 apply 填写（预期：零变化——每个 checker 的 stdout 与退出码逐字不变；治理套件用例数不减于 145）
- **影响面**: 待 apply 填写（预期：两个 checker 改薄入口 + 两个新子包 + `check_doc_hygiene.py` 内部分解 + `required-paths.toml` 登记 + 两份治理文档；无 spec 改动、无 harness/CI/hook 改动、kernel 位置不变）
- **实际跑了什么**: 待 apply 填写（runner 写下命令、退出码、revision）
- **未执行的检查**: 待 apply 填写
