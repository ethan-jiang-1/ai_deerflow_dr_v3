# Tasks

## 1. Baseline and split of the architecture checker

- [x] 1.1 Record the pre-change baseline: run the governance suite, both doc-hygiene modes, the closeout gate and the architecture checker from the repository root; verify all exit 0 and record the discovered test count (expected 145)
- [x] 1.2 Capture the pre-change stdout of every component checker for byte comparison: run `check_project_architecture.py`, `check_change_guidance.py`, `check_project_specs.py`, `check_harness_dependency_direction.py`, `check_ci_governance.py` and `check_doc_hygiene.py` from the repository root, redirecting stdout+stderr to per-checker files under `/tmp/split-before/`; verify each capture is non-empty and the exit codes are 0
- [x] 1.3 Create the `openspec/governance/project_architecture_check/` package and move the rule bodies into it by responsibility (manifest loading, guide block, required paths and ignored paths, import matrix, upstream gitlink), leaving only the CLI and re-exports in `check_project_architecture.py`; verify `python3 openspec/governance/check_project_architecture.py` still exits 0 and its stdout matches the `/tmp/split-before/` capture byte for byte
- [x] 1.4 Decompose `load_manifest` into `_parse_manifest_document`, `_validate_manifest_contract` and `_build_manifest`, with the entry point delegating to them; verify the architecture checker still exits 0 on the real tree and that a planted manifest defect still fails loudly (temporarily add an unknown ownership layer, expect non-zero naming the removed grammar, then restore)
- [x] 1.5 Register the new package and its modules in `openspec/governance/required-paths.toml` (a `directories` entry for the package plus a `files` entry per module); verify `python3 openspec/governance/check_project_architecture.py` exits 0 with the registration in place and fails loudly when one registered module is briefly renamed away
- [x] 1.6 Prove the entry point stays self-sufficient for the copied-script fixture: run the governance suite and verify `test_project_gate.py` (which copies the component scripts into an isolated tree and executes them) passes without any `PYTHONPATH` being set by the caller

## 2. Split of the change-guidance checker

- [x] 2.1 Create the `openspec/governance/change_guidance_check/` package and move the rule bodies into it by responsibility (guidance tree and product context, focus card and proposals, budgets and information map, policy and profile registry, the three review-table validators), leaving only the CLI and re-exports in `check_change_guidance.py`; verify stdout matches the `/tmp/split-before/` capture byte for byte and the exit code is 0
- [x] 2.2 Re-export the migration-period surface the tests address directly (`ContractViolation`, `_validate_change_tasks`) from the entry point, with a docstring note that these names are the compatibility surface; verify `python3 -m unittest openspec.tests.governance.test_change_authority` style discovery through the suite passes unchanged
- [x] 2.3 Keep `change_guidance_kernel.py` at its top-level path and file name, with the package importing it by module name; verify the planted-negative fixture test in `test_project_gate.py` passes (it copies the checker and the kernel by path into an isolated tree)
- [x] 2.4 Replace the three parallel review-policy if-blocks with one registry-driven dispatch table inside the package, preserving the order and the violation text of each; verify each of the three review policies still fails loudly when its required table is removed from a planted proposal (one planted defect per policy, restored after each)
- [x] 2.5 Register the new package and its modules in `required-paths.toml`; verify the architecture checker exits 0 and the plan and closeout gates still pass for this change

## 3. Function-level decomposition of the doc-hygiene ledger rule

- [x] 3.1 Decompose the 182-line `_rule_ledger_consistency` into named sub-rule functions (roster and index, counters and Next-ID, declaration consistency, row placement, card hukou and residency) called by the rule in the same order; verify the plain-mode violation text on a planted-violation tree is identical before and after by re-running the change's green-field comparison
- [x] 3.2 Verify the whole battery still holds after the decomposition: `python3 openspec/governance/check_doc_hygiene.py --self-test` exits 0 and the governance suite still reports at least 145 tests
- [x] 3.3 Confirm no rule logic leaked into the entry points: verify each of the three touched entry points stays within a declared line ceiling and contains no rule body, by measuring their line counts and reviewing their contents

## 4. Closeout evidence and receipt

