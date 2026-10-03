# Design

## Context

Verified this session: the marker's owners are the framework's
`llm_error_handling_middleware.py` (line 685) and `terminal_response_middleware.py`
(line 148) — the LLM-error-handling middleware is default-on (the wiring plan decision
4 default matrix), so every embedded run already carries this behavior. The wiring
smoke's diagnostic captured the real shape: the fallback AI message carries
`additional_kwargs = {"deerflow_error_fallback": True, "error_type": "ValueError", …}`
with content like "LLM request failed: …", and the run then ends normally (the stream
reaches `end` with no `stop_reason`). The run engine's terminal picture currently
collects only tool calls, answered ids, and the stop reason — the marker is invisible
to it, so a failed model call completes the run silently.
`docs/known-limitations.md` has carried the finding since the wiring change. Policy
routing: `workflow-outcome-review`, `change-admission`; no StateGraph
transition/predicate is authored here.

## Goals / Non-Goals

**Goals:**

- A framework-disguised model failure is a loud harness failure: `failed-resume`, the
  rendered error journaled, the completion path unreachable for such a run.
- The guard adds no behavior to clean runs (the negative control is explicit).

**Non-Goals:**

- No retry/repair of model calls (the framework's own retries already ran before the
  fallback renders), no delegated/subagent-stream handling (the lead-stream rule lands
  here; delegated flows ride their consumers), no framework-side change, no CI change.

## Decisions

1. **Detection lives in the terminal picture, not in the stream loop.** The
   `values`-snapshot scan (already the authoritative terminal picture) additionally
   captures whether the LAST AI message carries the truthy `deerflow_error_fallback`
   marker in its `additional_kwargs`, plus the rendered `error_type`. The chunk-level
   scan does not collect the marker (the snapshot is authoritative, exactly as the
   clarification detection settled during the wiring smoke). Alternative (a
   stream-loop check on every chunk) rejected: chunk-level `additional_kwargs` are
   partial and the snapshot is where the final message shape is complete.
2. **Fallback-first branch order.** In `run_research`, a detected fallback transfers
   to `failed-resume` before the clarification, stop-reason, and completed branches
   are considered: the fallback message is an error report — treating it as an answer
   (or as a clarification to continue from) would launder the failure. The
   clarification detection still runs first for its own purpose (an unanswered
   question stays unanswered), but the disposition when a fallback is present is
   `failed-resume` regardless.
3. **The journal names the error, the message names nothing new.** The `terminal`
   entry carries `{"reason": "llm_error_fallback", "error_type": …}`; the fallback
   message itself already appeared in the journal via the normal model_tool flow. No
   new journal category or vocabulary is introduced (the small-closed-set discipline).
4. **The integration proof drives the real fallback path**: the scripted fixture model
   gains a `{"raise": "…"}` script action (`_generate` raises), so the scenario runs
   model-error → framework error-handling middleware → fallback message → harness
   guard → `failed-resume`. Forcing the error from the model (instead of faking the
   marker) proves the whole chain including the framework side.
5. **`known-limitations.md` stays, with its disposition updated.** The framework
   behavior (disguising failures) remains a fact; what changes is the harness
   disposition — the row now says the guard landed (this change) and points at the
   run engine's rule.

## Alternatives

- **Stream-loop marker detection on every chunk** — rejected: see decision 1; the
  snapshot is the authoritative terminal picture and chunk-level kwargs are partial.
- **A dedicated journal category for model errors** — rejected: the `terminal`
  category already owns run-disposition records; a new category would widen the
  closed set for no queryable gain (the detail dict carries the error type).
- **Retrying failed model calls in the harness** — rejected: the framework's
  error-handling middleware owns retries (its default matrix); a harness-side retry
  would be a competing controller.
- **Silently keeping `completed` with the error in content** — rejected: that is the
  exact "安静烂掉" the quality tenets and the terminal-honesty requirement forbid; it
  is also what `known-limitations.md` has flagged since the wiring change.

## Risks / Trade-offs

- [A legitimate final answer happens to carry the marker] → the marker is set only by
  the framework's error-handling middlewares (verified: the two middlewares are the
  only owners); a clean answer never carries it. If a future framework version sets
  it elsewhere, the contract mirror and this guard's negative control are the alarm.
- [The fallback arrives mid-run, not at the end] → the snapshot is authoritative for
  the terminal picture; if the framework recovers and produces a later clean answer,
  the last AI message is the clean one and the run completes — the guard judges the
  terminal state, not the run's history.
- [Marker shape drifts in a framework bump] → the integration scenario (a raising
  model) fails naming the missing disposition; the marker is additionally documented
  in the mirror's event-family declarations if it stabilizes.

## Migration Plan

Single apply, red-before-green: unit tests (scripted fallback events: detection,
branch order over clarification/completion, negative control) red → engine change
green; integration scenario (raising scripted model → failed-resume end-to-end) green;
`known-limitations.md` disposition update; verification sequence; reviews; archive;
commit. Rollback is reverting the edits; no registry IDs are touched.

## Open Questions

(none — the marker's shape, owners, and the branch order were pinned against the
framework source and a live diagnostic this session)
