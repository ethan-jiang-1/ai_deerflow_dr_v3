# Tasks

## 1. Baseline and scope extraction (no behavior change)

- [x] 1.1 Record the pre-change baseline on the current revision: run `python3 -m unittest discover -s openspec/tests/governance -q`, `python3 openspec/governance/check_doc_hygiene.py --self-test`, `python3 openspec/governance/check_doc_hygiene.py`, and `python3 openspec/governance/check_project_gate.py --phase closeout`; verify all four exit 0 and record the discovered test count (expected 99 methods)
- [x] 1.2 Capture the 31 negative-control identifiers verbatim before touching the file: `grep -oE 'errors\.append\("self-test: [^"]*"' openspec/governance/check_doc_hygiene.py | sort > /tmp/self-test-assertions.before.txt`; verify the file holds exactly 31 unique lines
- [x] 1.3 Introduce the frozen `Scope` value object carrying `root` plus the declared tables (`ENTRY_DOCS`, `DOC_LAYER_DOCS`, `LINKED_ASSET_DOCS`, `DOC_BUDGETS`, `BACKLOG_UNDERSCORE_DIRS`, `BACKLOG_STATUS_VOCABULARY`, `STALE_MARKER_FILES`, `MARKER_ALLOWLIST`, `BACKLOG_ROOT`, `DOCS_TREE`, `ADR_DIR`, `ADR_INDEX`); verify `python3 openspec/governance/check_doc_hygiene.py` still exits 0 on the real tree
- [x] 1.4 Switch every `_rule_*` callable to the uniform `check(scope) -> list[str]` signature and pass `MARKER_ALLOWLIST` into `_rule_stale_markers` as an argument instead of reading it as a module global; verify the plain-mode violation text is byte-identical to the pre-change run on the real tree
- [x] 1.5 Replace the hand-listed dispatch in `violations()` with a frozen `RULES` tuple iterated in the same order; verify a green run of `python3 openspec/governance/check_doc_hygiene.py` and that `--self-test` still exits 0 (the inlined battery body is untouched at this step)

## 2. Per-rule green-field comparison (proves zero semantic change)

- [x] 2.1 Author the comparison harness: for one temporary tree, run the pre-change rule implementation (from `git show HEAD:openspec/governance/check_doc_hygiene.py` loaded via `importlib`) and the post-change rule, then diff their returned violation lists; verify the harness reports zero differences for `_rule_adr_index`
- [x] 2.2 Extend the comparison to `_rule_links` and `_rule_encoding_newline`; verify zero differences on the same tree
- [x] 2.3 Extend the comparison to `_rule_docs_scope`, `_rule_backlog_underscore`, and `_rule_doc_budgets`; verify zero differences
- [x] 2.4 Extend the comparison to `_rule_ledger_consistency`, `_rule_root_counts`, and `_rule_stale_markers`; verify zero differences and that the stale-marker comparison holds with the allowlist passed as an argument

## 3. Battery extraction into `_battery.py`

- [x] 3.1 Create `openspec/governance/_battery.py` exporting `NEGATIVE_CASES` (one entry per negative control: owning rule name, temp-tree builder, expected violation substring, one-line note) and the shared fixture builders; verify the module imports cleanly with `python3 -c "import sys; sys.path.insert(0, 'openspec/governance'); import _battery; print(len(_battery.NEGATIVE_CASES))"` printing 31
- [x] 3.2 Migrate all 31 controls into `NEGATIVE_CASES` with their assertion text preserved verbatim; verify every identifier from `/tmp/self-test-assertions.before.txt` still appears in the new module
- [x] 3.3 Keep `--self-test` in `check_doc_hygiene.py` as a thin delegate that iterates `NEGATIVE_CASES` and renders the unchanged stdout (`doc-hygiene self-test passed.` / the failure list on stderr) and the unchanged exit codes; verify `python3 openspec/governance/check_doc_hygiene.py --self-test` exits 0 and prints exactly `doc-hygiene self-test passed.`
- [x] 3.4 Delete the inlined battery body from `check_doc_hygiene.py` (the 442-line `_self_test`) and verify no assertion code remains in the product module: `grep -c 'errors.append("self-test' openspec/governance/check_doc_hygiene.py` returns 0
- [x] 3.5 Verify the product module shrank and the CLI contract survived: record the new line count of `check_doc_hygiene.py` and confirm both `python3 openspec/governance/check_doc_hygiene.py` and its `--self-test` mode exit 0

