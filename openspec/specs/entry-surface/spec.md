
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
optional event hook (the live view's sink), an optional clarification hook, and an
optional plan hook without altering the journal or terminal rules; the watch
projection SHALL render journal entries, not raw events. A clarification question
and a proposed research plan delivered in an interactive context SHALL render through
the same module as stable human phrases. The interactive context SHALL be gated: a
foreground command MAY prompt on stdin only when stdin is a terminal or an explicit
environment override (`DEEP_RESEARCH_INTERACTIVE`) is set; a non-interactive context
SHALL never block on stdin, SHALL drive the run without a clarification hook (the
bounded automatic continuation stands), and SHALL drive it WITH an auto-confirming
plan hook for a first-generation `create`: the plan phase runs, the proposed plan is
confirmed verbatim and injected as the continuation, and the run proceeds to
research — the plan-phase model round is the deliberate price of the plan-first
research methodology (BUG-001: with no plan phase, the plan-first output falls
through to completion as a plan-shaped "report"). The plan prompt SHALL offer the
three ways with stable phrases: confirm as-is, append a revision note, or skip the
plan injection; an explicit abort input exits without further turns. `create` is the
only command that MAY carry a plan hook, and only for a first-generation run —
`refine`'s direction document already is the user-authored plan.

#### Scenario: Renderer strings are stable across live view and projection

- **WHEN** the same tool call is rendered from the live stream and later from the
  journal projection
- **THEN** both renderings use the same human phrase for the tool and the arguments

#### Scenario: The clarification question renders through the shared module

- **WHEN** an interactive foreground run delivers a clarification question to the
  operator
- **THEN** the question renders as a stable human phrase from the same rendering
  module the live view uses, followed by the answer prompt

#### Scenario: The proposed plan renders with a three-way prompt

- **WHEN** an interactive `create` delivers the agent's proposed research plan to
  the operator
- **THEN** the plan renders through the shared module, followed by the stable
  three-way prompt (confirm / append revision note / skip) and the abort hint

#### Scenario: A non-interactive context never blocks on stdin

- **WHEN** a foreground command runs with stdin not a terminal and no environment
  override
- **THEN** the run is driven without a clarification hook (the bounded automatic
  continuation applies) and without ever reading stdin, and a first-generation
  `create` carries an auto-confirming plan hook: the plan phase runs, the proposed
  plan is confirmed verbatim and injected, the gate lifecycle is journaled
  (`plan_proposed` then `plan_confirmed`), and the run proceeds to research

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

### Requirement: Create and refine route through the declared chain, locked offline

The `create` and `refine` journeys SHALL route through the declared chain: the stable
launcher delegates to the interaction surface; the verb handler SHALL create or extend
the bundle through the bundle actions owner and SHALL drive the run through the
foreground assembly owner; the foreground assembly SHALL open the bundle checkpointer,
build the bound client, and construct the stream callable through the DeerFlow binding;
the run engine SHALL reach its typed terminal state and SHALL submit the final report
through the admission owner. No journey stage SHALL bypass or duplicate an adjacent
stage's responsibility.

The chain's composition SHALL be locked by an offline contract test in the `contract`
test lane (entering `make verify`, stdlib-only, no framework import): the test SHALL
assert the declared call relationships between the chain's stages, SHALL fail naming
the broken link when a stage is replaced, bypassed, or its owning module renamed
without cutover, and SHALL NOT depend on line numbers or cosmetic formatting so that
behavior-preserving refactors inside a stage do not false-fail.

#### Scenario: The locked chain validates green

- **WHEN** the offline chain-lock contract test runs against a tree whose entry chain
  matches the declared composition
- **THEN** the test passes with every declared link asserted

#### Scenario: A broken or bypassed chain link fails loudly

- **WHEN** a journey stage is rewired to bypass or replace an adjacent stage's owner,
  or a chain module is renamed without cutting over its consumers
- **THEN** the offline chain-lock contract test fails naming the broken link

#### Scenario: Behavior-preserving refactor does not false-fail

- **WHEN** code inside a single chain stage is refactored without changing which owner
  performs each stage's responsibility
- **THEN** the offline chain-lock contract test still passes
