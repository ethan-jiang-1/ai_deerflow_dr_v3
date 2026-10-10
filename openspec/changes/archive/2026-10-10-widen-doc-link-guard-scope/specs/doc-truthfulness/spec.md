# doc-truthfulness Delta

## ADDED Requirements

### Requirement: Managed doc surfaces' relative links resolve on disk

The document-hygiene checker SHALL validate that every relative Markdown link in the
managed doc surfaces resolves to an existing path on disk. The managed surfaces are a
declared closed list: the entry-chain documents and the docs-layer documents already
managed by the checker, plus the harness test-assets documents
(`deep_research_harness/tests/README.md`, `deep_research_harness/tests/fixtures/README.md`)
and the tools document (`deep_research_harness/tools/README.md`). A link whose target
path does not exist SHALL fail loudly naming the file and the target. External
(`http://`, `https://`, `mailto:`), anchor-only, and empty targets SHALL be skipped;
fragment and query suffixes SHALL not participate in existence checking. Anchors SHALL
NOT be validated for existence: line anchors track implementations and are excluded by
declared limitation, not by omission. Expanding the managed-surface list is a visible
change to the declaring table; archived work-item and change surfaces
(`openspec/changes/archive/`, `_backlog/_archived/`) are historical context under their
own lifecycle policy and SHALL NOT be swept by this rule.

#### Scenario: Managed surfaces with resolvable links pass

- **WHEN** the checker runs and every relative link in the managed surfaces resolves
  to an existing path on disk
- **THEN** the checker exits 0

#### Scenario: A dead link in an asset document fails loudly

- **WHEN** a managed asset document carries a relative link whose target path does not
  exist on disk
- **THEN** the checker exits non-zero naming the file and the dead target

#### Scenario: The rule proves it can fail (self-test)

- **WHEN** the checker's self-test battery builds a temporary tree whose asset document
  contains a dead relative link
- **THEN** the rule reports the violation, and the battery's negative control passes
  only because the violation is detected