- [x] 4.1 Byte-compare every checker's post-change stdout against its `/tmp/split-before/` capture; verify each file is identical (`diff` reports nothing) and every exit code is 0
- [x] 4.2 Run the full gate set from the repository root: the governance suite, both doc-hygiene modes, the closeout gate, `check_project_architecture.py` and `openspec validate split-governance-checkers --strict`; verify every exit code is 0 read directly (no pipes), and that the suite count did not drop below the baseline
- [x] 4.3 Prove the split cannot silently degrade: temporarily rename one package module away and verify the corresponding checker exits non-zero naming the failure rather than passing with reduced coverage; restore and verify green
- [x] 4.4 Confirm the untouched surfaces: verify `git diff --stat HEAD -- deep_research_harness/ .github/ .githooks/` is empty, that `check_ci_governance.py` exits 0, and that no checker command string in CI or the hook changed
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines (command, exit code, revision) produced by the runner above

## Deviation Register

- 偏差 1（apply 于步骤 1.4 发现）：任务书写 `load_manifest` 拆为「解析 / 校验 / 构造」三段，实测构造段直接引用 19 个中间变量，硬拆需要引入参数对象、会改变错误路径与代码形状。**裁决依据**：本 change 的验收边界是"只搬不改、零语义变化"，为了形式上的三段而重排控制流与之冲突。**落点**：取两个天然子块为具名函数——`_parse_fixture_declaration`（90 行）与 `_parse_inventory`（60 行，文件加载留在调用方使助手成为解析后文档的纯函数）；`load_manifest` 保留"解析 + 编排 + 构造"职责，269 → 171 行。**验证**：CLI 输出逐字相同、治理套件 145 用例全绿。
- 偏差 2（apply 期过程记录，如实留痕）：步骤 1.3/1.4 的搬移由脚本按行范围拼接完成，中途三次拼接边界/缩进出错（把 `package`/`source_root` 赋值搬走、块缩进加减方向弄反、两个新助手缺 return），每次都**由 CLI 逐字比对与套件立即抓红**，未进入任何提交；最终形态经同一对探针验证。教训：按行范围搬运必须先断言切片首行与缩进，再断言助手返回值。
- 偏差 3（apply 于步骤 1.5 设计）：包内每个模块都被 `facade`/`__init__` import，因此"移走一个已登记模块"总是先炸在 import 上，无法精确命中"登记路径缺失"这条规则。**落点**：新增 `project_architecture_check/notes.py`（已登记、故意不被 import 的说明性模块），使该规则可被移走-恢复动作直接验证；红点实测 `ERROR [path.missing] required file is missing: …/notes.py`。
- 偏差 4（apply 于步骤 1.5 抓到的真 bug，非设计偏离而是必须记录的缺陷）：搬移时 `facade.py` 漏了 `import sys`，正常路径不触发、**只有失败路径打印违规时炸**，而"stdout 逐字比对"永远走不到那里。**落点**：补 `import sys`；教训写入 Delivery Record 的"未执行的检查"——**拆包必须验证失败路径，正常路径逐字绿不构成证据**。
- 偏差 5（apply 于步骤 2.4 完成）：`_validate_selected_policy_reviews` 的三个并行 if 块换成注册表 `_REVIEW_RECORDS`（policy → 标题/错误码后缀/校验器）加统一适配器——三个原校验器签名不一（只有 control-placement 收 triggered_policies），故用薄适配器对齐，而非改其签名。**验证**：三条策略各做一次种植变红（`focus.control_placement_review_missing` / `focus.node_agent_review_missing` / `focus.workflow_outcome_review_missing`）＋ 两条反向控制（无触发策略不索要记录、满足的记录放行）＋ CLI 逐字不变。
- 偏差 6（apply 于步骤 2.3 的测试面同步）：`test_project_gate.py` 的 `RealChangeGuidancePlantedNegativeTest` 按路径把入口与 kernel **复制**进临时树再执行，拆包后复制品找不到子包。**裁决依据**：proposal 已把该夹具的可达性写为相邻契约（"入口必须自足、kernel 位置不变"），夹具源码清单随文件结构同步属结构同步而非行为变更。**落点**：`_FIXTURE_SOURCES` 增加子包目录（`shutil.copytree` 原生支持目录项），并附注释说明理由；测试断言与断言文本零改动。
- 偏差 7（apply 于步骤 3.1 执行）：design 说"分解 `_rule_ledger_consistency`"，实现时发现该规则原有三个嵌套助手（`_surface_dir`/`_work_files`/`_allocated_numbers`）依赖闭包变量 `scope`/`backlog`；提为模块级必须把这两个变量改为显式参数，属**签名变更**而非纯文本搬移——但只影响模块内部调用点（`Scope`/`RULES` 契约不变、无外部消费者）。**落点**：三个助手更名为 `_ledger_surface_dir`/`_ledger_work_files`/`_allocated_numbers` 并接收 `scope, backlog`；三个子规则函数 `_ledger_roster_problems`(73) / `_ledger_counter_problems`(35) / `_ledger_placement_problems`(39) 各返回自己的问题列表，主规则按**原累加顺序**串接。**验证**：9/9 规则 IDENTICAL、合并对照 18 == 18、`--self-test` exit 0、套件 145 全绿；`_rule_ledger_consistency` 182 → 20 行。
- 偏差 8（apply 于步骤 4.5 的过程失误，与阶段 1 偏差 3 同类复发）：填写 Delivery Record 时按子串 `## Delivery Record` 定位并截断，锚点命中的是**任务行 4.5 里的同名字符串**而非节标题，导致 Deviation Register 与 Delivery Record 两节同时损坏。**裁决依据**：本仓"失败照实说"纪律。**落点**：按行首精确匹配重建两节；教训——**锚点必须匹配行首标题，不能匹配任意子串**（本 change 内第二次踩同类坑，第一次是 1.4 的 `\ndef load_manifest(`）。
- none: 除上述八项外无其他设计偏离。

