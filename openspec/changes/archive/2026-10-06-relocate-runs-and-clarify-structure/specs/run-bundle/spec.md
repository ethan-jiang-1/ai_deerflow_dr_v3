# Spec Delta

## MODIFIED Requirements

### Requirement: Bundle directory contract is declared and exactly materialized

The run bundle SHALL live at `runs/{bucket}/{bundle_id}/` under the repository root —
outside the application subtree (`deep_research_harness/`) — with exactly the subtrees
`request/`, `work/`, `evidence/`, `final/`, `diagnostics/` plus `state.json` at the
bundle root, created by the `start` action; the v2 `synthesis/` and `review/` subtrees
SHALL NOT be created. All bundle path constants — including the runs-root directory
name — SHALL be declared in one pure domain module, and the runtime entry SHALL consume
that constant rather than re-declaring the name; no second path declaration SHALL exist
in the source tree. The resolved runs root SHALL be overridable by the
`DEEP_RESEARCH_RUNS_ROOT` environment variable (for tests, tools, and non-default
checkouts); when unset, the default SHALL be the repository-root `runs/` directory. The
`checkpoint.sqlite` location SHALL be part of the declared contract; a bundle started
before a run engine writes checkpoints SHALL legally lack the file, and a
present-but-unopenable checkpoint file SHALL fail loudly when accessed (never silently
ignored). Final reports SHALL be routed to `final/`, acceptance and evidence records to
`evidence/`, and process diagnostics to `diagnostics/`. Run state SHALL carry no
absolute filesystem paths, so a bundle directory relocated wholesale (as in the one-time
move from the retired `scopes/` root) SHALL remain fully readable and operable with no
migration step.

#### Scenario: Started bundle materializes the declared contract

- **WHEN** the `start` action creates a bundle
- **THEN** the bundle directory contains exactly `request/`, `work/`, `evidence/`,
  `final/`, `diagnostics/`, and `state.json`, and no `synthesis/` or `review/` subtree
  exists

#### Scenario: The default runs root sits outside the application subtree

- **WHEN** the runs root is resolved with no `DEEP_RESEARCH_RUNS_ROOT` override
- **THEN** it resolves to the repository-root `runs/` directory, which is not inside
  `deep_research_harness/`, and bundle data is created there

#### Scenario: The environment override redirects the runs root

- **WHEN** `DEEP_RESEARCH_RUNS_ROOT` names an existing directory before a command runs
- **THEN** bundle creation and resolution use that directory, and no bundle data is
  written under the default root

#### Scenario: Path constants come from the single domain module

- **WHEN** any harness code needs a bundle path, subtree name, or the runs-root
  directory name
- **THEN** it resolves it from the declared domain constants, and no second path
  declaration exists in the source tree

#### Scenario: A relocated legacy bundle stays operable

- **WHEN** a bundle directory created under the retired `scopes/` root is moved
  wholesale into the runs root
- **THEN** every action on that bundle behaves as before, because `state.json` and the
  bundle's records carry no absolute filesystem paths
