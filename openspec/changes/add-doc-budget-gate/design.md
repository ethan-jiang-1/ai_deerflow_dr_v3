# Design

## Context

Verified current state (correcting this change's own first draft, which wrongly assumed
no budget mechanism existed): `check_doc_hygiene.py` already carries a `DOC_BUDGETS`
table inherited from v2 — four managed resident files, character counts, and a ratchet
comment, all in place since the scaffold. What is actually missing, and what this
change completes: `openspec/config.yaml` (the largest resident-injection layer, 12237
chars measured) is unmanaged; the v2-era ceilings (root `AGENTS.md` 2900 vs measured
2323; `deep_research_harness/AGENTS.md` 8200 vs ~6.7k) sit far above v3 reality; a
managed file that goes missing is silently skipped (`continue`) on the assumption the
link rule reports it — it does not cover the root instruction files, so deletion would
go unnoticed; the budget rule has no negative-control self-test; and the behavior has
no owning spec. Gap D lands here because this change's diff touches
`deep_research_harness/AGENTS.md`. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**

- The largest resident file (`openspec/config.yaml`) managed with a deliberately tight
  ceiling; v2-era ceilings tightened to measured v3 baselines with clean-hundred
  headroom; the missing-managed-path defect closed; red proof for both failure modes
  via the checker's built-in self-test; the whole behavior spec-owned (DOB-001).

**Non-Goals:**

- No extracting the table into a TOML manifest (see Alternatives), no ceiling below the
  starting points (separate argued decisions), no git-history ratchet enforcement, no
  spec coverage of doc-hygiene's other rules, no CI change, no application code.

## Decisions

1. **Complete the existing table instead of building a new mechanism.** The budget rule
   already runs standalone and inside the CI canonical sequence; extending the table,
   fixing the skip, and adding self-tests completes gap C with the smallest possible
   diff. Alternative: a fresh dedicated checker or manifest was rejected — the propose
   draft's premise (no gate exists) was wrong, and this is recorded here rather than
   quietly rewritten.
2. **Characters, not words or bytes.** Kept from the inherited design and now spec'd:
   word counts under-count CJK text by an order of magnitude; bytes double-count it.
3. **Ceilings: measure, then round up to a clean hundred.** Root `AGENTS.md` 2500
   (2323 measured), `deep_research_harness/AGENTS.md` 7000 (~6.7k plus the gap-D line),
   `openspec/config.yaml` 12500 (12237 measured — deliberately tight to stop growth),
   the two `CLAUDE.md` stubs stay at 400. Starting points, not targets; the ratchet now
   protects every subsequent reduction.
4. **Missing managed file fails, not skips.** The inherited `continue` assumed the link
   rule reports missing files; it does not cover the root instruction files, so the
   budget rule owns the missing-managed-path failure itself. This closes a real silent
   gap (delete `AGENTS.md` today and the budget rule says nothing).
5. **Red proof via the checker's own `--self-test`.** The self-test harness is this
   checker's established negative-control mechanism; adding over-limit and
   missing-managed-path fixtures there keeps one red-proof home instead of a parallel
   unittest module.
6. **Ratchet stays review-level, honestly.** The table comment (inherited, kept) states
   the one-line-justification obligation; a raise is always visible in the diff. A
   history-reading checker adds a git dependency for marginal guard strength.
7. **Gap D folded in here** (its carrier condition: this diff touches
   `deep_research_harness/AGENTS.md`; identical entry-layer theme): the nested-AGENTS.md
   prohibition gains rationale and escalation condition in place.

## Alternatives

- **A new TOML budget manifest (`doc-budgets.toml`)** — rejected: the declaring table
  already exists in the checker; extracting it is a form refactor with zero new
  enforcement, and the declaring-table location is deliberately left as an
  implementation detail in the spec. Revisit if the table grows past a handful of
  entries or non-checker tooling needs to read it.
- **A dedicated gate component for budgets** — rejected: doc hygiene already runs in
  the CI canonical sequence; a ninth component adds wiring without adding enforcement.
- **Byte or line budgets** — rejected: bytes double-count CJK; lines are evaded by a
  single long line and conflate wrapping style with size.
- **Git-history ratchet enforcement** — deferred (decision 6).
- **Tight ceilings below today's sizes** — deferred: establish the completed gate at
  honest starting points; reductions are separate argued decisions.

## Risks / Trade-offs

- [A managed file legitimately needs growth] → the ratchet path: a change with a
  one-line justification raises the ceiling, visible in the diff for review.
- [The `openspec/config.yaml` ceiling at 12500 leaves only ~260 chars of headroom] →
  deliberate: the file is the known bloat risk (the DSH borrowing analysis named it);
  hitting the ceiling forces the argued conversation instead of silent growth.
- [Self-test fixtures grow the checker] → bounded: two focused fixtures; the harness
  already exists.

## Migration Plan

Single apply: land the gap-D line, measure the post-D baseline, tighten and extend the
table, fix the skip, add the two self-test cases, register DOB-001, add `@impl DOB-001`
to the checker docstring, update requirement IDs and the governance README, verify with
direct exit codes. Rollback is reverting the edits; the registry entry takes a
retirement marker per the append-only discipline if abandoned post-registration.
