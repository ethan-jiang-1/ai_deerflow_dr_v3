> req: RUB-001

# Spec Delta

## MODIFIED Requirements

### Requirement: state.json is the single run-state authority with revision CAS

`state.json` SHALL be the only authority for run status, thread id, prior thread lineage, owner PID, deerflow
pin commit, generation, composition, and clarification-continuation state. Every state
write SHALL carry the writer's observed revision and SHALL be rejected loudly, naming the
expected and actual revisions, when the stored revision is not that value; a successful
write SHALL atomically replace the file and increment the revision. Readers SHALL see a
fully written state file or a loud read failure, never a torn write.

#### Scenario: Conflicting write is rejected naming revisions

- **WHEN** two writers read revision N and both attempt to write
- **THEN** exactly one write succeeds to revision N+1 and the other fails with a
  violation naming expected N and actual N+1

#### Scenario: State file is atomically replaced

- **WHEN** a state write succeeds
- **THEN** the file content is replaced atomically (no partially written state is ever
  observable by a reader)

### Requirement: Lifecycle transitions are legal-only and fail loudly

The state machine SHALL allow exactly the transitions: `start` creates a bundle in
`active`; `cancel` records a cancellation request on an `active` bundle; `refine` on a
terminal state (`completed`, `cancelled`, `failed-resume`) creates generation+1 and
returns the bundle to `active`; the run-terminal transitions into `completed`,
`cancelled`, and `failed-resume` follow the declared rules. Any other requested
transition SHALL be rejected loudly naming the current state, requested action, and
reason.

#### Scenario: Illegal transition is rejected

- **WHEN** `refine` is requested on an `active` bundle
- **THEN** the action fails naming current state `active`, the requested action, and the
  legal precondition

#### Scenario: Fresh-thread refine restarts light with recorded lineage

- **WHEN** `refine` is requested on a terminal bundle with a fresh context document
- **THEN** the bundle returns to `active` on a new thread id, the prior thread is
  appended to the recorded lineage, and the seed document lands in `request/`

#### Scenario: Refine creates the next generation

- **WHEN** `refine` is requested on a `completed` bundle with direction text
- **THEN** the bundle returns to `active` with generation incremented by one and the
  direction text recorded in the bundle