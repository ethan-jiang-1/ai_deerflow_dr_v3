# entry-surface Delta

## MODIFIED Requirements

### Requirement: Six verbs mirror the state machine and observation layers

The CLI SHALL expose exactly `create`, `status`, `watch`, `cancel`, `refine`,
`inspect`, and `diagnose`; each SHALL delegate to the owning runtime action and SHALL
add no second state authority. `create` SHALL start a bundle (configuration selected
explicitly, `fixture` by default) and drive the run engine in the foreground with the
live human view; `status` SHALL report state, journal summary, and owner-PID liveness;
`watch` SHALL render the journal projection until the run reaches a terminal state,
then exit; `cancel` SHALL record the cancellation request; `refine` SHALL require
non-empty direction text, enter the next generation, and then drive the run engine in
the foreground over that generation's direction document — continuing the bundle's
declared composition ladder (no fresh ladder choice; an unwired composition SHALL fail
loudly naming it) — ending at a typed terminal state with the same terminal output and
environment-remedy behavior as `create`; `inspect` SHALL render the journal timeline,
the admitted evidence, the assembly snapshot, and the checkpoint thread summary when
the framework is available; `diagnose` SHALL read the bundle's persisted facts — the
typed state, the journal's terminal and lifecycle entries, and the existence of
diagnostics artifacts — and SHALL render a classified failure diagnosis: the terminal
outcome classified into the declared classes (model-call failure carrying the
framework-reported error type; framework crash carrying the exception name; framework
stop reason; clarification bound exhausted pointing at the unanswered-clarifications
artifact; operator cancellation; owner-death transfer detected from a live state whose
owner PID is gone; completed-but-undelivered when the terminal state carries no
recorded delivery), the chain stage that owns the failing condition, and the concrete
evidence files for the class. An active run SHALL be reported as still running and
SHALL NOT be classified. `diagnose` SHALL be a projection only: it SHALL NOT modify
state, journal, or any bundle artifact, and its classification SHALL NOT become
lifecycle authority. Any other command SHALL be rejected loudly naming the legal set.

#### Scenario: Every verb delegates and unknown verbs fail

- **WHEN** each of the seven verbs runs against a fixture bundle, and an unknown verb
  is requested
- **THEN** each verb produces the substrate's declared behavior, and the unknown verb
  fails naming the legal command set

#### Scenario: Refined generation runs to an honest terminal

- **WHEN** `refine` runs on a terminal fixture bundle with direction text
- **THEN** the next generation is created, the run engine is driven in the foreground
  over the direction document, and the command exits after printing a typed terminal
  state for that generation

#### Scenario: Each terminal class renders its classification and evidence pointers

- **WHEN** `diagnose` runs on bundles whose persisted facts represent each declared
  class (a model-call fallback with its error type, a framework crash with its
  exception name, a stop reason, an exhausted clarification bound, a cancellation, a
  live state with a dead owner PID, and a completed state without a recorded delivery)
- **THEN** each run names its class, the owning chain stage, and the evidence files
  for that class, and no two classes collide on the same persisted facts

#### Scenario: Diagnose is read-only and never classifies an active run

- **WHEN** `diagnose` runs on an active bundle, and the bundle's state, journal, and
  diagnostics files are compared before and after the command
- **THEN** the output reports the run as still running without a terminal
  classification, and every bundle artifact is byte-identical afterwards

#### Scenario: The diagnosis journey classifies a real failed run

- **WHEN** a fixture create is driven to a model-call failure on the real CLI
  subprocess, and `diagnose` runs on the resulting bundle
- **THEN** the classification names the model-call failure class with the
  framework-reported error type and points at the diagnostics evidence, with no
  credential required
