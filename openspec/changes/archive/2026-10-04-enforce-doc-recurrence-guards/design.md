# Design

## Context

Verified this session (post `1ee535a`, which retired requirement-ID tracking
end-to-end; the operator confirmed the retirement is intentional):

- `check_doc_hygiene.py` carries eight rules; the two recurrence mechanisms live in
  `_rule_ledger_consistency` (rule 7: presence/index/counter checks — no placement
  check) and in no rule at all for counts (the root README status line is free text).
- `DOC_BUDGETS` still declares the pre-sweep ceilings 2435/6864 while the measured
  sizes after `doc-hygiene-second-sweep` are 2425/6863 — the ratchet-down this change
  executes (ordinary edit per the doc-budgets spec).
- `MARKER_ALLOWLIST` justifies the empty `agents/` layer with a path into
  `_backlog/plans/`; the plan file now lives in `_done/_closed_plans/`.
- `check_project_gate.py` runs six component checkers; the retired tracking checkers
  are gone and nothing else references the registry.

## Goals / Non-Goals

**Goals:** two new red-first rules (count pinning, row placement) with negative
controls; allowlist justification corrected; ceilings ratcheted down; A5 and C2
content declarations landed; C3 recorded as accepted (no edit).

**Non-Goals:** no change to the other six checker files or their semantics; no CI
workflow edit; no harness runtime/CLI change; no `deerflow/` contact; no revival of
requirement-ID tracking (retired by `1ee535a`; the delta therefore carries no
`> req:` header — requirement IDs no longer exist as a system).

## Decisions

1. **Count pinning is structural, not byte-exact.** The checker computes
   `len(list(openspec/specs))` and `len(list(openspec/changes/archive))` and requires
   the root README status line to contain those two integers anchored to their
   inventory nouns (the line's "能力"/"归档" phrasing). Wording may evolve; numbers
   may not drift. Alternative rejected: pinning a byte-exact sentence would make
   every wording edit a checker edit.
2. **Row placement rides the existing ledger rule.** Placement (contiguity with the
   row's table header block) is added inside `_rule_ledger_consistency`, reusing its
   surface enumeration and failure naming. A row separated from its header block by a
   blank line, prose, or a fence fails; two adjacent tables in one file each validate
   against their own header. Alternative rejected: a separate rule would duplicate
   the surface walk.
3. **Negative controls live in the checker's self-test**, which already exercises
   each rule against built fixtures (`--self-test`); both new rules gain a failing
   fixture and the green case, demonstrated red before the rule lands (TDD).
4. **Content declarations are one-line edits.** A5 in `CONTEXT-MAP.md`
   (vocabulary-routing owner); C2 one line in each of the two gate texts declaring
   divergence allowed with the harness version as application authority. The harness
   `AGENTS.md` line must be budget-neutral or negative (6863/6864 headroom is 1
   character) — the C2 line replaces an equal-or-longer passage.
5. **Ratchet-down is data, not ceremony.** `DOC_BUDGETS` entries move to the measured
   2425/6863 with a comment noting the sweep; the doc-budgets spec explicitly makes
   lowering ordinary.

## Risks / Trade-offs

- [The count rule's structural anchor can miss a reworded status line] → the anchor
  requires both integers and both inventory nouns on one line; removing either noun
  fails loudly as unpinned, which is the contract (counts must stay declared).
- [Row placement is syntactic; a semantically misplaced row inside the right table
  still passes] → accepted: the failure modes observed twice (B3/B5) were structural;
  semantic placement is review's job and remains visible in diffs.
- [Self-test fixtures drift from real-tree shapes] → the self-test fixtures are built
  from the same path conventions the real ledger uses; the real-tree green run after
  each rule is part of the done criteria.

## Migration Plan

Red-first: add both negative controls to the self-test suite, run them red against
the current checker → implement the two rules and the allowlist fix → self-test and
real tree green → ratchet ceilings → land the A5/C2 one-liners → full closeout gate.
Rollback: revert the single change commit; no data or runtime state involved.

## Open Questions

None — all five semantic forms were ruled by the operator on 2026-10-04.
