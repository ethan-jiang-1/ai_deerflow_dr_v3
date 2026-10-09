# Spec Delta

## MODIFIED Requirements

### Requirement: Clarification continuation is bounded and records its count

The state machine SHALL carry `auto_proceed_count` and the configured bound (N=2) in
`state.json`. Whether a stream terminal contains an unanswered `ask_clarification` call
SHALL be decided by a pure detection function. When the run is driven with a
clarification hook (an interactive context), the detected question text SHALL be
delivered to that hook and a returned non-empty answer SHALL continue the run on the
same thread; an answered interactive round SHALL NOT consume the auto bound (the bound
guards against blind guessing, and a human answer is not a guess; the human remains the
loop breaker and may decline any question). A declined or empty answer SHALL fall back
to the automatic continuation: the bound allows at most N automatic continuation rounds
with provenance-marked replies, the count is recorded in `state.json`, and exhausting
the bound SHALL transfer the bundle to `failed-resume` with the unanswered question text
preserved in `diagnostics/`. Runs without a hook (headless) SHALL behave exactly as the
bounded automatic continuation. Every clarification round — asked, answered, declined,
or absorbed — SHALL be journaled: an `ask_clarification` call that the terminal turn
itself resolves (its call id appears in the answered set because the framework answered
it within the same turn, without the run's hook) SHALL be journaled as its own
clarification round with the question text, so the interaction history is
reconstructable with no silent absorption. An absorbed round is a recorded observation
only: it SHALL change no state-machine fact, consume no bound, and trigger no
continuation. The client re-invocation loop itself is owned by the wiring change.

#### Scenario: Exhausting the continuation bound transfers to failed-resume

- **WHEN** the detection function reports an unanswered clarification and
  `auto_proceed_count` already equals the bound
- **THEN** the transition rule returns `failed-resume` with the question text routed to
  `diagnostics/`

#### Scenario: An answered interactive round continues without consuming the bound

- **WHEN** a run driven with a clarification hook detects an unanswered clarification
  and the hook returns a non-empty answer
- **THEN** the run continues on the same thread with the answer as the human's own
  message, the round is journaled as asked-and-answered, and `auto_proceed_count` is
  unchanged

#### Scenario: Declining a question falls back to the bounded automatic reply

- **WHEN** the hook returns an empty answer (the operator declines)
- **THEN** the run continues with the provenance-marked automatic reply and the round
  consumes the auto bound exactly as a headless continuation would

#### Scenario: An absorbed clarification round is journaled, never acted on

- **WHEN** a terminal turn carries an `ask_clarification` whose call id the turn's own
  answered set resolves (the framework answered it in-turn, so no unanswered question
  is detected) — headless or interactive, with or without a hook
- **THEN** the round is journaled with the question text, the run's terminal rules and
  `auto_proceed_count` are exactly as if the call had not existed, and no continuation
  is triggered by the absorbed round
