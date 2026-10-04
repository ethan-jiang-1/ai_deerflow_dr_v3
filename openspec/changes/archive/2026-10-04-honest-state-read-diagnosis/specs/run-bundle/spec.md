# run-bundle Specification

## MODIFIED Requirements

### Requirement: state.json is the single run-state authority with revision CAS

`state.json` SHALL be the only authority for run status, thread id, prior thread lineage, owner PID, deerflow
pin commit, generation, composition, and clarification-continuation state. Every state
write SHALL carry the writer's observed revision and SHALL be rejected loudly, naming the
expected and actual revisions, when the stored revision is not that value; a successful
write SHALL atomically replace the file and increment the revision. Readers SHALL see a
fully written state file or a loud read failure, never a torn write. A loud read
failure SHALL distinguish the two absence shapes: when the bundle directory itself is
absent, the reader SHALL report the bundle as unavailable under the permanent-deletion
semantics; when the directory is present but the state file is not, the reader SHALL
report state corruption carrying the read evidence (failure phase and the directory's
temporary-file siblings).

#### Scenario: Conflicting write is rejected naming revisions

- **WHEN** two writers read revision N and both attempt to write
- **THEN** exactly one write succeeds to revision N+1 and the other fails with a
  violation naming expected N and actual N+1

#### Scenario: State file is atomically replaced

- **WHEN** a state write succeeds
- **THEN** the file content is replaced atomically (no partially written state is ever
  observable by a reader)

#### Scenario: Directory-level absence is not misreported as file corruption

- **WHEN** the bundle directory is transiently absent at read time (external
  interference, move, or deletion), and separately when the directory is present but
  the state file is absent
- **THEN** the first shape reports the bundle as unavailable, and the second reports
  state corruption carrying the read evidence — the two shapes are never conflated
