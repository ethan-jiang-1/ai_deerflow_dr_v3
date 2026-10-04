# Design

## Context

Verified current state (measured this session, HEAD `6458c2d`):

- The three resident files sit exactly at their `DOC_BUDGETS` ceilings: root `AGENTS.md`
  2435/2435, `deep_research_harness/AGENTS.md` 6864/6864, `openspec/config.yaml`
  11436/11436. `check_doc_hygiene.py` passes (exit 0) — the tree is green; every defect
  in the plan card lives in space no rule currently reaches.
- The stale-marker rule declares seven forbidden phrases over 20 managed files
  (`check_doc_hygiene.py` `STALE_MARKERS`/`STALE_MARKER_FILES`, with one justification
  allowlist entry for the genuinely empty `agents/` layer). Every rewrite in this change
  must compose around that list without touching it.
- The machine-held surfaces are: ledger index/counters (rule 7), markers (rule 8),
  budgets, entry-chain links, and the COMMANDS↔Makefile↔cli command surface. The
  defects being repaired (checker enumeration, counts in prose, section structure,
  duplicated recitals) are all in free text outside those surfaces.
- `check_doc_hygiene.py`'s `MARKER_ALLOWLIST` justification references
  `_backlog/plans/2026-10-04-fresh-agent-doc-cleanup.md`, which moved to
  `_done/_closed_plans/` when CLS-012 closed — a newly found stale pointer inside a
  checker file. It is out of this change's scope (see Not in scope in proposal.md) and
  is recorded for the follow-up governance change.

## Goals / Non-Goals

**Goals:**

- All 19 change-scoped findings repaired with machine-verifiable before/after receipts.
- Every edit conformant to existing rules: no ceiling exceeded, no marker introduced,
  no link broken, COMMANDS menu unchanged, ledger ritual respected.
- Each recurrence mechanism's *immediate symptom* fixed in a way the next sweep can
  diff against.

**Non-Goals:**

- No checker rule, declaring table, or allowlist edit; no spec requirement change; no
  `openspec/config.yaml` edit (it is at ceiling and needs none of the fixes).
- No ruling on the deferred semantic decisions (A5, C2, C3, systemic A2) — they stay
  with the user and the follow-up governance change.
- No `deerflow/` source modification or browsing beyond the qualified upstream
  references added by A7/B7.

## Decisions

1. **Single mechanical pass, no checker edits.** The change repairs declarations only;
   the anti-recurrence apparatus (count enforcement, ledger-row placement validation,
   allowlist justification fix) is a separate governance change the user rules on
   first. Rationale: mixing declaration-layer edits with checker semantics in one
   change violates the plan card's own routing and doubles the review surface.
2. **Budget strategy: delete-then-add, measure per edit.** For the two resident
   `AGENTS.md` files, each edit removes an equal-or-larger stale passage before adding
   replacement text, and `check_doc_hygiene.py` runs after every edit (its budget rule
   is the red/green instrument). B1 (remove `scripts`) and the C1 recital removal in
   harness AGENTS.md free the headroom A6-A8 need.
3. **Marker avoidance by wording, not allowlist.** Replacement phrases are composed to
   avoid all seven declared markers (e.g. the `agents/` first-read annotation reads
   "空层;契约随 owning code 落地" — which contains no declared marker). Rationale:
   extending the allowlist would be a checker edit (out of scope) and would weaken the
   rule for everyone else.
4. **A2 short-term: correct the numbers to measured reality (11/31).** The systemic
   form (pointerize counts or enforce them) is a semantic decision the user has not
   ruled on; the proposal records it as the follow-up change's first agenda item.
   Rationale: leaving known-false numbers in the freshest-read file for one more cycle
   is worse than a number that will age honestly.
5. **Governance README edits verify against the full gate.** No current checker pins
   the governance README's enumeration text (verified: the gate is green while the
   enumeration is wrong), but `check_ci_governance.py` and the doc-hygiene link rule
   both touch nearby surfaces — after each governance-layer edit, the change runs the
   whole gate, not just doc hygiene.
6. **C1 consolidation keeps the guarded surface intact.** `COMMANDS.md` becomes the
   single semantic owner of `make verify` meaning; the seven other surfaces shrink to
   one word + link. COMMANDS↔Makefile↔cli stays pinned by the command-surface guard,
   so the consolidation removes unguarded recitals only.
7. **B6 retired IDs: pointer, not deletion.** ENS-001/RT10/RLF-001 mentions stay but
   each gains a pointer into the archived retiring change. Rationale: the retiring
   change declared these mentions inert history; deleting them loses traceability of
   why the names exist at all.

## Alternatives

- **Fold the anti-recurrence apparatus into this change** — rejected: it mixes
  declaration-layer and checker-semantic work in one review surface, and its two
  central choices (count enforcement form; row-placement rule) need a user ruling the
  plan card explicitly defers (decision 1).
- **Raise a resident ceiling to create headroom** — rejected: the budget ratchet only
  goes down; both AGENTS.md files have net-negative edits available (decision 2).
- **Extend the marker allowlist to permit new wording** — rejected: a checker edit out
  of scope, and wording freedom suffices (decision 3).
- **Pointerize the root README counts now (systemic A2)** — rejected for this change:
  it pre-empts the user's deferred decision; the honest interim is a correct number
  (decision 4).
- **Delete the retired requirement-ID mentions (B6)** — rejected: they are declared
  inert history; pointers preserve the trace at lower cost (decision 7).
- **Rewrite `known-limitations.md` as a fresh document** — rejected: the table's
  ongoing rows and their receipts are still live facts; only the resolved rows move
  out, so the edit is subtractive (A3).

## Risks / Trade-offs

- [Line numbers pinned to `6458c2d` drift as edits land] → every task re-verifies its
  finding's line and claim with `git grep` before editing; receipts quote matched text,
  not bare line numbers.
- [Zero budget headroom turns any additive edit red] → delete-then-add per edit with a
  checker run between steps (decision 2); the ratchet-down of declared numbers happens
  only after final measurement.
- [A checker pins governance-README text that today reads green only by accident] →
  full gate after each governance-layer edit (decision 5); a red gate on an edit is a
  finding, not a blocker — the edit adapts or the item routes out with a recorded
  reason.
- [Markdown table edits can re-break tables — this session's own plan card needed two
  structural fixes] → every table-touching task validates cell counts (a one-line
  Python check) before moving on.
- [Corrected counts (A2) age again at the next archive] → accepted deliberately
  (decision 4); the recurrence is the evidence for the follow-up change.
- [Consolidating recitals (C1/C5) drops nuance a specific file needed] → each
  shrink keeps the pointer adjacent to the surviving keyword, so the semantic
  destination stays one hop away.

## Migration Plan

Pure declaration-layer edits; no runtime, data, or interface migration. Rollback = git
revert of the change's commit(s). Order of execution (least risk first): `_backlog`
ledger ritual fixes (B3-B5, outside change scope, done alongside) → root layer →
harness doc layer → openspec layer → resident AGENTS.md files last (tightest budgets) →
final full gate + budget measurement (any warranted ratchet-down is recorded for the
follow-up governance change, keeping this change free of checker-file edits).

## Open Questions

None that block implementation. The deferred semantic decisions (A5, C2, C3, systemic
A2) are not open questions *of this change* — they are explicitly routed to the user
and the follow-up governance change.
