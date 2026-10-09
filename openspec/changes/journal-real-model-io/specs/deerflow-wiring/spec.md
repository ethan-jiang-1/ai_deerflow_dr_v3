# Spec Delta

## Purpose

Owns the wiring contracts of the embedded-harness form: explicit configuration
resolution, the contract mirror over borrowed framework surfaces, and the run
engine's stream consumption with terminal honesty.

## MODIFIED Requirements

### Requirement: Configuration resolution is explicit and never auto-discovered

Constructing the harness client binding SHALL require an explicit configuration path
resolving to a checked-in configuration (`base`, `fixture`, or `record`); the binding
SHALL NOT fall back to framework default discovery, and an ambiguous or missing path
SHALL fail loudly at construction naming the requested configuration. The checked-in
configurations SHALL be shape/secret separated: shape lives in the configuration file,
credentials are `$VAR` references resolved from the environment by the framework. The
`record` configuration SHALL be the `base` composition with the model `use:` seam
pointing at the harness-owned journaling provider: it requires the
`DEERFLOW_RECORD_SINK` environment variable (construction fails loudly without it),
journals every model input/output pair (including `tool_calls` turns) to that path
with a one-time metadata sidecar (model class, deerflow pin, invocation, timestamp),
and declares the bundle composition as `all_real` — a journaled real run is still a
real run.

#### Scenario: Explicit path is honored and ambiguity fails

- **WHEN** the binding is constructed with an explicit existing configuration path
- **THEN** the framework client is constructed with exactly that `config_path`; a
  missing path fails construction naming the requested configuration

#### Scenario: Fixture configuration runs the real chain with fakes

- **WHEN** the fixture configuration is selected
- **THEN** its `use:` seams resolve to harness-owned fake model and search providers,
  and the real client chain runs end-to-end with zero credentials

#### Scenario: Record configuration journals the real model without changing the ladder

- **WHEN** the record configuration is selected with `DEERFLOW_RECORD_SINK` set
- **THEN** the real model is wrapped by the journaling provider, every model turn is
  appended to the sink as a normalized-input-hash keyed line carrying content and any
  `tool_calls`, and the bundle's declared composition is `all_real`
- **WHEN** the record configuration is selected without `DEERFLOW_RECORD_SINK`
- **THEN** construction fails loudly naming the missing variable

#### Scenario: Journal lines replay across the format boundary

- **WHEN** a journal line carries a `tool_calls` field
- **THEN** replay reconstructs the turn as an assistant message with both content and
  tool calls; a line without the field (legacy format) replays content-only

## ADDED Requirements

### Requirement: The journaling provider is a thin wrapper, never a semantics change

The harness-owned journaling provider SHALL subclass the framework's configured chat
model and override only `_generate` (delegating to `super()` and appending the journal
line) plus construction (sink resolution, loud failure, sidecar). It SHALL NOT alter
binding, tool protocols, middleware order, or any framework behavior a recorded run
would otherwise exhibit; the framework class is imported and subclassed at the
harness-owned seam and the framework subtree is never modified. Usage/token metadata
SHALL NOT be journaled — the recording boundary matches the ladder's declared token
limit.

#### Scenario: A journaled run behaves exactly as its base configuration

- **WHEN** the same problem runs under `record` and `base` with equivalent credentials
- **THEN** the model protocol, tool binding, and event stream are those of the base
  configuration; the only difference is the journal file and its sidecar

#### Scenario: Tool-call turns are captured whole

- **WHEN** a model turn emits tool calls
- **THEN** the journal line records name/args/id for each call, and replaying the line
  reproduces the tool-call turn the recorded run executed
