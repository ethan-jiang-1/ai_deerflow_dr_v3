# doc-truthfulness Delta

## MODIFIED Requirements

### Requirement: Ledger bookkeeping surfaces are machine-consistent

The document-hygiene checker SHALL validate the `_backlog` ledger's bookkeeping
surfaces — each active directory's README (`issues/`, `bugs/`), the `_archived/README.md`
counters, and each archive subdirectory's index README (`_fixed_bugs/`,
`_suspended_bugs/`, `_settled_issues/`, `_suspended_issues/`) — as one consistency
surface: a work-item file present in an active or archive directory SHALL appear in that
directory's README list, a README list row SHALL reference a file that exists on disk
under the declared naming convention, and the counters and next-ID declarations in
`_archived/README.md` SHALL match the authoritative index tables and the disk inventory.
The checker SHALL additionally validate next-ID declarations in the ledger READMEs: each
numbered ledger README (`issues/`, `bugs/`, `_fixed_bugs/`, `_settled_issues/`) SHALL
carry at most one "Next available … ID" declaration line per ID prefix, and any
declaration it carries SHALL equal the next ID derived by the ledger's allocation rule
(the maximum allocated number across the archive index table, the archive work items,
and the active work items, plus one) — a duplicated declaration or a declaration whose
value disagrees with the derivation SHALL fail loudly even when the counters table alone
stays consistent (BUG-002: a stale header declaration coexisted with a correct body
declaration and the checker stayed green). The checker SHALL additionally validate card
hukou and residency: every work-item card in an active directory SHALL carry a `状态：`
field within its first 12 lines whose word is a member of that surface's declared status
vocabulary, and an active card whose status line declares the graduation field as passed
(`毕业门` value `已过`) or declares `可关闭：是` SHALL fail until it leaves the active
directory — the match SHALL anchor on those declared fields only, so awaiting-human
(`等人拍板`) and not-yet-graduated (`未过`) cards never fail. The checker SHALL fail
loudly naming the inconsistent surface, the row or file, and the expected
reconciliation; adding a bookkeeping surface, a status vocabulary, or a
graduation-anchored field to management is a visible change to the declaring tables.
Archived cards are out of scope for the hukou and residency checks (grandfathered), and
renaming a category SHALL update the declaring surface tables and the structural
manifest in the same revision that moves the directories.

#### Scenario: Consistent ledger passes

- **WHEN** the checker runs and every active/archive work-item file is indexed, every
  row resolves to disk, the counters and next-ID declarations match, every ledger README
  carries at most one declaration per prefix whose value equals the allocation-derived
  next ID, every active card carries a vocabulary-checked `状态：` hukou, and no active
  card declares a passed graduation field or `可关闭：是`
- **THEN** the checker exits 0

#### Scenario: Unindexed or dangling row fails loudly

- **WHEN** a work-item file exists on disk without an index row, or a row references a
  file name that does not exist on disk, or a counter disagrees with its authoritative
  table
- **THEN** the checker exits non-zero and names the surface, the offending row or file,
  and the reconciliation

#### Scenario: Duplicated or contradictory next-ID declaration fails loudly

- **WHEN** a ledger README carries more than one next-ID declaration for a prefix, or a
  single declaration whose value differs from the allocation-derived next ID
- **THEN** the checker exits non-zero naming the file and the conflicting or disagreeing
  declarations

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
