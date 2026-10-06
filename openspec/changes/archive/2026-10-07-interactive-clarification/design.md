# Design

## Context

`run_engine._drive` loops `_consume_turn`; on an unanswered `ask_clarification` terminal
it journals `auto_continuation`, sets `message = AUTO_REPLY_PREFIX + question`, and
continues, bounded by `auto_proceed_count/bound` (N=2) in `state.json`; exhaustion
writes `diagnostics/unanswered-clarifications.json` and transfers to `failed-resume`.
The entry surface already has the optional-hook pattern (the live-view event sink,
spec'd in entry-surface) and a shared rendering module. `create`/`refine` drive
`entry.run_foreground` → `run_engine.run_research` in the foreground. Smoke drives the
CLI as a subprocess (stdin is a pipe, not a TTY). Existing unit tests fake an
unanswered-ask stream in `tests/unit/runtime/test_run_engine.py`.

## Goals / Non-Goals

**Goals:**
- The agent's clarifying question reaches the operator in interactive foreground runs,
  and the operator's answer continues the run as their own words.
- Headless contexts (smoke, background, non-TTY) behave byte-identically to today.
- The auto bound keeps its meaning (caps blind guessing), not engagement.

**Non-Goals:**
- No cross-process answering (a future `answer` verb for paused bundles is explicitly
  out — that needs a new state and is a separate change if ever wanted).
- No mandatory questionnaire; no new verbs or flags; no journal category additions; no
  state-machine transition changes; no upstream changes.

## Decisions

### D1 — An injected hook, not a new run state

`run_research(..., on_clarification: Callable[[str], str | None] | None = None)` —
exactly parallel to `on_event`. The question is answered synchronously inside the
process; the bundle stays `active` throughout, so no state machine or persistence
semantics change. A crash mid-prompt is covered by the existing crash-transfer
(dead owner → `failed-resume` on the next `status`). Alternative rejected: an
`awaiting-clarification` state with a later `answer` verb — correct for a service form,
but it doubles this change's surface (new state, new verb, liveness rules) for a
foreground CLI that can simply ask inline.

### D2 — Gating: TTY or `DEEP_RESEARCH_INTERACTIVE`, never otherwise

The CLI builds a handler iff `sys.stdin.isatty()` or `DEEP_RESEARCH_INTERACTIVE` is
truthy. The env override exists for two reasons: subprocess/smoke can drive the prompt
with piped stdin (testability), and a user on a weird terminal can force interactivity.
Without either, no handler is passed and the engine takes today's path — a
non-interactive context can never block on stdin. Alternative rejected: a CLI flag
(`--interactive`) — works, but the env var matches the existing `DEEP_RESEARCH_*`
family and needs no verb-surface addition.

### D3 — Answered rounds are free; declined rounds are auto rounds

On hook delivery: journal `clarification_asked`; call the hook; a non-empty stripped
answer journals `clarification_answered` and continues with `message = answer` (raw —
it is the human's words; the auto-reply keeps its provenance prefix because it is not).
An empty answer journals `clarification_declined` and falls through to the existing
auto-reply branch (increments the count). Rationale: the bound exists to stop the agent
blindly guessing; a human answer is not a guess, and the human is the natural loop
breaker (they can decline at any question). A runaway ask-loop with answers is bounded
by the same graph recursion limit as any conversation and by the human's patience.
Alternative rejected: counting everything against N=2 — punishes engagement; two
questions then dead is exactly the misdirected-run cost this change removes.

### D4 — Journal through existing categories, render through the shared module

Events use the `lifecycle` category (`clarification_asked` / `clarification_answered` /
`clarification_declined`) — the closed category set is untouched. The question renders
via `render.py` (stable phrase), then the prompt reads one line from stdin. The prompt
text states that an empty line declines (letting the agent proceed on its own judgment).

### D5 — `refine` gets the same wiring for free

Both `create` and `refine` drive `run_foreground`; the hook threads through
`entry.run_foreground(...)` to `run_research`, so both verbs become interactive under
the same gating with one wiring point.

## Risks / Trade-offs

- [A model asks many questions and the operator answers all of them] → The operator can
  decline any question (empty input), which immediately returns to the bounded path;
  the recursion limit caps the run regardless.
- [Blocking on stdin in an unforeseen non-TTY context] → The default is headless: no
  TTY and no override means no handler, and the engine cannot read stdin at all (the
  engine never touches stdin — only the CLI-built handler does).
- [The piped-stdin smoke is timing-sensitive] → The handler reads stdin only after the
  question arrives; a piped answer sits in the buffer until read — no polling, no race.
- [Journal consumers see new event names] → New `lifecycle` event names only; the
  category set and schema are unchanged; `watch` renders them as lifecycle lines.

## Migration Plan

Pure addition; no data or schema migration. Headless callers (tools, smoke, tests)
observe no difference. Rollback is reverting the commit.
