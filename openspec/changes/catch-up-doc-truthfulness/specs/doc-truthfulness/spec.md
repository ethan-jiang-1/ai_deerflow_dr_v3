# Spec Delta

## Purpose

Owns the required behavior of the declaration-layer truthfulness gate: the ledger
bookkeeping surfaces stay mechanically consistent with disk, and a declared closed list
of resident and doc-layer files stays free of declared skeleton-era narrative markers,
both enforced by the document-hygiene checker's red-first rules so narrative cannot lag
implementation silently.

## ADDED Requirements

### Requirement: Ledger bookkeeping surfaces are machine-consistent

The document-hygiene checker SHALL validate the `_backlog` ledger's bookkeeping
surfaces — each active directory's README (`plans/`, `bugs/`), the `_done/README.md`
counters, and each archive subdirectory's index README — as one consistency surface: a
work-item file present in an active or archive directory SHALL appear in that
directory's README list, a README list row SHALL reference a file that exists on disk
under the declared naming convention, and the counters and next-ID declarations in
`_done/README.md` SHALL match the authoritative index tables and the disk inventory.
The checker SHALL fail loudly naming the inconsistent surface, the row or file, and the
expected reconciliation; adding a bookkeeping surface to management is a visible change
to the declaring table.

#### Scenario: Consistent ledger passes

- **WHEN** the checker runs and every active/archive work-item file is indexed, every
  row resolves to disk, and the counters and next-ID declarations match
- **THEN** the checker exits 0

#### Scenario: Unindexed or dangling row fails loudly

- **WHEN** a work-item file exists on disk without an index row, or a row references a
  file name that does not exist on disk, or a counter disagrees with its authoritative
  table
- **THEN** the checker exits non-zero and names the surface, the offending row or file,
  and the reconciliation

### Requirement: Declared stale-narrative markers fail loudly

The checker SHALL validate a declared closed list of resident and doc-layer files
against a declared closed list of skeleton-era narrative markers (for example
"骨架占位", "skeleton)" as a module docstring claim on an implemented layer). A file
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
