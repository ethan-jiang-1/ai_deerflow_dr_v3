# Spec Delta

## MODIFIED Requirements

### Requirement: state.json is the single run-state authority with revision CAS

`state.json` SHALL be the only authority for run status, thread id, prior thread lineage, owner PID, deerflow
pin commit, generation, composition, clarification-continuation state, and the per-generation
delivery disposition — the orthogonal delivered-fact of the run's final answer
(`admitted` with its artifact path, `rejected`, `no-answer`, or not recorded). Every state
write SHALL carry the writer's observed revision and SHALL be rejected loudly, naming the
expected and actual revisions, when the stored revision is not that value; a successful
write SHALL atomically replace the file and increment the revision. Readers SHALL see a
fully written state file or a loud read failure, never a torn write. A state file written
before the delivery field existed SHALL read as delivery not recorded, never as an error;
the delivery disposition SHALL be written after the terminal write through the same
revision-CAS path (the process fact lands first, the delivery fact enriches it), and the
terminal-status rules SHALL remain unchanged by delivery values.

#### Scenario: Conflicting write is rejected naming revisions

- **WHEN** two writers read revision N and both attempt to write
- **THEN** exactly one write succeeds to revision N+1 and the other fails with a
  violation naming expected N and actual N+1

#### Scenario: State file is atomically replaced

- **WHEN** a state write succeeds
- **THEN** the file content is replaced atomically (no partially written state is ever
  observable by a reader)

#### Scenario: Delivery disposition is a first-class state fact

- **WHEN** a run reaches `completed` and its final answer is submitted, or the answer is
  empty and nothing is submitted
- **THEN** the state carries the generation's delivery disposition (`admitted` with the
  artifact path, `rejected`, or `no-answer`) written after the terminal write via the
  CAS path, and a pre-change state file without the field reads as delivery not recorded
