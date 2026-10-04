# Proposal

## Why

The flat-chunk bug proved the dangerous gap: fake events used the adapter's assumed shape, so every test stayed green while the real stream behaved differently — the drift only surfaced in a real (token-costing, non-deterministic) run. The digest's level-2 answer: record real runs once, replay them deterministically forever. This change records a real stream fixture and wires the replay, converting the most expensive debugging evidence into a permanent regression.

## What Changes

- **Recording**: a small real-ladder run captures the full raw event stream (type + verbatim data dicts) to `tests/fixtures/replay/real-small-stream.json`, via a reusable `make record-stream PROBLEM="…" CONFIG=base` target (the recording utility is committed, so future re-records need no new code).
- **Replay test**: `tests/unit/test_event_stream_replay.py` loads the fixture, replays the events through `run_research` on a fresh bundle, and asserts: terminal state, the journal's category/event sequence shape, and (tamper negative control) that mutating a recorded `tool_calls` field turns the journal-shape assertion red. Volatile values (ids, timestamps) are not asserted.
- **Doctrine doc**: the stand-in ladder table marks the real-event replay lane as landed.

## Capabilities

### New Capabilities
(none — test infrastructure over an already-spec'd engine; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- New: `tests/fixtures/replay/real-small-stream.json`, `tests/unit/test_event_stream_replay.py`, a Makefile `record-stream` target. Modified: `docs/testing-and-evaluation.md` (ladder row), no product code.

## Change Focus

- **Primary module / causal owner:** `tests/fixtures/replay/easa-small-stream.json` — the recorded real event stream IS the asset; the replay test owns its contract.
- **Seam classification:** deterministic-guardrail — real events replayed through the engine assert terminal honesty and journal shape; no model in the loop.
- **Question:** How does the real stream's exact shape become a permanent regression fixture (recording, replay through run_research, shape assertions), so adapter drift like the flat-chunk bug can never pass green again?
- **Necessary adjacent/external contracts:** the real stream protocol notes (answers: the shapes being recorded); run_research's terminal rules (answers: what the replay asserts — terminal state + journal categories); the recording utility (answers: how future re-records happen — make target).
- **Evidence seam:** the replay test green on the committed fixture; a tamper negative control (a modified event turns the assertion red); the recording utility documented.
- **Not in scope:** the content-addressed LLM replay model (A2, separate); asserting volatile values (ids/timestamps); recording real runs into CI.
- **Triggered review policies:** change-admission
