# Proposal

## Why

The postmortem re-run proved the exception guard but traced the surviving blocker precisely: the embedded stream's recursion_limit defaults to 100 and reads a per-call override (client.py:293) — the AppConfig top-level key is not consumed, so the config-only fix never reached the stream and deep research still caps at ~10 tool rounds. The known limitation is recorded in docs/known-limitations.md.

## What Changes

- The binding gains `make_stream_fn(client, thread_id, *, recursion_limit=DEEP_RESEARCH_RECURSION_LIMIT)` — the single seam where the run's stream calls are built; the CLI and drivers use it so every stream call carries the limit. `DEEP_RESEARCH_RECURSION_LIMIT = 300` (framework max 1000; conservative start, adjust on evidence).
- The mirror documents the consumed stream kwarg (the constructor mirror stays; the stream-call seam is noted as consumed surface).
- The limitation row's disposition updates once the re-run completes.

## Capabilities

### New Capabilities

(none — conformance fix; `skip_specs: true`)

### Modified Capabilities

(none)

## Impact

- Modified: `runtime/client.py` (stream-fn factory + limit constant), `cli.py` (uses the
  factory), `runtime/contracts/client_surface.py` (consumed-stream-kwarg note),
  `tests/unit/test_wiring_mirror.py` (factory test red-green),
  `docs/known-limitations.md` (disposition after the live proof). No governance/CI/deerflow changes.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/client.py` — the stream-call seam owns the limit the framework reads per-call.
- **Seam classification:** wiring — a call-parameter adaptation at the framework boundary; no policy change.
- **Question:** How does the recursion limit actually reach the embedded stream (per-call override, not AppConfig), so deep research stops capping at 100 steps — with the seam owned in one place and proven by a completing re-run?
- **Necessary adjacent/external contracts:** client.py:293 (answers: the exact per-call mechanism the fix must use); the crashed EASA bundle (answers: the live verification subject — its preserved material should finally complete the briefing).
- **Evidence seam:** a unit test proving every stream call carries the limit (fake client records kwargs), plus the live refine re-run completing as the end-to-end proof.
- **Not in scope:** adaptive limits, spec text changes, CI changes.
- **Triggered review policies:** change-admission
