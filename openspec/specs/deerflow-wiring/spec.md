
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
terminal disposition. The engine SHALL accept an optional clarification hook: when the
hook is provided and an unanswered `ask_clarification` is detected, the engine SHALL
deliver the question text to the hook and re-invoke the client on the same thread with
the returned non-empty answer as the continuation message; an empty or declined answer
SHALL fall back to the bounded automatic continuation — a provenance-marked system
reply within the state bound — and exhausting the bound transfers to `failed-resume`
with the question text preserved in `diagnostics/`. Without a hook the engine SHALL
apply the bounded automatic continuation unchanged. An `ask_clarification` call that
the terminal turn itself resolves — its call id appears in the answered set because the
framework answered it within the same turn, without the run's hook — SHALL be journaled
as an absorbed clarification round with the question text; the engine SHALL act on no
absorbed round (no continuation, no bound consumption, no terminal change).

When a plan hook is provided for a first-generation run, the engine SHALL enter a
plan phase: the first message is the problem text with a plan-request framing that
asks for the plan wrapped in explicit plan markers and binds the two channels — a
clarification turn carries only `ask_clarification` (no sibling tool calls; the
framework's middleware drops them by design), and plan confirmation travels only
through the markers, never inside an `ask_clarification` call — and the first final
text carrying the markers is the PROPOSED PLAN — the extracted inner text (markers
stripped) SHALL NOT be admitted as a final answer. The engine SHALL deliver the
extracted plan to the hook; a returned plan string is injected as the continuation
message on the same thread (confirmed or user-amended), and a `None` return injects a
skip-proceed message. A plan-phase turn whose final text carries no markers SHALL
degrade the gate honestly — whether it is a research report, a non-plan answer, or an
empty reply, and regardless of the turn's tool calls (the terminal picture cannot
distinguish a research turn from a plan turn; detection is deterministic content
structure, never behavioral inference): the engine journals the degradation, clears the
plan phase, and proceeds under the rules above — the gate never force-blocks the agent,
and the channel binding in the framing is wording-level constraint under the same
honest-degradation philosophy, never a hard block. A clarification detected during the
plan phase SHALL be handled by the clarification rules unchanged (the plan arrives on a
later marked turn).

The engine SHALL treat a framework error-fallback message — the final AI message
carrying the `deerflow_error_fallback` marker that the framework's error-handling
middleware renders when a model call fails — as a failed run: the disposition SHALL
be `failed-resume` with the rendered error journaled in a `terminal` entry, and the
engine SHALL NOT report `completed` for such a run. The engine SHALL NOT report a
terminal state contradicting the state machine.

#### Scenario: Multi-turn run lands a readable checkpoint

- **WHEN** the run engine drives the embedded client through a multi-turn conversation
  with the bundle's sync saver
- **THEN** the conversation completes and the bundle's checkpoint file is readable with
  the thread's state

#### Scenario: The hook routes the question and the answer continues the run

- **WHEN** a run is driven with a clarification hook and the stream terminal carries an
  unanswered `ask_clarification`
- **THEN** the hook receives the question text, the client is re-invoked on the same
  thread with the returned answer, and the round is journaled without consuming the
  auto bound

#### Scenario: The plan phase proposes, gates, and injects

- **WHEN** a first-generation run is driven with a plan hook and a turn's final text
  carries the plan markers
- **THEN** the extracted inner text (markers stripped — never leaked to the hook, the
  injection, or the materialized artifact) is delivered to the plan hook and is not
  submitted through admission; a returned plan string is injected as the same-thread
  continuation under the unchanged terminal rules

#### Scenario: A researching first turn degrades the gate honestly

- **WHEN** a plan-phase turn ends in a plain-text research report with no plan
  markers — regardless of the turn's tool calls (the terminal picture cannot
  distinguish a research turn from a plan turn; the real-ladder regression,
  bundle 58b5440e)
- **THEN** the engine journals the degradation, clears the plan phase, and the run
  completes under the unchanged rules without ever presenting the report as a plan
  or injecting a second pass — nothing is force-blocked

#### Scenario: Clarification inside the plan phase composes

- **WHEN** the plan phase's first turn carries an unanswered `ask_clarification`
- **THEN** the clarification rules apply unchanged, and the next marked turn becomes
  the proposed plan

#### Scenario: Bounded continuation exhausts honestly

- **WHEN** the stream terminal carries an unanswered clarification and the continuation
  bound is exhausted
- **THEN** the engine transfers the bundle to `failed-resume`, preserves the question
  text in `diagnostics/`, and journals the exhaustion

#### Scenario: A framework error-fallback fails the run loudly

- **WHEN** the terminal picture's final AI message carries the framework's
  `deerflow_error_fallback` marker (a model call failed and the error-handling
  middleware rendered the fallback)
- **THEN** the engine transfers the bundle to `failed-resume`, journals a `terminal`
  entry naming the error type, and does not report `completed`

#### Scenario: A clean completion lands the report through the hold point

- **WHEN** a run completes cleanly with a non-empty final answer
- **THEN** the engine submits the answer as a final_report through the admission hold point, and an admitted report file appears under final/ with a ledger admit entry

#### Scenario: The framing binds the channels and absorbed rounds stay observable

- **WHEN** a plan-phase framing is composed, or a terminal turn's `ask_clarification`
  calls are all resolved by the turn's own answered set
- **THEN** the framing instructs that question turns carry only `ask_clarification`
  and plan confirmation only travels through the plan markers, and each absorbed
  round is journaled with its question text without triggering a continuation,
  consuming the bound, or altering the terminal disposition

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


### Requirement: Skill selection is declared, not implicit

The bound client's skill surface (`available_skills`) SHALL be sourced from an explicit
declaration in the owning configuration file of the selected ladder, resolved at
assembly time and passed to the binding — never hard-coded at the binding site. The
declaration SHALL default to the unwired posture (no skills declared), and the default
assembly SHALL preserve the current binding behavior exactly. A declaration that
resolves to a non-default posture SHALL be a conscious configuration act, not a
fallback.

A contract guard SHALL lock the default posture offline (stdlib-only, no framework
import): it SHALL fail when the binding stops sourcing the skill surface from the
declaration, when the default posture silently changes, or when the declaration parser
swallows or coerces a declared value. Actual skill activation semantics — what the
framework loads and with what quality — are outside this requirement's scope and need
their own cognitive-program establishment before any non-default declaration ships.

#### Scenario: Default posture is declared-none and preserved

- **WHEN** the configuration declares no skills and assembly builds the client through
  a recording stand-in
- **THEN** the binding receives the unwired skill posture (no skills), matching the
  pre-declaration binding behavior

#### Scenario: An implicit or coerced skill surface fails the guard

- **WHEN** the binding hard-codes a skill surface, ignores the declaration, or the
  declaration parser coerces or swallows a declared value
- **THEN** the offline contract guard fails naming the violated seam

#### Scenario: Declaration drift fails loudly without touching the framework

- **WHEN** the guard runs offline (no framework import, no credentials)
- **THEN** it validates the declaration-to-binding seam using the contract mirror and
  recording stand-ins only
