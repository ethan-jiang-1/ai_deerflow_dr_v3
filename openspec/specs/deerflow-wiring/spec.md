> req: DEW-001

# deerflow-wiring Specification

## Purpose

Owns the required behavior of the embedded DeerFlow binding: explicit config
resolution with no auto-discovery, a contract mirror locked to the real client surface
by test, the per-run assembly snapshot, and a terminal-honest run engine that feeds the
journal, applies the bounded clarification continuation, and hands checkpoints to the
bundle's sync saver.

## Requirements

### Requirement: Configuration resolution is explicit and never auto-discovered

Constructing the harness client binding SHALL require an explicit configuration path
resolving to a checked-in configuration (`base` or `fixture`); the binding SHALL NOT
fall back to framework default discovery, and an ambiguous or missing path SHALL fail
loudly at construction naming the requested configuration. The checked-in
configurations SHALL be shape/secret separated: shape lives in the configuration file,
credentials are `$VAR` references resolved from the environment by the framework.

#### Scenario: Explicit path is honored and ambiguity fails

- **WHEN** the binding is constructed with an explicit existing configuration path
- **THEN** the framework client is constructed with exactly that `config_path`; a
  missing path fails construction naming the requested configuration

#### Scenario: Fixture configuration runs the real chain with fakes

- **WHEN** the fixture configuration is selected
- **THEN** its `use:` seams resolve to harness-owned fake model and search providers,
  and the real client chain runs end-to-end with zero credentials

### Requirement: The contract mirror locks every borrowed surface

The mirror SHALL declare typed definitions of each borrowed surface — the client
constructor parameters, the stream event shapes (`values`, `messages-tuple`, `custom`,
`end`), and the checkpointer seam — in `runtime/contracts/`. A contract test SHALL
compare the mirror against the real framework surface and SHALL fail, naming the
drifted surface, when they disagree. The mirror captures interface shape only; no
framework implementation is copied.

#### Scenario: Drifted framework surface fails the contract test

- **WHEN** the framework's public client surface changes relative to the mirror
- **THEN** the contract test fails naming the drifted parameter or event shape

#### Scenario: The mirror is shape only

- **WHEN** the mirror sources are inspected
- **THEN** they contain typed declarations and documentation of the framework surface,
  and no framework implementation code

### Requirement: The run engine consumes the stream with terminal honesty

The run engine SHALL iterate the client stream exactly once, feeding the journal
(`model_tool`, `subagent` lifecycle entries) and applying the RUB-001 terminal rules
(stop-reason recognition, clarification detection, crash honesty) to decide the run's
terminal disposition. The engine SHALL apply the bounded clarification continuation:
an unanswered `ask_clarification` within the state bound triggers a client
re-invocation on the same thread with a provenance-marked system reply; exhausting the
bound transfers to `failed-resume` with the question text preserved in `diagnostics/`.
The engine SHALL NOT report a terminal state contradicting the state machine.

#### Scenario: Multi-turn run lands a readable checkpoint

- **WHEN** the run engine drives the embedded client through a multi-turn conversation
  with the bundle's sync saver
- **THEN** the conversation completes and the bundle's checkpoint file is readable with
  the thread's state

#### Scenario: Bounded continuation exhausts honestly

- **WHEN** the stream terminal carries an unanswered clarification and the continuation
  bound is exhausted
- **THEN** the engine transfers the bundle to `failed-resume`, preserves the question
  text in `diagnostics/`, and journals the exhaustion

### Requirement: Every run records an assembly snapshot

The run engine SHALL inject a first-round middleware hook that records the rendered
system prompt and the visible tool list into `diagnostics/` once per run, together with
the model name and the deerflow pin, before the first model call completes. The
snapshot SHALL be the per-run record of what the model actually saw (the RT2/RT7
blind-spot closure); a snapshot that cannot be captured SHALL fail the run loudly
rather than continue silently unrecorded.

#### Scenario: Snapshot captures the model-visible surface

- **WHEN** a run starts
- **THEN** `diagnostics/` contains the assembly snapshot naming the rendered system
  prompt, the visible tool list, the model name, and the pin
