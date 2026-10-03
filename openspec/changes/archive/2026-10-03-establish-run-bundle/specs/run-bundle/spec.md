> req: RUB-001

# Spec Delta

## Purpose

Owns the required behavior of the run bundle substrate: the declared directory contract
for a run's durable record, a single-authority state machine over `state.json` with
revision CAS and directory-lease liveness, fail-loud crash detection and bounded
clarification-continuation state, a bounded append-only journal that never evicts
admission anchors, permanent deletion semantics, and the recorded run composition.

## ADDED Requirements

### Requirement: Bundle directory contract is declared and exactly materialized

The run bundle SHALL live at `scopes/{bucket}/{bundle_id}/` with exactly the subtrees
`request/`, `work/`, `evidence/`, `final/`, `diagnostics/` plus `state.json` at the
bundle root, created by the `start` action; the v2 `synthesis/` and `review/` subtrees
SHALL NOT be created. All bundle path constants SHALL be declared in one pure domain
module. The `checkpoint.sqlite` location SHALL be part of the declared contract; a bundle
started before a run engine writes checkpoints SHALL legally lack the file, and a
present-but-unopenable checkpoint file SHALL fail loudly when accessed (never silently
ignored). Final reports SHALL be routed to `final/`, acceptance and evidence records to
`evidence/`, and process diagnostics to `diagnostics/`.

#### Scenario: Started bundle materializes the declared contract

- **WHEN** the `start` action creates a bundle
- **THEN** the bundle directory contains exactly `request/`, `work/`, `evidence/`,
  `final/`, `diagnostics/`, and `state.json`, and no `synthesis/` or `review/` subtree
  exists

#### Scenario: Path constants come from the single domain module

- **WHEN** any harness code needs a bundle path or subtree name
- **THEN** it resolves it from the declared domain constants, and no second path
  declaration exists in the source tree

### Requirement: state.json is the single run-state authority with revision CAS

`state.json` SHALL be the only authority for run status, thread id, owner PID, deerflow
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

### Requirement: Every write revalidates the directory lease

Before any write into a bundle, the writer SHALL revalidate that the bundle directory's
identity (`st_dev`, `st_ino`) still matches the identity recorded when the handle was
opened; a mismatch SHALL be rejected loudly naming the lease violation, with no repair
attempted.

#### Scenario: Replaced directory rejects the write

- **WHEN** a bundle directory is deleted and recreated (new identity) before a writer's
  next write
- **THEN** the write is rejected with a lease violation naming the identity mismatch

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

#### Scenario: Refine creates the next generation

- **WHEN** `refine` is requested on a `completed` bundle with direction text
- **THEN** the bundle returns to `active` with generation incremented by one and the
  direction text recorded in the bundle

### Requirement: A dead owner PID transfers active to failed-resume

The `status` action SHALL check the recorded owner PID's liveness; when the state says
`active` and the owner PID is dead, `status` SHALL transfer the bundle to
`failed-resume`, append a journal `terminal` entry naming the detection reason, and
report the failure loudly — never reporting a live-seeming state.

#### Scenario: Dead owner is detected on status

- **WHEN** `status` observes an `active` bundle whose recorded owner PID no longer exists
- **THEN** the bundle state becomes `failed-resume`, the journal gains a `terminal`
  entry naming the dead-PID detection, and the status report states the failure

### Requirement: Clarification continuation is bounded and records its count

The state machine SHALL carry `auto_proceed_count` and the configured bound (N=2) in
`state.json`. Whether a stream terminal contains an unanswered `ask_clarification` call
SHALL be decided by a pure detection function; when continuation is detected, the bound
allows at most N automatic continuation rounds, the count is recorded in `state.json`,
and exhausting the bound SHALL transfer the bundle to `failed-resume` with the unanswered
question text preserved in `diagnostics/`. The client re-invocation loop itself is owned
by the wiring change.

#### Scenario: Exhausting the continuation bound transfers to failed-resume

- **WHEN** the detection function reports an unanswered clarification and
  `auto_proceed_count` already equals the bound
- **THEN** the transition rule returns `failed-resume` with the question text routed to
  `diagnostics/`

### Requirement: The journal is bounded, append-only, and never evicts admission anchors

The journal SHALL live at `diagnostics/journal.jsonl` as append-only JSONL entries whose
category belongs to the closed set `admission`, `lifecycle`, `model_tool`, `subagent`,
`validation`, `submit`, `exhaustion`, `terminal`; any other category SHALL be rejected
loudly. Retention SHALL be bounded (by entry count) with priority eviction, and
`admission` entries SHALL never be evicted; periodic compaction SHALL preserve all
`admission` entries plus the most recent tail. A corrupted journal tail SHALL fail the
read loudly naming the corruption site instead of being silently truncated.

#### Scenario: Eviction never touches admission anchors

- **WHEN** the journal exceeds its bound and eviction runs
- **THEN** every `admission` entry remains present and only lower-priority entries are
  evicted

#### Scenario: Illegal category is rejected

- **WHEN** a write attempts a journal entry outside the closed category set
- **THEN** the write fails loudly naming the illegal category

#### Scenario: Corrupted tail fails loudly

- **WHEN** the journal file contains a truncated or unparsable tail entry
- **THEN** reading fails naming the corruption site instead of silently dropping it

### Requirement: Deletion is permanent and honestly reported

Bundle discovery SHALL be directory scanning with no registry. Deleting a bundle
directory SHALL be permanent: there SHALL be no recovery path, no silent migration, and
no second authority; any later action on the deleted bundle SHALL report loudly and in
human-readable terms that the bundle is permanently unavailable.

#### Scenario: Deleted bundle reports permanent unavailability

- **WHEN** an action targets a bundle id whose directory no longer exists
- **THEN** the action fails with a human-readable permanent-unavailability report and
  creates nothing

### Requirement: Composition is recorded at start

The `start` action SHALL record the run composition (`fixture`, `mixed`, or `all_real`)
in `state.json`; any other value SHALL be rejected loudly at the boundary.

#### Scenario: Illegal composition is rejected at start

- **WHEN** `start` is called with a composition outside the closed set
- **THEN** the action fails loudly naming the illegal value and the bundle is not created
