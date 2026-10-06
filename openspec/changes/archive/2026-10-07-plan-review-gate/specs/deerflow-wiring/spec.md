# Spec Delta

## MODIFIED Requirements

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
apply the bounded automatic continuation unchanged.

When a plan hook is provided for a first-generation run, the engine SHALL enter a
plan phase: the first message is the problem text with a plan-request framing, and
the first turn that ends in plain text with no tool calls and no unanswered
clarification is the PROPOSED PLAN — it SHALL NOT be admitted as a final answer. The
engine SHALL deliver the plan to the hook; a returned plan string is injected as the
continuation message on the same thread (confirmed or user-amended), and a `None`
return injects a skip-proceed message. A clarification detected during the plan phase
SHALL be handled by the clarification rules unchanged (the plan arrives on a later
plain-text turn). A first turn that carries tool calls despite the framing SHALL
degrade the gate honestly: the engine journals the degradation, clears the plan
phase, and proceeds under the rules above — the gate never force-blocks the agent.

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

- **WHEN** a first-generation run is driven with a plan hook and the first plain-text
  turn carries no tool calls
- **THEN** that text is delivered to the plan hook and is not submitted through
  admission; a returned plan string is injected as the same-thread continuation and
  the research turns follow under the unchanged terminal rules

#### Scenario: Clarification inside the plan phase composes

- **WHEN** the plan phase's first turn carries an unanswered `ask_clarification`
- **THEN** the clarification rules apply unchanged, and the next plain-text turn
  without tool calls becomes the proposed plan

#### Scenario: A researching first turn degrades the gate honestly

- **WHEN** the plan phase's first turn carries tool calls despite the framing
- **THEN** the engine journals the degradation, clears the plan phase, and the run
  proceeds under the unchanged rules — nothing is force-blocked

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
