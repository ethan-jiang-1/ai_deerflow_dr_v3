# doc-truthfulness Specification

## Purpose

Owns the required behavior of the declaration-layer truthfulness gate: the ledger
bookkeeping surfaces stay mechanically consistent with disk, a declared closed list
of resident and doc-layer files stays free of declared stale-narrative markers, and
the root README's inventory counts stay machine-pinned — all enforced by the
document-hygiene checker's red-first rules so narrative cannot lag implementation
silently.

## MODIFIED Requirements

### Requirement: Ledger bookkeeping surfaces are machine-consistent

The document-hygiene checker SHALL validate the `_backlog` ledger's bookkeeping
surfaces — each active directory's README (`plans/`, `bugs/`), the `_done/README.md`
counters, and each archive subdirectory's index README — as one consistency surface:
a work-item file present in an active or archive directory SHALL appear in that
directory's README list, a README list row SHALL reference a file that exists on disk
under the declared naming convention, the counters and next-ID declarations in
`_done/README.md` SHALL match the authoritative index tables and the disk inventory,
and every work-item row SHALL sit inside its declared table — contiguous with the
table header block it belongs to, not separated from it by blank lines, prose, or
fenced content. The checker SHALL fail loudly naming the inconsistent surface, the
row or file, its placement, and the expected reconciliation; adding a bookkeeping
surface to management is a visible change to the declaring table.

#### Scenario: Consistent ledger passes

- **WHEN** the checker runs and every active/archive work-item file is indexed, every
  row resolves to disk, the counters and next-ID declarations match, and every row is
  contiguous with its table
- **THEN** the checker exits 0

#### Scenario: Unindexed or dangling row fails loudly

- **WHEN** a work-item file exists on disk without an index row, or a row references a
  file name that does not exist on disk, or a counter disagrees with its authoritative
  table
- **THEN** the checker exits non-zero and names the surface, the offending row or file,
  and the reconciliation

#### Scenario: A row separated from its table fails loudly

- **WHEN** a work-item row is separated from its table header block by a blank line,
  prose, or a fenced code block — or lands after other content while its table is
  elsewhere in the file
- **THEN** the checker exits non-zero and names the surface, the row, and the
  placement defect

## ADDED Requirements

### Requirement: Root README inventory counts are machine-pinned

The document-hygiene checker SHALL compute the number of capability specs under
`openspec/specs/` and the number of archived changes under `openspec/changes/archive/`
directly from disk, and SHALL require the root `README.md` status line to declare
exactly those two numbers. A declared count that differs from the computed inventory
SHALL fail loudly naming both the computed and the declared values. The rule SHALL
match the status line structurally (the declared count pattern anchored to its
inventory nouns), not to a byte-exact sentence, so wording may evolve without
weakening the pin.

#### Scenario: Matching counts pass

- **WHEN** the checker runs and the root README declares exactly the computed
  capability-spec and archived-change counts
- **THEN** the checker exits 0

#### Scenario: A drifted count fails loudly

- **WHEN** the computed inventory differs from the counts declared in the root README
  status line
- **THEN** the checker exits non-zero naming both the computed and the declared values
