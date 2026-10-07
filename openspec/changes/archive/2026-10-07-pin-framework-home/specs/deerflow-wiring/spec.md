# deerflow-wiring Delta

## ADDED Requirements

### Requirement: The framework home is pinned outside the application subtree

The binding SHALL explicitly set the framework's home directory
(`DEER_FLOW_HOME`) to a fixed location outside the application subtree — the
repository-root `.deer-flow/` — before any framework import or client
construction in a run, and SHALL NOT rely on the framework's
checkout-relative default. The resolved home SHALL always be outside the
module guide's source root; a pin that resolves inside the application
subtree SHALL fail loudly. Framework runtime state (memory retrieval stores,
skill projections, user data) SHALL live only under the pinned home; the
application tree holds product code, tests, docs, config, and tools only.
The pin is configuration of where the framework writes, not an assertion
about what it writes: activation semantics stay with their owning change.

#### Scenario: The pin resolves outside the application subtree

- **WHEN** the binding resolves the framework home in a checkout whose
  application tree is the module guide's source root
- **THEN** the pinned path is the repository-root `.deer-flow/`, the
  `DEER_FLOW_HOME` environment is set to it before client construction, and
  the path is not inside the application subtree

#### Scenario: An in-subtree resolution fails loudly

- **WHEN** the home resolution would place the framework home inside the
  application subtree
- **THEN** the pin fails loudly naming the resolved path and the boundary

#### Scenario: Run-state writes land under the pinned home

- **WHEN** a fixture-ladder run executes on the real CLI subprocess after the
  pin
- **THEN** the framework runtime state it writes appears under the pinned
  repository-root home and no framework state directory is created inside the
  application subtree
