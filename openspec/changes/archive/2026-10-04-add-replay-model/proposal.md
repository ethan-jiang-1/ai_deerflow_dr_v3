# Proposal

## Why

The stand-in ladder's level 1 (scripted model) pins behavior contracts but cannot regress-test REAL model I/O — and real runs cost tokens, minutes, and non-determinism (the EASA arc needed five runs). The digest's level 2 (content-addressed replay) converts one real run into a permanent deterministic fixture. This change lands it: record once, replay forever.

## What Changes

- `runtime/fixtures/replay_model.py`: `RecordingChatModel` (wraps a real model, delegates `_generate`, records normalized-input-hash -> output to a JSONL sink) and `ReplayChatModel` (serves recorded outputs by the same hash; misses fail loudly naming the known keys and an input preview). Normalization strips volatile content (dates, UUIDs, system-reminder blocks) before hashing.
- A real recording: one small real-ladder run through `RecordingChatModel` produces `tests/fixtures/replay/real-model-io.jsonl` (committed, no key inside).
- Unit tests: hash hit, loud miss, normalization stability; a replay test serving the recorded answer deterministically.

## Capabilities

### New Capabilities
(none — test infrastructure; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- New: `runtime/fixtures/replay_model.py`, `tests/fixtures/replay/real-model-io.jsonl`, `tests/unit/test_replay_model.py`. No product code, no CI changes.

## Change Focus

- **Primary module / causal owner:** `runtime/fixtures/replay_model.py` — the model-boundary stand-in ladder's level 2.
- **Seam classification:** deterministic-guardrail — real recorded I/O served by hash; the model boundary is the only substitution point.
- **Question:** How does a real run's model I/O become a permanent deterministic fixture (record once via a delegating wrapper, replay by normalized-input hash with loud misses), converting the real-ladder's most expensive evidence into zero-cost regression?
- **Necessary adjacent/external contracts:** the digest's level-2 design (answers: content-addressing over turn-indexing, normalization rules, the miss discipline); the use: seam (answers: how the replay model reaches the agent in future smoke scenarios); the real EASA recording run (answers: the fixture's provenance).
- **Evidence seam:** unit tests (hash hit, loud miss, normalization stability) red-green + a real recording run producing the fixture + a replay test serving the recorded answer.
- **Not in scope:** full agent-loop replay via the use: seam (future — needs the recorded flow to match the agent's multi-call pattern), delegated/subagent streams.
- **Triggered review policies:** change-admission
