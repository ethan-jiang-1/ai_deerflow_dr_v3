# Proposal: Doc Hygiene Second Sweep

## Why

The first sweep (CLS-012 → `catch-up-doc-truthfulness`) proved effective for everything
it put under machine rules: zero broken relative links, ledger bookkeeping mechanically
consistent, resident budgets ratcheted. A second fresh-agent audit
(`_backlog/plans/2026-10-04-doc-hygiene-second-sweep.md`, committed `cc4b675`, all line
numbers verified at HEAD `6458c2d`) found 26 defects in exactly the space those guards do
not reach — plus two **recurrence mechanisms**: inline counts drift again at every
archive (root README was corrected to 9/29 by the catch-up change itself, and is now
11/31), and ledger "补记" (backfilling) bypasses table structure (the CLS-012 row landed
after the card-template code fence; the `_closed_plans` table is re-shattered by the same
blank-line pattern CLS-012 fixed). Narrative lag in the resident layer is the denominator
of every prompt; it misdirects every future session until repaired.

## What Changes

- **Declaration-layer repairs** (19 of the 26 findings; A1-A4, A6-A8, B1, B6-B10, C1,
  C4-C8 of the plan card) across root, `deep_research_harness/`, and `openspec/`:
  - Correct the governance README's component-checker enumeration to the real gate
    inventory (`check_proof_receipts.py` is a component; `check_release_face.py` is
    standalone) and route the four un-routed governance files; include the missing
    `make smoke` CI step (A1, C8).
  - Correct root README counts to measured reality (11 capability specs, 31 archived
    changes) as the short-term fix (A2; the systemic pointer-ize/enforce decision stays
    with the user — see Not in scope).
  - Re-scope `known-limitations.md` to genuinely ongoing items; resolved rows collapse
    to pointers (A3); fix the tier table's duplicate "级 3" (C6); shrink closed-out
    history (借鉴队列, playbook receipt history, archaeology numbers) to pointers (C7).
  - Fix the "三套搬迁 ritual (todo/bug/plan)" fossil to the two-kind rule (A4); remove
    the nonexistent `scripts` from root AGENTS.md's layer table (B1); repair the
    dead "Suspended" pointer (B2); qualify root README's not-yet-present root residents
    (B8); repair the `local/deep-research.md` section broken mid-sentence (B9); remove
    the live dangling "the boundary plan above" phrase and fix the "v3 direction note"
    link label (B10 — cold-review find: the phrase survived the first sweep's
    root-README fix).
  - Add the missing "when it is not ordinary work" criterion for source-browsing the
    read-only upstream, and qualify bare `client.py:293` references to the upstream
    path (A7, B7 — includes the `runtime/client.py:18` comment, a comment-only edit).
  - De-dangle the `agents/` first-read pointer (A8) without using any declared
    stale-marker phrase.
  - Retire the retired-requirement-ID mentions to pointers into the archived change
    (B6: ENS-001 / RT10 / RLF-001).
  - Consolidate duplicated authority: `make verify` semantics under `COMMANDS.md` as the
    single semantic owner (C1); the gotcha list lives in the playbook, local-operations
    points at it (C4); the v3 narrative keeps one full telling, others point (C5).
- **Ledger ritual repairs** (B3-B5: misplaced CLS-012 row, stale `_backlog` header,
  re-shattered `_closed_plans` table) execute alongside as direct `_backlog` ritual
  maintenance per the plan card's routing — they are **not** change scope and carry no
  spec delta.
- **No checker rule changes, no spec requirement changes, no code behavior changes.**

## Capabilities

### New Capabilities

<!-- none: this change holds no behavior-bearing deliverable. -->

### Modified Capabilities

<!-- none: every edit is declaration-layer content or a code comment. The
     doc-truthfulness, doc-budgets, agent-playbook, and entry-surface requirements are
     conformed to, not changed: budgets only shrink, the marker allowlist is untouched,
     the COMMANDS menu and routing targets are unchanged, and playbook receipt
     discipline is satisfied by removing stale facts. The change therefore declares
     skip_specs: true (established pattern: 16 of 31 archived changes). -->

## Impact

