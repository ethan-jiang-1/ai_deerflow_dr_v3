
# entry-surface Specification

## Purpose

Owns the required behavior of the human command surface: six thin verbs over the
existing substrate — create, status, watch, cancel, refine, inspect — a shared
human rendering vocabulary for the live view and the journal projection, the
two-ladder configuration selection, and the EV2 evidence (journey smoke, golden
replay).

## Requirements

### Requirement: Six verbs mirror the state machine and observation layers

The CLI SHALL expose exactly `create`, `status`, `watch`, `cancel`, `refine`, and
`inspect`; each SHALL delegate to the owning runtime action and SHALL add no second
state authority. `create` SHALL start a bundle (configuration selected explicitly,
`fixture` by default) and drive the run engine in the foreground with the live human
view; `status` SHALL report state, journal summary, and owner-PID liveness; `watch`
SHALL render the journal projection until the run reaches a terminal state, then exit;
`cancel` SHALL record the cancellation request; `refine` SHALL require non-empty
direction text, enter the next generation, and then drive the run engine in the
foreground over that generation's direction document — continuing the bundle's
declared composition ladder (no fresh ladder choice; an unwired composition SHALL
fail loudly naming it) — ending at a typed terminal state with the same terminal
output and environment-remedy behavior as `create`; `inspect` SHALL render the journal
timeline, the admitted evidence, the assembly snapshot, and the checkpoint thread
summary when the framework is available. Any other command SHALL be rejected loudly
naming the legal set.

#### Scenario: Every verb delegates and unknown verbs fail

- **WHEN** each of the six verbs runs against a fixture bundle, and an unknown verb is
  requested
- **THEN** each verb produces the substrate's declared behavior, and the unknown verb
  fails naming the legal command set

#### Scenario: Refined generation runs to an honest terminal

- **WHEN** `refine` runs on a terminal fixture bundle with direction text
- **THEN** the next generation is created, the run engine is driven in the foreground
  over the direction document, and the command exits after printing a typed terminal
  state for that generation

### Requirement: One rendering vocabulary serves the live view and the projection

The live view and the journal projection SHALL share a single rendering module whose
output is deterministic human-readable text (tool calls, state changes, dispositions,
and terminal reasons render as stable human phrases). The run engine SHALL accept an
optional event hook (the live view's sink) without altering the journal or terminal
rules; the watch projection SHALL render journal entries, not raw events.

#### Scenario: Renderer strings are stable across live view and projection

- **WHEN** the same tool call is rendered from the live stream and later from the
  journal projection
- **THEN** both renderings use the same human phrase for the tool and the arguments

### Requirement: The watch projection is bounded and terminal-exiting

`watch` SHALL tail the journal from its current position, rendering new entries as
they appear, and SHALL exit after rendering a `terminal` entry (or when the run is
already terminal, after rendering the recent history). Watching a bundle whose run is
terminal SHALL render history and exit, never wait.

#### Scenario: Watch exits on the terminal entry

- **WHEN** a watched run journals its terminal entry
- **THEN** watch renders the terminal line and exits zero

### Requirement: The two-ladder selection is explicit

`create` SHALL require the configuration ladder choice to resolve explicitly —
`fixture` by default (zero-credential rehearsal through the harness-owned fakes) and
`base` for the real run (credentials via `$VAR` resolved by the framework); an unknown
ladder name SHALL fail loudly naming the legal set.

#### Scenario: Fixture default runs without credentials

- **WHEN** `create` runs with no configuration argument
- **THEN** the fixture configuration drives the real client chain over the scripted
  providers, with no credential required

### Requirement: The EV2 evidence accompanies the surface

The change SHALL land: a journey integration test walking create → watch → status →
refine → inspect over the fixture ladder; a negative control per new guard (unknown
verb, unknown ladder, missing bundle, refine on non-terminal, watch on terminal run);
and a recorded replay golden (a real failure scenario recorded as JSON and replayed
through the renderer with shape-stable assertions).

#### Scenario: The golden replay pins the rendered shape

- **WHEN** the recorded clarification-exhaustion scenario replays through the renderer
- **THEN** the rendered timeline matches the recorded shape (stable phrases and
  ordering, volatile values excluded)
