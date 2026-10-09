# doc-truthfulness Specification

## Purpose

Owns the required behavior of the declaration-layer truthfulness gate: the ledger
bookkeeping surfaces stay mechanically consistent with disk, and a declared closed list
of resident and doc-layer files stays free of declared stale-narrative markers, both
enforced by the document-hygiene checker's red-first rules so narrative cannot lag
implementation silently.

## Requirements

### Requirement: Ledger bookkeeping surfaces are machine-consistent

The document-hygiene checker SHALL validate the `_backlog` ledger's bookkeeping
surfaces — each active directory's README (`issues/`, `bugs/`), the `_archived/README.md`
counters, and each archive subdirectory's index README (`_fixed_bugs/`,
`_suspended_bugs/`, `_settled_issues/`, `_suspended_issues/`) — as one consistency
surface: a work-item file present in an active or archive directory SHALL appear in that
directory's README list, a README list row SHALL reference a file that exists on disk
under the declared naming convention, and the counters and next-ID declarations in
`_archived/README.md` SHALL match the authoritative index tables and the disk inventory.
The checker SHALL additionally validate card hukou and residency: every work-item card
in an active directory SHALL carry a `状态：` field within its first 12 lines whose word
is a member of that surface's declared status vocabulary, and an active card whose
status line declares the graduation field as passed (`毕业门` value `已过`) or declares
`可关闭：是` SHALL fail until it leaves the active directory — the match SHALL anchor on
those declared fields only, so awaiting-human (`等人拍板`) and not-yet-graduated (`未过`)
cards never fail. The checker SHALL fail loudly naming the inconsistent surface, the row
or file, and the expected reconciliation; adding a bookkeeping surface, a status
vocabulary, or a graduation-anchored field to management is a visible change to the
declaring tables. Archived cards are out of scope for the hukou and residency checks
(grandfathered), and renaming a category SHALL update the declaring surface tables and
the structural manifest in the same revision that moves the directories.

#### Scenario: Consistent ledger passes

- **WHEN** the checker runs and every active/archive work-item file is indexed, every
  row resolves to disk, the counters and next-ID declarations match, every active card
  carries a vocabulary-checked `状态：` hukou, and no active card declares a passed
  graduation field or `可关闭：是`
- **THEN** the checker exits 0

#### Scenario: Unindexed or dangling row fails loudly

- **WHEN** a work-item file exists on disk without an index row, or a row references a
  file name that does not exist on disk, or a counter disagrees with its authoritative
  table
- **THEN** the checker exits non-zero and names the surface, the offending row or file,
  and the reconciliation

#### Scenario: Card without hukou fails loudly

- **WHEN** an active card lacks a `状态：` field in its first 12 lines, or its status
  word is not in the declared vocabulary for its surface
- **THEN** the checker exits non-zero and names the surface, the card, and the
  vocabulary

#### Scenario: Residency violation fails loudly

- **WHEN** an active card's status line declares `毕业门` as `已过` or declares
  `可关闭：是`, and the card still sits in the active directory
- **THEN** the checker exits non-zero and names the card and the declared field

#### Scenario: Awaiting-human card passes

- **WHEN** an active card's status line reads `状态：等人拍板` with `毕业门` `未过` and
  `可关闭：否`, including a card that also records delivered-partial language in its body
- **THEN** the checker exits 0

### Requirement: Declared stale-narrative markers fail loudly

The checker SHALL validate a declared closed list of resident and doc-layer files
against a declared closed list of stale-narrative markers — pre-implementation-era
placeholder phrases and stale module docstring claims on implemented layers, each
declared verbatim in the checker's declaring table. A file
measuring as containing a marker SHALL fail loudly naming the file, the marker, and the
line, unless an explicit allowlist entry covering that file-and-marker pair carries a
recorded justification (for a marker that is currently true, such as the genuinely
empty `agents/` layer). Adding a file, a marker, or an allowlist entry is a visible
change to the declaring tables; an allowlist entry without a justification fails the
check.

#### Scenario: Truthful declaration layer passes

- **WHEN** the checker runs and no declared file contains a declared marker outside the
  justified allowlist
- **THEN** the checker exits 0

#### Scenario: Re-introduced marker fails loudly

- **WHEN** a declared file gains a declared marker with no covering allowlist entry
- **THEN** the checker exits non-zero and names the file, the marker, and the line

#### Scenario: Allowlisted exception stays honest

- **WHEN** a file contains a marker but a justification-recorded allowlist entry covers
  the pair, or an allowlist entry has no justification or no longer matches any file
- **THEN** the covered pair passes, and an unjustified or dangling allowlist entry
  fails loudly naming the entry
