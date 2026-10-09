# Tasks

## 1. Checker rules first (red-green per TDD)

- [x] 1.1 Rename the declaring surface tables in `openspec/governance/check_doc_hygiene.py`: `BACKLOG_ACTIVE_SURFACES` → `("issues", "bugs")`; `BACKLOG_ARCHIVE_SURFACES` → `("_fixed_bugs", "_suspended_bugs", "_settled_issues", "_suspended_issues")`; update the fixture-tree paths in the self-test harness (`plans`/`_closed_plans`/`_suspended_plans` → new names) so `--self-test` stays green on the renamed shape. Verify: `python3 openspec/governance/check_doc_hygiene.py --self-test` exit 0.
- [x] 1.2 Add the hukou rule (red-first): every active card's first 12 lines carry a `状态：` field whose word is in a declared per-zone vocabulary tuple (`issues`: 推敲中/等人拍板; `bugs`: 活跃/待修); red fixture = card without the field + card with an out-of-vocabulary word. Verify: `--self-test` exercises both reds and a green card; exit 0 with fixtures, named violations without.
- [x] 1.3 Add the residency rule (red-first): an active card whose status line declares `毕业门` value `已过` or `可关闭：是` fails, anchored on those fields only; fixtures include the mis-kill negative (a `等人拍板`/`未过` card whose body contains `已交付` language must stay green — DSH-assistant 2026-10-08 regression). Verify: `--self-test` red on both anchors, green on the awaiting-human negative.
- [x] 1.4 Add `_backlog/triggers.md` to `ENTRY_DOCS` (link-resolution + UTF-8/newline coverage; no budget entry). Verify: `--self-test` includes a dangling-link red for the new entry.
- [x] 1.5 Live-run the checker against the real tree and record the true reds (expected: the reborrow card is the first live hukou subject — it is already written in the target form; any unexpected red is fixed on the ledger side, not by weakening the rule). Verify: command + exit codes recorded in the receipt.

## 2. Ledger charter and card template

- [x] 2.1 Rewrite `_backlog/README.md`: 总流程 updated to issues vocabulary; four-way closure-conditions table (做/以后做/不做/结论已在别处, each with what must be left behind); status/graduation vocabulary section; triggers.md discipline section (admit bar, delete bar, scan moments: change-archive closeout / supersede-check before a new card / stage closeouts); step→owner routing table (no methods/ directory); dated 刻意不借 register (no research/ lifecycle, no YAML frontmatter, no YYMMDD names, no 🔒 discipline, `_done/` name kept). Verify: checker exits 0; no stale `plans/` references remain in the file.
- [x] 2.2 Rewrite `issues/README.md` (from `plans/README.md` content): active roster with both-direction consistency in mind, new issue card template (问题与期望结果/当前情况/未决问题/下一步 + 方案与取舍/落地关联/关闭条件, status line with 状态/类型/毕业门/可关闭), closure and suspension ritual pointing at `_settled_issues/` and `_suspended_issues/`. Verify: checker exits 0.
- [x] 2.3 Update `bugs/README.md` (vocabulary gains `待修` → `_suspended_bugs/`), `_done/README.md` (surface names + counters tables), and the two archive index READMEs' relocation notes. Verify: checker exits 0; `--self-test` still 0.

## 3. The rename (one revision, all moves together)