## 4. Discoverable unittest battery

- [x] 4.1 Add `openspec/tests/governance/test_doc_hygiene.py` that imports `_battery.NEGATIVE_CASES` and the checker's rule callables, groups cases per rule into `TestCase` classes, and generates one test identifier per case (dynamic methods plus `subTest` messages naming the case); verify `python3 -m unittest discover -s openspec/tests/governance -q` exits 0 and reports at least 130 methods (baseline 99 plus 31)
- [x] 4.2 Add the clean-fixture acceptance test (a well-formed temporary tree yields zero violations) and a per-rule targeted negative so every rule carries both directions; verify each new test fails when its guarded rule is stubbed to return an empty list (mutation check) and passes on the real implementation
- [x] 4.3 Add a CLI-contract test that runs `check_doc_hygiene.py --self-test` as a subprocess and asserts exit 0 plus the unchanged stdout line; verify it goes red when `--self-test` is temporarily made to skip one case (planted-failure check), then restore
- [x] 4.4 Confirm the new test file needs no structural registration: verify `python3 openspec/governance/check_project_architecture.py` exits 0 with `required-paths.toml` unchanged

## 5. Documentation sync for the checker's self-description

- [x] 5.1 Update the `check_doc_hygiene.py` row in `openspec/governance/README.md` (line 18) and the standalone-checker note (lines 68-69) to state that the negative battery now runs under the governance discover command and that `--self-test` is its thin delegate entry; verify the standalone/non-gate role statement is preserved verbatim and `python3 openspec/governance/check_doc_hygiene.py` still exits 0 (its own link/scope rules cover this file)
- [x] 5.2 Add the new module and test file to the visible record in the same edit; verify `git status --porcelain=v1 --untracked-files=all` lists exactly `_battery.py`, `test_doc_hygiene.py`, `check_doc_hygiene.py`, `README.md` for this change

## 6. Closeout evidence and receipt

- [x] 6.1 Reconciliation: regenerate the assertion set with `grep -oE 'self-test: [^"]*' openspec/governance/_battery.py | sort -u` and diff it against `/tmp/self-test-assertions.before.txt`; verify both sides hold exactly 31 lines and the diff is empty, otherwise treat the change as failed
- [x] 6.2 Run the governance suite, both doc-hygiene modes, the closeout gate, and the architecture checker from the repository root; verify every exit code is 0 read directly (no pipe swallowing the status), and re-run the per-rule green-field comparison for all nine rules
- [x] 6.3 Prove the extracted battery still fails loudly: in the dedicated reproduction scratchpad, construct one planted violation (an over-budget managed document), run the checker against it, and verify non-zero exit plus the naming violation; record the command, exit code, and output as the receipt
- [x] 6.4 Confirm the harness lane is untouched: verify `git diff --stat HEAD -- deep_research_harness/` reports no changes and that `openspec/governance/check_ci_governance.py` still exits 0 (the CI command set is unchanged)
- [x] 6.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines (command, exit code, revision) produced by the runner above

## Deviation Register

