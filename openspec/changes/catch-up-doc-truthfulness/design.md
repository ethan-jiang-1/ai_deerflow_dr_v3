# Design

## Context

See proposal.md — Why. The declaration layer lags the implemented reality in ~40 audited
places; the only behavior-bearing deliverable is two new rules in
`openspec/governance/check_doc_hygiene.py` (437 lines, rule-per-function architecture:
`_rule_*(root) -> list[str]`, composed by `violations()`, negative-control fixtures in
`_self_test()`, standalone CLI with `--self-test`, already wired into the CI canonical
sequence). Resident budgets are tight: root `AGENTS.md` 2323/2500, harness `AGENTS.md`
6934/7000, `openspec/config.yaml` 12,237/12,500. The ledger's authoritative formats are
parseable today: `_closed_plans/README.md` rows embed literal filenames as markdown
links; `_done/README.md` declares counts and Next IDs in a table.

## Goals / Non-Goals

**Goals:**
- Truth held by machine: after this change, re-introducing a stale skeleton claim or
  dropping a ledger index row fails a checker loudly, instead of waiting for the next
  audit.
- All 40 audit findings in scope closed with before/after receipts; resident budgets
  end strictly lower than they started.
- Red-first discipline: each new rule has a deterministic negative-control fixture that
  fails before the rule exists and passes after; the live tree itself is red for both
  rules today (missing CLS-008/009 rows; live markers), so the red state is doubly
  demonstrated.

**Non-Goals:**
- The four deferred semantic decisions (see proposal Not in scope): no spec content
  changes, no `check_proof_receipts.py` behavior change, no `agents/` layer change.
- No heuristic/NLP staleness detection: the marker rule is a closed declared list, not
  a linter over all "骨架" mentions.
- No new checker script, no new CI wiring, no ceiling raise.

## Decisions

1. **Extend `check_doc_hygiene.py` instead of adding a new checker.** The two rules are
   doc-layer facts; the script already owns rule composition, self-test fixtures, CLI,
   CI placement, and the `_backlog` `_`-directory rule. A new script would buy registry,
   required-paths, gate, and CI churn for zero semantic gain. Declaring tables
   (`STALE_MARKER_FILES`, `STALE_MARKERS`, `MARKER_ALLOWLIST`) sit at the file top next
   to `DOC_BUDGETS`, same comment discipline ("adding a file is a visible change").
2. **Ledger consistency parses declared formats narrowly, not markdown generically.**
   The rule requires: every active/archive work-item file (non-README) appears as its
   literal `<name>.md` in its directory's README; every README link target ending in
   `.md` resolves on disk; `_done/README.md`'s per-directory counts equal the disk
   inventory; the declared Next ID equals max allocated ID + 1 (bugs union across
   active/fixed/suspended, per the ledger's own rule). The formats are already stated
   in the ledger READMEs; if a format evolves, the declaring-table comment is where the
   contract is maintained. Alternative rejected: full markdown-table parsing (brittle,
   over-coupled to rendering).
3. **Marker rule = closed file list × closed marker list × justification allowlist.**
   `(file, marker)` pairs outside the allowlist fail with file/marker/line; an allowlist
   entry without a justification (or matching no file on disk) also fails — the allowlist
   cannot become a silent dumping ground. `agents/__init__.py` + "(skeleton)" enters the
   allowlist with a justification pointing at its deferred owning decision; the other
   four layer docstrings are updated (truthful today, so no allowlist entry).
4. **TDD sequence per rule, then content.** Order: (a) add negative fixtures +
   assertions to `_self_test()` and the new declaring tables → `--self-test` fails
   (rules absent); (b) implement the rules → `--self-test` green, live tree still red
   (expected, receipts recorded); (c) repair the ledger and run the content catch-up →
   live scan green. This makes every content fix test-backed rather than vibes-backed.
5. **config.yaml diet is relocation, not deletion of governance.** The Chinese
   design-routing block's operative content moves to `change-guidance/README.md`'s
   policy route section (its existing owner); config.yaml keeps a one-line pointer.
   Both files stay inside their ceilings; the requirement wording in config.yaml's
   rules is untouched.
6. **Root AGENTS.md routing addition (C2) is paid for in the same file.** The routing
   row for `CONTEXT-MAP.md` plus the A2/A3/B5 deletions must net out at or under 2500
   chars; the harness AGENTS.md future-tense deletions (A8) pay for nothing new — its
   budget only shrinks.

## Risks / Trade-offs

- [Tight budgets flip a file red mid-edit] → per-file edit order is delete-then-add,
  with `check_doc_hygiene.py` run after each resident-file task; ceilings are ratcheted
  down only after the final measurement.
- [Ledger format drift breaks the parser] → the parser validates the formats the ledger
  READMEs themselves declare; a format change is a visible diff to those READMEs and
  will trip the rule, which is the desired loud failure, not silent acceptance.
- [Marker list too narrow to prevent regression] → accepted: the rule's job is to lock
  today's caught-up state against the *recorded* failure modes (skeleton claims,
  placeholder commands, unindexed ledger rows); novel staleness is what the next audit
  and the playbook's same-turn repair discipline are for.
- [Allowlist rots (layer gets implemented, marker stays)] → the deferred-decision
  justification names its owning decision; when that change lands, removing the
  allowlist entry is part of its closeout. A dangling entry fails the checker.

## Migration Plan

Content + checker changes land in one apply (single change, no runtime surface). Rollback
is `git revert`; the rules fail loudly rather than silently, so a partial revert is
always visible. Registry rows for the new requirement IDs are added in the same apply
(registered with their evidence seam before closeout).

## Open Questions

None blocking. The four deferred semantic decisions are recorded as proposal Not-in-scope
and do not affect this design, these specs, or the task breakdown.