- [x] 3.1 Pre-apply grep receipt: search root docs, `openspec/`, `deep_research_harness/` (excluding `changes/archive/`, `deerflow/`) for `_backlog/plans`, `_closed_plans`, `_suspended_plans`; confirm the hit list equals the planned touchpoints (required-paths.toml, root AGENTS.md, openspec/README.md, two app docs, backlog READMEs). Verify: receipt lists every live reference; zero unexpected hits.
- [x] 3.2 `git mv _backlog/plans _backlog/issues`; `git mv _backlog/_done/_closed_plans _backlog/_done/_settled_issues`; `git mv _backlog/_done/_suspended_plans _backlog/_done/_suspended_issues` (19 card bodies move verbatim; same-depth move, relative links unaffected). Verify: `git status` receipt; checker exits 0 after the moves.
- [x] 3.3 Update `openspec/governance/required-paths.toml` (7 backlog path entries move; `_backlog/triggers.md` added as a required file) and `openspec/governance/check_doc_hygiene.py` marker-allowlist comment path if it names `_closed_plans`. Verify: `python3 openspec/governance/check_project_gate.py --phase plan` exit 0 (structural inventory green).
- [x] 3.4 Re-point the live references: root `AGENTS.md` ledger cell (`plans / bugs` → `issues / bugs`, character-neutral; verify `AGENTS.md` stays within its 2425 ceiling via the budget rule), `openspec/README.md` step-1 label, `deep_research_harness/docs/control-map.md` (2 links), `deep_research_harness/docs/testing-and-evaluation.md` (1 link). Verify: checker link rule exits 0; budget rule exits 0.
- [x] 3.5 Migrate the reborrow card: `git mv` it with the directory (already inside `plans/`), update its 状态行 to record the change destination and confirm its hukou passes the new rule as the first live issue card. Verify: checker exits 0 with the card present in `issues/` roster and disk.

## 4. Trigger index seed