- Modified (docs/content only): root `README.md`, `AGENTS.md`;
  `deep_research_harness/README.md`, `AGENTS.md`, `COMMANDS.md`,
  `docs/known-limitations.md`, `docs/local-operations.md`,
  `docs/testing-and-evaluation.md`, `docs/quality-register.md`,
  `playbook/run-research.md`; `openspec/governance/README.md`,
  `openspec/change-guidance/local/deep-research.md`.
- Modified (comment text only, zero behavior): `deep_research_harness/src/deerflow_deep_research/runtime/client.py:18`.
- Ledger ritual maintenance (outside change scope, executed alongside):
  `_backlog/plans/README.md`, `_backlog/README.md`,
  `_backlog/_done/_closed_plans/README.md`,
  `_backlog/_done/_suspended_bugs/README.md`.
- Removed: the untracked `.pi/tasks/` residue directory.
- Not touched: `openspec/governance/check_doc_hygiene.py` (and every other checker),
  all capability specs under `openspec/specs/`, `openspec/config.yaml`, Makefile target
  semantics, `cli.py`, CI workflow, and the `deerflow/` gitlink (read-only, never
  modified or source-browsed beyond the qualified upstream references this change adds).

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` — owner
  of the declaration-layer rules (stale-marker list, resident budgets, link and ledger
  rules) that every edit here must conform to and that supply the negative-path
  evidence; the change itself adds no rule and touches no checker code.
- **Seam classification:** deterministic-guardrail — every edit and every verification
  is a deterministic textual fact under machine rules; no model, prompt, state machine,
  or lifecycle outcome is touched.
- **Question:** Can the 19 change-scoped findings (including the immediate symptoms of
  both recurrence mechanisms) be repaired in one pass while the three resident files sit
  exactly at their character ceilings (root `AGENTS.md` 2435/2435, harness `AGENTS.md`
  6864/6864, `openspec/config.yaml` 11436/11436 — the last is untouched here), without
  changing any checker rule or spec requirement and without touching any checker file?
- **Necessary adjacent/external contracts:** `doc-budgets` capability (answers: the
  character ceilings and ratchet discipline the edits must fit under);
  `doc-truthfulness` capability (answers: the declared marker list and justification
  allowlist the rewrites must not collide with); `agent-playbook` capability (answers:
  the COMMANDS menu discipline and playbook receipt rule the C1/C4/C7 edits must keep);
  `_backlog/README.md` ledger ritual (answers: why B3-B5 route as direct maintenance);
  `_backlog/plans/2026-10-04-doc-hygiene-second-sweep.md` (answers: the 26 findings,
  their file:line evidence, and the deferred semantic decisions).
- **Evidence seam:** per-A-class-claim `git grep` before/after receipts; the checker
  suite as the deterministic gate (`check_doc_hygiene.py`, `check_project_gate.py
  --phase plan`, `check_release_face.py`, `make verify` — all exit 0); resident-budget
  measurements before/after (must not exceed ceilings).
- **Not in scope:** the semantic decisions the plan card defers to the user — the
  `profile` vocabulary registration (A5), the six-step LLM-Node gate dual-authority
  ruling (C2), the routing-table disposition (C3), and the systemic form of A2 (count
  pointerization vs checker enforcement); the anti-recurrence apparatus itself (a
  follow-up governance change that owns all checker edits, including the newly found
  stale justification path in `MARKER_ALLOWLIST` that references the moved
  `_backlog/plans/2026-10-04-fresh-agent-doc-cleanup.md`); the ledger ritual fixes
  B3-B5; and any `deerflow/` source change.
- **Triggered review policies:** change-admission, authority-and-projections, local-context

## Impact on resident budgets

All edits to budgeted resident files are net-negative or budget-neutral (delete-then-add,
counted per edit): root `AGENTS.md` loses the `scripts` entry (B1) and gains the A8
annotation; harness `AGENTS.md` loses A6/A7/A8/B6 restatements and the C1 verify
recital. Declared ceilings are not raised; a ratchet-down, if the post-change
measurements warrant one, is recorded in this change's closing notes and executed by
the follow-up governance change (which owns all checker-file edits, per the
`doc-budgets` spec's ordinary-edit rule).
