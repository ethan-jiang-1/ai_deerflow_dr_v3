# Spec Delta

## MODIFIED Requirements

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
SHALL never block on stdin and SHALL drive the run without a clarification hook or a
plan hook (no plan phase, no extra model round). The plan prompt SHALL offer the
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
- **THEN** the run is driven without a clarification hook and without a plan hook,
  completes through the bounded automatic continuation without ever reading stdin,
  and performs no plan-phase model round
