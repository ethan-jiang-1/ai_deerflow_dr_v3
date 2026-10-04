# Proposal

## Why

The recursion-chain debugging arc proved the stream's recursion_limit is a per-call override (client.py:293) invisible to introspection — and the wiring smoke still built its stream calls with a hand-rolled lambda, so the seam the guard relies on was not the seam the smoke exercised. The mirror declares the consumed stream kwargs; nothing pinned the behavior.

## What Changes

- The wiring smoke's multi-turn scenario switches to `make_stream_fn` (the single seam) — the real-run behavioral pin.
- The mirror gains the consumed stream-kwarg declaration (`CONSUMED_STREAM_KWARGS`, already drafted in the seam fix) promoted to a pinned constant with a unit assertion.
- Design/tasks/proposal record the seam as the only sanctioned stream-call path (no raw client.stream lambdas outside make_stream_fn).

## Capabilities

### New Capabilities
(none — conformance fix; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- Modified: `runtime/contracts/client_surface.py`, `tests/unit/test_wiring_mirror.py`, `tests/integration/test_wiring_smoke.py`. No product behavior change (the smoke already ran through the same limit via the earlier seam fix; this pins it).

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/client.py` — make_stream_fn is the single stream-call seam (the recursion-chain scar: the limit is a per-call override invisible to the constructor signature).
- **Seam classification:** deterministic-guardrail — the seam is pinned by test; no policy change.
- **Question:** How does the stream-call seam (thread_id + recursion_limit per-call kwargs) stay pinned — the smoke exercises it, the mirror declares it, and the unit test proves the injection?
- **Necessary adjacent/external contracts:** the contract mirror (answers: where the consumed stream kwargs are declared); the wiring smoke (answers: the behavioral pin — a real run through the seam completes); the unit factory test (answers: the injection proof).
- **Evidence seam:** unit factory test (limit + thread_id injected), smoke's real-run through make_stream_fn, mirror declaration.
- **Not in scope:** the content-addressed replay model (separate), constructor-surface changes, CI changes.
- **Triggered review policies:** change-admission
