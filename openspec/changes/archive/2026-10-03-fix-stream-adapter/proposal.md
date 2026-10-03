# Proposal

## Why

The first real-ladder run (real DeepSeek + the real deep-research skill) proved the
pipeline end-to-end but exposed a conformance bug the fixture-shaped fake events had
masked: against the real stream, the journal's `model_tool`/`subagent` sink silently
records nothing (the adapter reads a `data["message"]` wrapper that the real
`messages-tuple` events do not carry — their data IS the message chunk itself), and the
live view renders one line per token, which is unreadable. The evidence and the
DeerFlow stream-protocol notes live in
`_backlog/plans/2026-10-03-stream-adapter-and-live-view.md`.

## What Changes

- **Adapter conformance fix** (`runtime/run_engine.py`): the `messages-tuple` handler
  reads the event's data as the message chunk directly (flat dict: `type`, `content`,
  `tool_calls`, `additional_kwargs`, …), matching the real stream verified by the
  live dump. Fake test events are reshaped to the real shape. This makes the engine
  meet the already-declared deerflow-wiring requirement ("feeding the journal") — no
  spec text changes.
- **Per-turn journal aggregation**: token-level chunks are no longer journaled
  individually (they would flood the ledger); the turn accumulates the AI text and
  journals one aggregated `model_tool` entry at turn end (tool calls plus an answer
  excerpt). The `values` snapshot stays the authoritative terminal picture.
- **Token-streaming live view**: the renderer gains a streaming mode — AI text chunks
  print inline (no newline), tool calls / state changes / turn ends render as the
  existing stable phrases. The CLI's `create` live view uses it; `watch` and the
  journal projection are unaffected (they render the per-turn aggregated entries).

## Capabilities

### New Capabilities

(none — a conformance fix against existing requirements; the change opts out of specs
via `skip_specs: true`)

### Modified Capabilities

(none)

## Impact

- Modified: `deep_research_harness/src/deerflow_deep_research/runtime/run_engine.py`
  (adapter + turn aggregation), `runtime/render.py` (streaming mode),
  `deep_research_harness/cli.py` (live-view handler), the fake events in
  `tests/unit/test_run_engine.py` / `tests/unit/test_entry_surface.py` (reshaped to
  the real stream), the golden's affected assertions (explicit updates, red-green).
- No governance registration changes, no CI workflow change, no `deerflow/` contact
  beyond the already-owned boundary.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/run_engine.py`
  — the stream adapter is where the real shape meets the engine; the fix is a
  conformance repair of its declared behavior.
- **Seam classification:** wiring — the changed behavior is adaptation to the
  framework's real event shape plus presentation of its tokens; no policy changes.
- **Question:** How does the engine conform to the real `messages-tuple` shape (flat
  chunk, token-grained) so the journal sink records real turns and the live view
  streams tokens inline — without touching the terminal rules or the spec text?
- **Necessary adjacent/external contracts:** the plan's stream-protocol notes (answers: the real data shapes the adapter must match, verified by the live dump); the journal policy (answers: why aggregation lands at turn granularity — token-level entries would flood the ledger); the entry renderer (answers: how streaming mode composes with the existing phrase vocabulary).
- **Evidence seam:** unit tests with real-shaped fake chunks (adapter, aggregation,
  streaming) red-before-green; a small real-ladder run proving the journal gains
  aggregated entries and the live view streams inline.
- **Not in scope:** the full deep-research demonstration run (a bigger real question
  — it follows this change), watch/projection changes, spec text changes.
- **Triggered review policies:** change-admission
