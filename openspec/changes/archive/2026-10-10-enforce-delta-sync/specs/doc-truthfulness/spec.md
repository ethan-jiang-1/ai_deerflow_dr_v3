# doc-truthfulness Delta

## ADDED Requirements

### Requirement: Archived ADDED requirements are machine-pinned into main specs

The specification checker SHALL validate, in its full-tree mode, that every
requirement title an archived change's delta declares under `## ADDED
Requirements` for a capability is present as a requirement title in that
capability's main spec under `openspec/specs/`, failing loudly naming the
archiving change, the capability, and the missing title. The rule SHALL fail
loudly when an archived ADDED requirement belongs to a capability that has no
main spec. The rule SHALL exempt a title that a later archived delta for the
same capability carries under `## REMOVED Requirements` or `## RENAMED
Requirements` (including a RENAMED section's `#### FROM:` line) — a formally
recorded retirement — and SHALL honor a declared allowlist of
capability-and-title pairs whose entries each carry a recorded justification
for out-of-band repairs (for example a rename applied by an audit repair while
absorbing a missed sync); an allowlist entry without a justification SHALL
fail loudly. Archive ordering follows the archive's date-prefixed change
names; same-day ordering is an approximation declared by limitation.
Requirement titles under `## MODIFIED Requirements` are deliberately not
pinned by this rule — out-of-band renames surface as allowlisted stale
titles — an exclusion by declared limitation, not by omission.

#### Scenario: A synced archive passes

- **WHEN** the checker runs in full-tree mode and every archived ADDED
  requirement title is present in its capability's main spec, exempted by a
  later formal retirement, or covered by a justified allowlist entry
- **THEN** the checker exits 0

#### Scenario: A skipped spec update fails loudly

- **WHEN** an archived change ADDED a requirement that no later delta retired
  and no allowlist entry covers, and the main spec lacks the title
- **THEN** the checker exits non-zero naming the change, the capability, and
  the missing title

#### Scenario: A formally retired title is exempt

- **WHEN** an archived change ADDED a title and a later archived delta for the
  same capability carries that title under REMOVED or RENAMED
- **THEN** the absence of the title from the main spec is not a violation

#### Scenario: An out-of-band rename is allowlisted with justification

- **WHEN** a capability's main spec carries a requirement under a title that
  differs from the title an archived change ADDED, and the allowlist covers
  the pair with a recorded justification
- **THEN** the checker exits 0 for that pair, and an entry lacking a
  justification fails loudly

#### Scenario: The rule proves it can fail (red-first fixtures)

- **WHEN** the governance unittest suite builds a temporary tree whose
  archived delta ADDS a requirement the main spec lacks
- **THEN** the rule reports the violation naming the change, the capability,
  and the title, and the suite's negative control passes only because the
  violation is detected
