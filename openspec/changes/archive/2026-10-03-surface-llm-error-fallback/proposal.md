# Proposal

## Why

The wiring smoke surfaced that the framework's LLM-error handling (a default-on
middleware) disguises a model-call failure as a normal AI message carrying the
`deerflow_error_fallback` marker — so a run whose model failed silently reports
`completed`, and the failure lives only inside the message content. For a harness whose
quality tenets are "宁可响亮失败、不可安静烂掉", a disguised failure completing a run
is the exact anti-pattern. `docs/known-limitations.md` has carried this since the
wiring change; this change closes it with a terminal-honesty guard.

## What Changes

- **Run-engine guard** (`runtime/run_engine.py`): the terminal picture gains the
  error-fallback fact — when the final AI message carries the framework's
  `deerflow_error_fallback` marker (with its `error_type`), the run transfers to
  `failed-resume` and journals a `terminal` entry naming the error, instead of
  completing. Detection precedence: a rendered fallback trumps the clarification,
  stop-reason, and completed branches (an error report is never a report).
- **DeerFlow-wiring spec MODIFIED** (DEW-001): the terminal-honesty requirement gains
  the fallback rule and a scenario; the existing scenarios are preserved verbatim.
- **Integration proof**: the scripted fixture model gains a `{"raise": "…"}` script
  action — a scenario whose model deliberately raises drives the framework's real
  fallback path, and the guard lands the run in `failed-resume` end-to-end (the whole
  chain: model error → framework fallback → harness guard).
- **`known-limitations.md` disposition updated**: the limitation remains a framework
  behavior, but its harness disposition changes from "unhandled" to "guarded — the run
  fails loudly instead of completing".

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `deerflow-wiring`: the requirement "The run engine consumes the stream with terminal
  honesty" gains the error-fallback detection rule and scenario. No other requirement
  changes.

## Impact

- Modified: `deep_research_harness/src/deerflow_deep_research/runtime/run_engine.py`
  (terminal-picture collection + detection branch),
  `runtime/fixtures/__init__.py` (the `{"raise": …}` script action),
  `tests/unit/test_run_engine.py` (guard cases + negative control),
  `tests/integration/test_wiring_smoke.py` (the real-error scenario),
  `deep_research_harness/docs/known-limitations.md` (disposition update),
  `openspec/specs/deerflow-wiring/spec.md` (merged at archive from the delta).
- No CI workflow change, no new external dependencies, no governance registration
  changes, no `deerflow/` contact beyond the already-owned public-API reading boundary.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/run_engine.py`
  — the terminal-disposition rules are where the guard lives; the framework renders
  the marker, the harness decides what it means.
- **Seam classification:** deterministic-guardrail — the changed behavior is a
  machine-checked terminal rule over a framework-rendered marker.
- **Question:** How does a framework-disguised failure become a loud harness failure —
  detected at the terminal picture, journaled with the error type, and dispositioned as
  `failed-resume` — without re-deciding any other terminal rule?
- **Necessary adjacent/external contracts:** the framework's LLM-error-handling middleware (answers: the marker's exact
  shape and that it is default-on — the harness detects, never synthesizes); the RUB-001 terminal rules (answers: which transitions the guard reuses and why the
  branch order is fallback-first); `docs/known-limitations.md` (answers: the limitation's disposition after the guard).
- **Evidence seam:** unit tests with scripted fallback events (detection, precedence
  over completion, negative control that a clean run still completes) plus the
  integration smoke scenario (a deliberately raising model drives the real fallback →
  `failed-resume` end-to-end).
- **Not in scope:** retry/repair of failed model calls (the framework owns retries),
  subagent-fallback handling (the marker appears in delegated flows too — the engine's
  rule covers the lead stream; delegated-stream handling rides the entry/wiring
  consumers), any framework-side change, CI wiring.
- **Triggered review policies:** workflow-outcome-review, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| Model call fails; the framework renders the error-fallback message | The run engine's terminal picture (marker detection) | None — fail loud; the framework's own retries already ran | `failed-resume`, journal `terminal` entry naming `error_type` | `refine` (same bundle, next generation) or manual inspection | Unit: scripted fallback event → failed-resume; Integration: a raising scripted model lands failed-resume end-to-end |
| Clean run (no fallback marker) | Terminal picture (no marker) | n/a | `completed` exactly as before — the guard adds no behavior | n/a | Unit negative control: clean stream still completes |
