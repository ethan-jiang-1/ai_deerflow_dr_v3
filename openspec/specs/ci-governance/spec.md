# ci-governance Specification

## Purpose

Owns the required behavior of the acceptance path: the governance suite is machine-forced
on every push and pull request through a single-job CI workflow, the local pre-commit hook
runs only cheap high-confidence checks, and the CI and hook declarations are themselves
machine-validated so the enforcement surface cannot drift silently.

## Requirements

### Requirement: CI runs the governance suite on the acceptance path

The repository SHALL run a single-job CI workflow on every push and on every pull request
that touches the governance surfaces (any path under `openspec/`, the harness tree, the
workflow file, or the hooks directory), and SHALL additionally accept a manual
`workflow_dispatch` run started by an operator with write access against the current
HEAD — the manual path re-runs the same canonical sequence and grants no new permission
or skip. The workflow SHALL check out the repository with
submodules (the architecture checker validates nested gitlink metadata), SHALL set up a
pinned Python and the pinned OpenSpec CLI version, and SHALL run the canonical governance
sequence — the governance unittest suite, the aggregate closeout gate, the standalone
document-hygiene checker, the harness `make verify`, the harness integration smoke
(`make smoke`), and the harness lint (`make lint`) — failing the job on any non-zero
exit. The workflow SHALL NOT split these checks across jobs or add platform matrices; the
exhaustive set stays in one deterministic job.

#### Scenario: Conforming push passes

- **WHEN** a push lands on a tree whose governance suite is fully green
- **THEN** the CI job runs every canonical step and exits green

#### Scenario: A red component blocks the job

- **WHEN** any canonical step exits non-zero (for example a governance unittest failure or
  an aggregate-gate violation)
- **THEN** the CI job fails and the push is flagged

#### Scenario: Path-filtered triggers

- **WHEN** a change touches nothing under the declared governance paths
- **THEN** the workflow does not run, and no unrelated surface can force or skip the gate
  by editing unrelated files

#### Scenario: Manual dispatch re-runs the gate on HEAD

- **WHEN** an operator with write access dispatches the workflow manually against the
  current HEAD
- **THEN** the same single job runs the full canonical sequence with no skipped or
  additional step, and its verdict reflects the HEAD tree exactly

### Requirement: The local hook stays cheap and high-confidence

The repository SHALL provide a versioned pre-commit hook activated once per clone via the
declared hooks path. The hook SHALL run only cheap high-confidence checks — the staged
whitespace check and the standalone document-hygiene checker — and SHALL complete without
network access or project installation. Tests, snapshots, type analysis, builds, and any
check whose cost varies with the changed surface SHALL NOT run in the hook; those belong
to CI.

#### Scenario: Staged whitespace error is rejected

- **WHEN** a commit is staged containing whitespace errors detectable by the staged diff
  check
- **THEN** the hook exits non-zero and names the offending paths

#### Scenario: The hook never runs the suites

- **WHEN** the hook script's declared command set is inspected
- **THEN** it contains only the two declared cheap checks and no test, snapshot,
  type-analysis, or build invocation

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