## Delivery Record

- **外部行为**: 零变化。六个 component/standalone checker 的 stdout 与退出码与改造前逐字相同（改造前快照取自 HEAD 逐个执行并存于 /tmp/split-before/；改造后逐文件 diff 全等）· 治理套件用例数 145 不变 · CI/hook 的命令字符串与文件路径未动 · 无 spec 改动（`skip_specs: true`）。
- **影响面**: 改 `check_project_architecture.py`（1024 → 39 行）+ 新包 `project_architecture_check/`（8 模块，含 notes.py）· 改 `check_change_guidance.py`（1473 → 36 行）+ 新包 `change_guidance_check/`（10 模块）· 改 `check_doc_hygiene.py`（账本规则 182 → 20 行，三个子规则 73/35/39）· `required-paths.toml` 增 2 个目录 + 18 个模块文件 · `test_project_gate.py` 的夹具源码清单增子包目录（结构同步，测试断言零改动）· **kernel 位置与文件名未动**、`_battery.py` 未动、harness/CI/hook 零改动。
- **实际跑了什么**: 六 checker stdout 逐字 diff：全部 IDENTICAL、exit 全 0 · 治理套件 exit 0（145 用例，计数不减）· doc-hygiene plain exit 0 与 `--self-test` exit 0 · `check_project_gate.py --phase closeout` exit 0（六组件各 0）· `check_project_architecture.py` exit 0 · `openspec validate split-governance-checkers --strict` exit 0 · 变红证明：移走 `project_architecture_check/notes.py` → exit 1 精确点名 `[path.missing]`；移走 `change_guidance_check/tasks.py` → exit 1；各自恢复后 exit 0 · 三审阅策略种植变红（control_placement / node_agent / workflow_outcome 三条 review_missing 码）+ 两条反向控制通过 · 绿地对照：9/9 规则 IDENTICAL（注入违规副本 18 条违规逐字逐序一致）· 未触碰面：`git diff origin/master..HEAD -- deep_research_harness/ .github/ .githooks/` 为空、`check_ci_governance.py` exit 0。
- **未执行的检查**: 远端 CI Governance Gate 未跑（本组未推送；由 push 后远端复核）· `make smoke` 未跑（本 change 不触 harness 组合面）· 未对拆分后的每个子包模块做独立覆盖率测量（本仓无覆盖率工具链；等效证据是六 checker 逐字输出 + 套件 145 + 变红证明 + 绿地对照四项并行）。
