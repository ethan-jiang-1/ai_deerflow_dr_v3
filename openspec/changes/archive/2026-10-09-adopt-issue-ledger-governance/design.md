# Design

## Context

The ledger rule in `check_doc_hygiene.py` (`_rule_ledger_consistency`, spec
`doc-truthfulness`) already enforces both roster directions, table placement, counters,
and next-ID arithmetic over the surface tables `BACKLOG_ACTIVE_SURFACES` /
`BACKLOG_ARCHIVE_SURFACES`; `required-paths.toml` pins the same paths as the structural
inventory. The category rename therefore lands as table data, not as a new mechanism.
The genuinely new mechanism is two red-first rules (hukou, residency) plus one scope
addition (`triggers.md` into `ENTRY_DOCS`). See proposal.md — Why for motivation and the
issue card `_backlog/plans/2026-10-09-backlog-governance-reborrow.md` for the decision
record.

## Goals / Non-Goals

**Goals:**

- Rename the category in one revision: directories (`git mv`), checker surface tables,
  `required-paths.toml`, and the live linking documents move together so every gate stays
  green at each commit boundary.
- Hold the two observed failure classes by machine: card without hukou; card declaring
  `毕业门：已过` / `可关闭：是` still sitting in the active zone.
- Give deferred verdicts a pointer-only visible surface (`triggers.md`) with scan
  obligations written into the charter, under the admit bar borrowed from the
  DSH-assistant ruling (one self-encountering observation; "user names it" is not a
  trigger; standing instructions are not duplicated).

**Non-Goals:**

- No mechanization of trigger-row semantics (borrowed ruling: semantic judgment is not
  gate material; recurrence is the escalation path, not pre-arming). Methods content is
  likewise ungated (human-discipline surface; the link rule covers its files only if they
  join the entry chain, which they deliberately do not).
- No rewrite of frozen history: `openspec/changes/archive/` references and the 19
  archived card bodies stay verbatim (including their historical `_done` mentions).
- No `_reference/` lifecycle, no YAML frontmatter, no CLS renumbering.

## Decisions

1. **Rename as table data + same-revision receipts, not a deprecation window.** The
   surfaces are internal bookkeeping with exactly one writer (this ledger's ritual) and
   zero external consumers found (grep receipt in tasks); a two-name transition period
   would double the declaring tables for no reader. Alternative rejected: keep `plans/`
   and alias `issues/` — two names for one thing is the split-brain the rename exists to
   remove.
2. **Hukou anchored on a status-line field, not YAML frontmatter.** The checker is
   line-based, the bug cards already carry `状态：` status lines, and the 19 archived
   cards stay untouched (grandfathered out of the new checks). The status line carries
   all anchored fields (`状态` / `毕业门` / `可关闭`), so one parse location serves both
   new rules. Alternative rejected: YAML frontmatter (DSH-assistant shape) — a second
   header convention inside this repo's card family and a checker rewrite for no gain at
   this scale.
3. **Residency anchors on declared fields, never on prose.** `毕业门` `已过` and
   `可关闭：是` are termination-state fields the card author sets deliberately;
   delivery language in the body (`已交付`, `全落地`) must never red-line an honest
   awaiting-human card. This is the DSH-assistant 2026-10-08 lesson (their first draft's
   `已交付` regex mis-killed a card waiting on final human acceptance; the fix anchors
   the gate on the graduation field itself). Fixtures include the mis-kill negative
   explicitly.
4. **`triggers.md` joins `ENTRY_DOCS`, not a new rule.** Row honesty (each row's home
   link resolves) is exactly what the existing relative-link rule does; content semantics
   stay ungated. The charter carries the admit bar, the delete bar, and the scan moments;
   the index never holds the deferred sentence itself — that stays on the owner card or
   record, so the index cannot drift into a second truth home.
5. **Trigger seed by harvest-under-a-bar, not bulk import.** The 19 archived cards are
   swept for deferred verdicts; each candidate must name one self-encountering
   observation and a live owner, else it is dropped (expected survivors: CLS-010 Tier-C
   items with their consumption status checked against CLS-020; the agent-playbook
   budget-revisit line). "User names it" candidates (plan-review-gate, wiring-structure)
   are recorded as rejected in the charter's register, so the bar is auditable.
6. **CLS numbering continues across the rename.** The identifier is assigned at settle
   time and cited by live docs (`testing-and-evaluation.md` CLS-010, `docs/README.md`
   CLS-014); re-prefixing is pure churn with real link cost. The category name changes;
   the identity scheme does not.
7. **Methods are digested, not copied (mid-apply user ruling 2026-10-09).** The original
   plan refused a `methods/` directory; the user overturned it ("methods 很重要"). The
   seven method bodies are rewritten against this repo's facts — downstream entry is
   `openspec-propose` stopping at the admission boundary (`issue-to-change`, not
   `issue-to-note`), evidence owners are the lane table and test-evidence policy, seam
   classes use this repo's vocabulary, the research lifecycle is replaced by
   evidence-on-card + `_reference/`, and the card naming/hukou rules follow this charter.
   Methods are standing infrastructure (no roster, no hukou, no work-item lifecycle), and
   the charter's routing table routes through them. Alternative rejected: verbatim copy —
   their methods reference a `notes/` downstream, a `research/` directory, and their
   skill-checkout paths, none of which exist here.
8. **`_done/` → `_archived/` (mid-apply user ruling 2026-10-09).** The original plan kept
   the name to avoid churn; the user overturned it. The honest-name argument wins: the
   directory holds suspended (not-done) work, so `_done` lied about its contents the same
   way `plans` lied about the category. Mechanically it is the same rename discipline as
   decision 1 — one `git mv`, the checker's declaring tables (`BACKLOG_UNDERSCORE_DIRS`,
   `BACKLOG_COUNTERS_FILE`, surface paths, fixtures), `required-paths.toml`, `.gitignore`,
   and every live link move in the same revision; frozen bodies keep their historical
   mentions.

## Risks / Trade-offs

- [New rules red-line the repo's own first cards] → the reborrow card is written in the
  target hukou form before the rules land; the apply sequence runs the checker live
  immediately after each rule and fixes the ledger, not the rule, when the red is real.
- [`AGENTS.md` budget is tight (2425 ceiling)] → the one-cell edit is
  character-neutral; if the header date bump tips it over, the same edit trims an equal
  amount elsewhere in the file (declared in the receipt).
- [Rename breaks an unknown consumer] → pre-apply grep receipt over root docs,
  `openspec/`, `deep_research_harness/` (excluding `archive/` and `deerflow/`); the
  doc-hygiene link rule and the `required-paths.toml` inventory both fail loudly on a
  miss, so the class is covered, not just the listed files.
- [`triggers.md` grows unbounded] → charter delete rules (trigger arrived; ruling
  overturned; row fails the "would you remember without the table" test); rows are
  pointers, so a dead row fails the link rule instead of rotting silently.
- [Vocabulary drift (`状态` words multiplying)] → the vocabulary is a declared tuple in
  the checker; adding a word is a visible table change, same discipline as surfaces.

## Migration Notes

Apply order inside the change (red-green at each step): checker rules + fixtures first
(red on fixtures, then live-run), ledger READMEs + template next, then the three
`git mv` moves together with `required-paths.toml` and the live link re-points, then
`triggers.md` seed + charter sections, then full gate receipt (`check_doc_hygiene.py`
incl. `--self-test`, `check_project_gate.py --phase plan/closeout`, `make verify`).