- [x] 4.1 Sweep the 19 archived cards in `_settled_issues/` for deferred verdicts (延后/再议/触发条件/暂不/不修 lines); for each candidate verify against its owner card: one self-encountering observation, live owner, not already consumed, not a "user names it" trigger. Verify: harvest table in the receipt (candidate → keep/drop + reason).
- [x] 4.2 Write `_backlog/triggers.md` with the charter header (nature: 账本 not 章程; no auto-rows; scan moments; delete rules) and the surviving rows (expected: CLS-010 Tier-C items with consumption status recorded, agent-playbook budget-revisit; rejected candidates logged in the charter register). Verify: checker link rule exits 0 (every row's home link resolves).

## 5. Full gate receipt and closeout

- [x] 5.1 Run the canonical receipt sequence and record command + exit code + revision: `python3 openspec/governance/check_doc_hygiene.py` (incl. `--self-test`), `python3 openspec/governance/check_project_gate.py --phase plan` and `--phase closeout`, `make verify`. Verify: all exit 0; receipts written under the change directory per closeout policy.
- [x] 5.2 Prove-it-red spot check on the live tree: temporarily declare the reborrow card `毕业门：已过` → expect the residency rule to name it; revert; expect green. Verify: both exit codes recorded (never committed in the red state).
- [ ] 5.3 Closeout: sync delta spec per policy, `openspec archive adopt-issue-ledger-governance`, ledger ritual (CLS-019 assigned at settle; three-README linkage), and the change's closeout evidence recorded. Verify: archive strict-validate exit 0; `_settled_issues/` index row present; counters updated.

## 6. Methods library (mid-apply user ruling 2026-10-09)

- [x] 6.1 Digest the borrowing source's method bodies (5 core files read in full: elicitation / probes / validation-design / synthesis / issue-to-note) and rewrite 7 methods + navigation README for this repo's context: downstream = `openspec-propose` at the admission boundary, evidence owners = lane table + test-evidence-policy, seam vocabulary = this repo's, research lifecycle replaced by evidence-on-card + `_reference/`. Verify: every repo-specific claim in a method body matches an existing file (links resolve from `_backlog/methods/`).
- [x] 6.2 Register methods in the structural inventory (`required-paths.toml`: `_backlog/methods/README.md` + directory) and the charter (tree, four-gate step 2, routing table through methods, `_` prefix preamble names methods as standing non-work-item area). Verify: `check_doc_hygiene.py` exit 0; `check_project_gate.py --phase plan --change` exit 0.

## 7. `_done/` → `_archived/` (mid-apply user ruling 2026-10-09)

- [x] 7.1 `git mv _backlog/_done _backlog/_archived`; sync the checker's declaring tables (`BACKLOG_UNDERSCORE_DIRS`, `BACKLOG_COUNTERS_FILE`, `_surface_dir` path, allowlist justification) and self-test fixtures (`_archived` trees, `_contiguous_plans` fixture renamed `_contiguous_issues`); `_backlog/.gitignore` → `_archived/_evidence/`; `required-paths.toml` paths. Verify: `--self-test` exit 0; live checker exit 0.
- [x] 7.2 Re-point every live `_done` reference: 8 `_backlog` READMEs, `triggers.md` home links, charter sections, `control-map.md` (2), `testing-and-evaluation.md` (1); frozen card bodies keep historical mentions verbatim. Verify: residual grep over live files zero hits (frozen `archive/` and card bodies excluded by design).

## Deviation Register

- 1.（预算口径修正）proposal/design 称根 `AGENTS.md` 编辑"字符中性"——实际 `plans`→`issues` +1 字符
  （2419→2420，仍在 2425 上限内，无需修剪）。口径修正，非行为偏离。
- 2.（夹具断言自伤）hukou 夹具首版的误杀负例把"unindexed 名册缺行"（另一条规则的正确红）也计入
  误杀断言而假红——收紧为只读 hukou 专属问题后绿。夹具修正，规则本体未动。
- 3.（翻案·范围扩大）原判"不设 `methods/` 目录"被驾驭者推翻（2026-10-09 apply 中："methods 那个
  还是很重要"）——按消化改写落地 7 篇 + 导航（design 决策 7）；章程登记翻案记录。
- 4.（翻案·范围扩大）原判"`_done/` 名字保留"被驾驭者推翻（2026-10-09 apply 中）——更名
  `_archived/`（design 决策 8）；章程登记翻案记录。两条翻案均并进本 change（未 archive，
  同语义域）。

## Delivery Record

- **外部行为**: declaration-layer 行为——账本类别更名（`plans/`→`issues/`、`_done/`→`_archived/`、
  `_closed_plans/`→`_settled_issues/`、`_suspended_plans/`→`_suspended_issues/`）、新增户口/滞留两门禁
  （锚字段，不误杀等人卡）、`triggers.md` 活触发器索引（8 行种子）、`methods/` 方法库（7 篇 + 导航）；
  无应用运行时行为变化。
- **影响面**: `check_doc_hygiene.py`（surface 表更名 + 2 新规则 + 红绿夹具 + `ENTRY_DOCS` 收
  `triggers.md`）；`required-paths.toml`（路径更名 + triggers.md + methods 登记）；
  `openspec/governance/README.md` checker 行补账本面描述；`_backlog` 8 份 README + 章程 +
  `.gitignore` + triggers.md + methods/ 8 文件；根 `AGENTS.md` 1 cell（2420/2425）；
  `openspec/README.md` 1 label；应用 docs 2 文件 3 链接；19 张归档卡 `git mv` 正文零改动。
- **实际跑了什么**（退出码一律直读，无管道；跑于 apply 工作树，HEAD `cbf6984` + 本 change 未提交改动，apply commit 紧随）:
  `check_doc_hygiene.py --self-test` → 0（含户口/滞留/触发器断链红绿夹具与"等人拍板不误杀"负例）；
  `check_doc_hygiene.py` live → 0（更名后全账本面绿）；`check_project_gate.py --phase plan --change` → 0
  （guidance/delta/strict 三组件）；`check_project_gate.py --phase closeout` → 0（六组件各 0）；
  `make verify`（deep_research_harness）→ 0；`openspec validate` → valid；prove-it-red：翻
  `毕业门: 已过` → exit 1 且点名 `issues/2026-10-09-backlog-governance-reborrow.md`，还原 → exit 0
  （红态未提交）。门禁过程真红三例均已修复：`triggers.md` 缺失（ENTRY_DOCS 新条目按设计报红→落盘）、
  `openspec/README.md` 断链（label 改写时误删 `../` 前缀→补回）、tasks.md 缺常设段（gate 报
  Deviation Register/Delivery Register→补齐）；最终残留 grep 由 `.venv` 噪声滤出真残留一处
  （`_reference/README.md` 旧 `plans/` 指向→修正），活文件清零。
- **未执行的检查**: `make smoke`（应用集成梯）——本 change 零应用代码/测试改动，按窄证据政策不整跑；
  CI 远端序列 UNVERIFIED-until-push（仓库惯例）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并实现，驾驭者拍板
  apply（2026-10-09）并中途裁定两条翻案（methods 采纳、`_archived` 更名），维护者对交付负最终责任。
