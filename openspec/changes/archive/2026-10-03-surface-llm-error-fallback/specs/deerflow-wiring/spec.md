> req: DEW-001

# Spec Delta

## MODIFIED Requirements

### Requirement: The run engine consumes the stream with terminal honesty

The run engine SHALL iterate the client stream exactly once, feeding the journal
(`model_tool`, `subagent` lifecycle entries) and applying the RUB-001 terminal rules
(stop-reason recognition, clarification detection, crash honesty) to decide the run's
terminal disposition. The engine SHALL apply the bounded clarification continuation:
an unanswered `ask_clarification` within the state bound triggers a client
re-invocation on the same thread with a provenance-marked system reply; exhausting the
bound transfers to `failed-resume` with the question text preserved in `diagnostics/`.
The engine SHALL treat a framework error-fallback message — the final AI message
carrying the `deerflow_error_fallback` marker that the framework's error-handling
middleware renders when a model call fails — as a failed run: the disposition SHALL be
`failed-resume` with the rendered error journaled in a `terminal` entry, and the
engine SHALL NOT report `completed` for such a run. The engine SHALL NOT report a
terminal state contradicting the state machine.

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

#### Scenario: A framework error-fallback fails the run loudly

- **WHEN** the terminal picture's final AI message carries the framework's
  `deerflow_error_fallback` marker (a model call failed and the error-handling
  middleware rendered the fallback)
- **THEN** the engine transfers the bundle to `failed-resume`, journals a `terminal`
  entry naming the error type, and does not report `completed`