- 偏差 1（apply 于步骤 1.3–1.5 发现）：design 假定内联电池在签名切换后不必改动，实际它是规则的直接调用方——28 处 `_rule_x(<temp-tree>)` 传的是 `Path`，切到 `Scope` 后 `--self-test` 立即红（`AttributeError: 'PosixPath' object has no attribute 'docs'`）。**裁决依据**：任务 1.4 要求规则统一为 `check(scope)`，而"两套签名并存"会让规则重新依赖模块状态，正是本 change 要消除的东西，故不设兼容层。**落点**：在 `_self_test` 顶部加局部适配器 `scope(var) -> Scope.from_defaults(Path(var))`，28 处调用机械改写为 `_rule_x(scope(var))`；该适配器随电池在步骤 3.4 一并删除（已删）。**验证**：改写后 `--self-test` exit 0、31 条断言标识不变、绿地对照（注入违规的真树副本）新旧 18 条违规逐字逐序相同。
- 偏差 2（apply 于步骤 3.2 发现，计数以**测量**为准）：任务书按继承电池的失败消息数写作「31 条负例」，实测为 **30 条负例控制**。测量法：把每条规则打成返回空列表，继承的内联电池与新提取的电池**都报 30 条失败**——即负例控制的真值。原「31」把 `clean fixture must have zero violations` 这条**正向控制**算进了负例。提取时另有 6 条原本混在负例里的「不该误报」断言被显式建模为绿色控制（`absent`）。**落点**：`_battery.py` 的 `NegativeCase.present/absent/zero_violations` 三态 + `tests/governance/test_doc_hygiene.py::BatteryInventoryTests` 把 30/9/39 钉死并写明测量依据；本任务书相关行的「31」保留原文不改，以免抹掉计划的原始口径。
- 偏差 3（apply 于步骤 6.5 引入，归档时由 closeout gate 抓出）：填写 `## Delivery Record` 时用"截断到文件末尾"的写法，把位于其**之前**的 `## Deviation Register` 一节连带删除，且当时未停下核对 closeout gate 的非零退出码就继续执行了归档。**裁决依据**：本仓「未执行的检查/失败照实说」纪律——门禁红了必须停下看全量输出，不能只看尾部。**落点**：本节的恢复 + `## Delivery Record` 的 `未执行的检查` 已如实记入该事件。**验证**：恢复后 `check_project_gate.py --phase closeout` exit 0（复现方式：把归档工件临时放回 `openspec/changes/` 下跑一次全量门禁，红点为 `[tasks.deviation_register_missing]`；修复后该组件 exit 0）。
- none: 除上述三项外无其他设计偏离。

## Delivery Record

- **外部行为**: 零变化。`check_doc_hygiene.py` 的 plain 模式与 `--self-test` 模式对同一棵树
  的 stdout 与退出码与改造前逐字相同（改造前参照为本仓 HEAD 抽出的
  `/tmp/check_doc_hygiene.BEFORE.py`，两版对真实树同时 exit 0 且输出一致）；9 条规则的违规
  文本与顺序在注入违规的副本上逐规则相同（9/9 IDENTICAL，18 条合并违规逐字逐序一致）。
  唯一有意行为变化：31 条负例断言从"只有 `--self-test` 一条通道"变为"治理套件
  `unittest discover` 也能跑到"——治理套件用例数 99 → 145（新增 46：39 条控制各一例 +
  7 条盘点/夹具/CLI 契约用例）。
- **影响面**: 改 `openspec/governance/check_doc_hygiene.py`（1199 → 863 行；Scope + RULES
  注册表 + 薄委托；删除 450 行内联电池）；新增 `openspec/governance/_battery.py`（39 条控制）；
  新增 `openspec/tests/governance/test_doc_hygiene.py`；改 `openspec/governance/README.md`
  （68-72 行自述：负例电池位置与双入口）。**无新增登记路径、无 spec 改动、无 harness 改动、
  无 CI/hook 改动**（命令字符串与文件路径均不变）。
- **实际跑了什么**: rev `ca748d8`（工作树未提交）；退出码一律直测，无管道：
  - `python3 -m unittest discover -s openspec/tests/governance -q` → exit 0（145 用例）
  - `python3 openspec/governance/check_doc_hygiene.py --self-test` → exit 0
  - `python3 openspec/governance/check_doc_hygiene.py` → exit 0
  - `python3 openspec/governance/check_project_gate.py --phase closeout` → exit 0
  - `python3 openspec/governance/check_project_architecture.py` → exit 0
  - `openspec validate extract-doc-hygiene-test-battery --strict` → exit 0
  - 逐规则绿地对照（注入违规副本，旧实现 vs 新实现）→ 9/9 IDENTICAL，exit 0
  - 合并产出对照 → 18 == 18 逐字相同，exit 0
  - 守卫变红实测（种入超预算受管文档）→ exit 1，输出指名
    `resident document over character budget: deep_research_harness/AGENTS.md (26345 > 6344)`
  - 变异法测控制盘点（规则全打空转）→ 新旧电池**都报 30 条失败**，即负例控制真值
  - `git diff --stat HEAD -- deep_research_harness/` → 空（harness 零改动）
  - harness：`UV_OFFLINE=1 make verify` → exit 0（251 tests）；ruff lint → exit 0
  - `python3 openspec/governance/check_ci_governance.py` → exit 0
- **未执行的检查**: CI 远端 Governance Gate 与 `make smoke` 未跑（本 change 不触框架组合面，
  且 `make smoke` 需 `uv sync`；CI 触发路径含 `openspec/**`，由 push 后远端复核）；
  真实模型/凭据车道（本 change 与认知面无关）；无凭据外推项。
