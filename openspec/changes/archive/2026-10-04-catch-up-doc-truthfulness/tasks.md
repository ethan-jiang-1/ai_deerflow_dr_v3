# Tasks

## 1. Registry scaffold

- [x] 1.1 Verify the audit plan's B6 pin claim against `openspec/tests/governance/test_upstream_pin_agreement.py` and record the finding in this change's notes; verify `git grep -n "CURRENT_DEERFLOW_PIN" deep_research_harness/src` outcome is recorded either way

## 2. Guard red (TDD red for both rules)

- [x] 2.1 Add declaring tables to `check_doc_hygiene.py`: `STALE_MARKER_FILES`, `STALE_MARKERS`, `MARKER_ALLOWLIST` (with the `agents/__init__.py` "(skeleton)" justification entry), plus the ledger surfaces list; verify the tables are present and commented per the DOC_BUDGETS discipline
- [x] 2.2 Add negative-control fixtures + assertions for ledger consistency (unindexed file, dangling row, count drift, Next-ID drift) and stale markers (marker present, unjustified allowlist, dangling allowlist) to `_self_test()`; verify `python3 openspec/governance/check_doc_hygiene.py --self-test` FAILS (rules do not exist yet) and record the red receipt

## 3. Guard green on fixtures

- [x] 3.1 Implement `_rule_ledger_consistency` and `_rule_stale_markers`; verify `--self-test` exits 0 and record the green receipt
- [x] 3.2 Verify the live tree is still red for both rules (missing CLS-008/009 rows; live markers) and record both messages as the second red receipt

## 4. Ledger repair (turns rule 1 live-green)

- [x] 4.1 Add CLS-008/009 rows to `_backlog/plans/README.md` archived table; de-fragment the `_closed_plans/README.md` and `known-limitations.md` tables (remove blank lines inside tables); bump stale "最后更新" headers (`_closed_plans`, `_reference`); verify `--self-test` 0 and the ledger-rule live violations are gone (checker output names none)
- [x] 4.2 Restore the consumption-status index to `_backlog/_reference/README.md` (six materials ↔ landed products CLS-004..010 mapping, including test-strategy/ fully consumed by CLS-010); verify the index renders and links resolve

## 5. Root layer catch-up

- [x] 5.1 Rewrite `README.md` status paragraph (A1), fix the `_reference/deerflow/` link (B1), drop "boundary plan above" (B2), correct specs/changes claims and plan pointers (B5, A6), rewrite the make targets block (A3), and resolve B6 per task 1.1 (present-tense pin statement); verify: each claim's before/after `git grep` receipt recorded, `check_doc_hygiene.py` exit 0, `check_release_face.py` exit 0
- [x] 5.2 Update root `AGENTS.md`: drop "骨架期占位"/"骨架期" qualifiers (A2, B5), add the `CONTEXT-MAP.md` routing row paid for by equal deletions (C2); verify file ≤ 2500 chars and checker exit 0
- [x] 5.3 Rewrite `CONTEXT-MAP.md` reading order to defer to `AGENTS.md` and stop routing through the empty plans list (C1); verify the three context links resolve

## 6. Harness layer catch-up

- [x] 6.1 Fix `docs/README.md` (delete duplicate known-limitations row A5, refresh "骨架期" header and ⬜ markers B7) and `tests/README.md` (B7, C6 empty contract dir); verify checker exit 0
- [x] 6.2 Rewrite `docs/local-operations.md` (A4: real command set, no false "不承载验证承诺") and `docs/runtime-architecture.md` (B3: real boundary summary, drop dead "boundary plan" pointer, mark `mixed` declared-but-unwired per pending decision B4); verify checker exit 0 and all claims cross-checked against Makefile/cli.py
- [x] 6.3 Update harness `AGENTS.md` (A8: delete three future-tense clauses; C4 gate gloss; C5 lane-separation note), `COMMANDS.md` (A8 install line), `Makefile` (A8 install echo; C5 comment), `CONTEXT.md` (C3 Entry Interface → Entry Surface, drop "pending", and correct the stale "(v3 skeleton … runtime facts do not exist yet)" parenthetical to present tense); verify harness AGENTS.md ≤ 7000 chars, checker exit 0
- [x] 6.4 Update the four implemented-layer `__init__.py` docstrings (B8, agents/ stays under allowlist) and fix the machine-local absolute path in `docs/testing-and-evaluation.md` (B10); verify `make verify` exit 0 (112 tests)

## 7. Openspec layer catch-up

- [x] 7.1 Fix `selected-change-closeout.md` naming (B13), `architecture-policy.md` "node grammar" (B14), `required-paths.toml` skeleton-era header remnant (B15), and the `check_project_gate.py` proof-receipt comment's stale "(PRS-009)" citation (B16; B12/A10 were resolved by `remove-requirement-id-tracking` deleting the registry and re-basing the gate at six components); verify all governance checkers exit 0
- [x] 7.2 Rewrite the Delivery Lanes section in `change-guidance/local/deep-research.md` (A9: lanes land with their owning change; today `make verify`/`make smoke` only; no mention of nonexistent commands); verify `git grep -n "make proof\|proof-lanes.toml" openspec/change-guidance` returns only the historical/allowlisted content
- [x] 7.3 De-duplicate: test-evidence pending promise → single owner (C9), Program Focus grammar → config.yaml owns (C10), "possible future use" mantra → change-practice.md keeps it, four pointers elsewhere (C11), delete or start using the two dead glossary terms in `openspec/CONTEXT.md` (C12); verify each fact has exactly one owner and pointers resolve
- [x] 7.4 `openspec/config.yaml` diet: relocate the Chinese design-routing block's operative content into `change-guidance/README.md`, keep a one-line pointer (C13); verify config.yaml measures below its ceiling with headroom and `check_change_guidance.py` exit 0

## 8. Budget ratchet + closeout evidence

- [x] 8.1 Measure all five declared resident files post-change and ratchet `DOC_BUDGETS` numbers down to the new measurements (no raises); verify `check_doc_hygiene.py` exit 0 with the lowered ceilings
- [x] 8.2 Run the full closeout evidence set and record receipts: `check_doc_hygiene.py --self-test` (negative controls red-first proven), `check_doc_hygiene.py`, `check_project_specs.py`, `check_project_architecture.py`, `check_change_guidance.py`, `check_harness_dependency_direction.py`, `check_ci_governance.py`, `check_release_face.py`, `make verify` — all exit 0; `git diff --check` clean
