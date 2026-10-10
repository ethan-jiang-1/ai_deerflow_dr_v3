# ci-governance Delta

## MODIFIED Requirements

### Requirement: The enforcement declarations are guarded against drift

The CI workflow file, the hook script, and the ci-governance checker SHALL be declared in
the structural inventory, so their deletion fails architecture governance. A dedicated
ci-governance checker SHALL machine-validate that the workflow declares the required
triggers and invokes each canonical governance command, and that the hook is wired to the
declared hooks path. The checker SHALL additionally cross-check the workflow's pinned
OpenSpec CLI generation against the generation recorded in the skills frontmatter
(`.agents/skills/*/SKILL.md` `generatedBy`): a workflow pin that disagrees with the
recorded generation, a missing or ambiguous generation record, SHALL fail loudly naming
both sides — two declarations may not drift together silently by corroborating only each
other. A workflow that stops invoking a canonical command, or a hook that gains a
forbidden command, SHALL fail the checker.

#### Scenario: Deleted workflow fails governance

- **WHEN** the CI workflow file or hook script is removed from the tree
- **THEN** architecture governance fails with a missing required path

#### Scenario: Gutted workflow fails the checker

- **WHEN** the workflow no longer declares push and pull-request triggers, or no longer
  invokes one of the canonical governance commands
- **THEN** the ci-governance checker exits non-zero and names the missing declaration

#### Scenario: Forbidden hook command fails the checker

- **WHEN** the hook script gains a test, snapshot, type-analysis, or build invocation
- **THEN** the ci-governance checker exits non-zero and names the forbidden command

#### Scenario: CLI generation drift fails the checker

- **WHEN** the workflow's pinned OpenSpec CLI version disagrees with the skills
  frontmatter's `generatedBy`, or the generation record is missing or ambiguous
- **THEN** the ci-governance checker exits non-zero naming the workflow pin and the
  recorded generation
