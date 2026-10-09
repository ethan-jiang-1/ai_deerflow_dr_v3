# Tasks

## 1. Checker rules first (red-green per TDD)

- [ ] 1.1 Rename the declaring surface tables in `openspec/governance/check_doc_hygiene.py`: `BACKLOG_ACTIVE_SURFACES` → `("issues", "bugs")`; `BACKLOG_ARCHIVE_SURFACES` → `("_fixed_bugs", "_suspended_bugs", "_settled_issues", "_suspended_issues")`; update the fixture-tree paths in the self-test harness (`plans`/`_closed_plans`/`_suspended_plans` → new names) so `--self-test` stays green on the renamed shape. Verify: `python3 openspec/governance/check_doc_hygiene.py --self-test` exit 0.
- [ ] 1.2 Add the hukou rule (red-first): every active card's first 12 lines carry a `状态：` field whose word is in a declared per-zone vocabulary tuple (`issues`: 推敲中/等人拍板; `bugs`: 活跃/待修); red fixture = card without the field + card with an out-of-vocabulary word. Verify: `--self-test` exercises both reds and a green card; exit 0 with fixtures, named violations without.
- [ ] 1.3 Add the residency rule (red-first): an active card whose status line declares `毕业门` value `已过` or `可关闭：是` fails, anchored on those fields only; fixtures include the mis-kill negative (a `等人拍板`/`未过` card whose body contains `已交付` language must stay green — DSH-assistant 2026-10-08 regression). Verify: `--self-test` red on both anchors, green on the awaiting-human negative.
- [ ] 1.4 Add `_backlog/triggers.md` to `ENTRY_DOCS` (link-resolution + UTF-8/newline coverage; no budget entry). Verify: `--self-test` includes a dangling-link red for the new entry.
- [ ] 1.5 Live-run the checker against the real tree and record the true reds (expected: the reborrow card is the first live hukou subject — it is already written in the target form; any unexpected red is fixed on the ledger side, not by weakening the rule). Verify: command + exit codes recorded in the receipt.

## 2. Ledger charter and card template

- [ ] 2.1 Rewrite `_backlog/README.md`: 总流程 updated to issues vocabulary; four-way closure-conditions table (做/以后做/不做/结论已在别处, each with what must be left behind); status/graduation vocabulary section; triggers.md discipline section (admit bar, delete bar, scan moments: change-archive closeout / supersede-check before a new card / stage closeouts); step→owner routing table (no methods/ directory); dated 刻意不借 register (no research/ lifecycle, no YAML frontmatter, no YYMMDD names, no 🔒 discipline, `_done/` name kept). Verify: checker exits 0; no stale `plans/` references remain in the file.
- [ ] 2.2 Rewrite `issues/README.md` (from `plans/README.md` content): active roster with both-direction consistency in mind, new issue card template (问题与期望结果/当前情况/未决问题/下一步 + 方案与取舍/落地关联/关闭条件, status line with 状态/类型/毕业门/可关闭), closure and suspension ritual pointing at `_settled_issues/` and `_suspended_issues/`. Verify: checker exits 0.
- [ ] 2.3 Update `bugs/README.md` (vocabulary gains `待修` → `_suspended_bugs/`), `_done/README.md` (surface names + counters tables), and the two archive index READMEs' relocation notes. Verify: checker exits 0; `--self-test` still 0.

## 3. The rename (one revision, all moves together)

- [ ] 3.1 Pre-apply grep receipt: search root docs, `openspec/`, `deep_research_harness/` (excluding `changes/archive/`, `deerflow/`) for `_backlog/plans`, `_closed_plans`, `_suspended_plans`; confirm the hit list equals the planned touchpoints (required-paths.toml, root AGENTS.md, openspec/README.md, two app docs, backlog READMEs). Verify: receipt lists every live reference; zero unexpected hits.
- [ ] 3.2 `git mv _backlog/plans _backlog/issues`; `git mv _backlog/_done/_closed_plans _backlog/_done/_settled_issues`; `git mv _backlog/_done/_suspended_plans _backlog/_done/_suspended_issues` (19 card bodies move verbatim; same-depth move, relative links unaffected). Verify: `git status` receipt; checker exits 0 after the moves.
- [ ] 3.3 Update `openspec/governance/required-paths.toml` (7 backlog path entries move; `_backlog/triggers.md` added as a required file) and `openspec/governance/check_doc_hygiene.py` marker-allowlist comment path if it names `_closed_plans`. Verify: `python3 openspec/governance/check_project_gate.py --phase plan` exit 0 (structural inventory green).
- [ ] 3.4 Re-point the live references: root `AGENTS.md` ledger cell (`plans / bugs` → `issues / bugs`, character-neutral; verify `AGENTS.md` stays within its 2425 ceiling via the budget rule), `openspec/README.md` step-1 label, `deep_research_harness/docs/control-map.md` (2 links), `deep_research_harness/docs/testing-and-evaluation.md` (1 link). Verify: checker link rule exits 0; budget rule exits 0.
- [ ] 3.5 Migrate the reborrow card: `git mv` it with the directory (already inside `plans/`), update its 状态行 to record the change destination and confirm its hukou passes the new rule as the first live issue card. Verify: checker exits 0 with the card present in `issues/` roster and disk.

## 4. Trigger index seed

- [ ] 4.1 Sweep the 19 archived cards in `_settled_issues/` for deferred verdicts (延后/再议/触发条件/暂不/不修 lines); for each candidate verify against its owner card: one self-encountering observation, live owner, not already consumed, not a "user names it" trigger. Verify: harvest table in the receipt (candidate → keep/drop + reason).
- [ ] 4.2 Write `_backlog/triggers.md` with the charter header (nature: 账本 not 章程; no auto-rows; scan moments; delete rules) and the surviving rows (expected: CLS-010 Tier-C items with consumption status recorded, agent-playbook budget-revisit; rejected candidates logged in the charter register). Verify: checker link rule exits 0 (every row's home link resolves).

## 5. Full gate receipt and closeout

- [ ] 5.1 Run the canonical receipt sequence and record command + exit code + revision: `python3 openspec/governance/check_doc_hygiene.py` (incl. `--self-test`), `python3 openspec/governance/check_project_gate.py --phase plan` and `--phase closeout`, `make verify`. Verify: all exit 0; receipts written under the change directory per closeout policy.
- [ ] 5.2 Prove-it-red spot check on the live tree: temporarily declare the reborrow card `毕业门：已过` → expect the residency rule to name it; revert; expect green. Verify: both exit codes recorded (never committed in the red state).
- [ ] 5.3 Closeout: sync delta spec per policy, `openspec archive adopt-issue-ledger-governance`, ledger ritual (CLS-019 assigned at settle; three-README linkage), and the change's closeout evidence recorded. Verify: archive strict-validate exit 0; `_settled_issues/` index row present; counters updated.
