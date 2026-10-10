# ci-governance Delta

## MODIFIED Requirements

### Requirement: CI runs the governance suite on the acceptance path

The repository SHALL run a single-job CI workflow on every push and on every pull request
that touches the governance surfaces (any path under `openspec/`, the harness tree, the
workflow file, or the hooks directory). The workflow SHALL check out the repository with
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
