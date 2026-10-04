# Design

## Context

The real stream shapes are documented in the plan's protocol notes (flat chunks,
token-grained, values snapshots with full messages). The EASA small run already
produced a complete clean-completion stream; the recording re-captures it verbatim.

## Decisions

1. Record verbatim (type + full data dicts, JSON) — volatile values exist in the
   fixture but the assertions are shape-level; the fixture is the recording, the test
   owns what it asserts.
2. Replay through the engine on a fresh bundle (the events are self-contained; the
   thread id in them is irrelevant to the engine — it reads state.json).
3. Tamper negative control: mutate a recorded tool_calls field and the journal-shape
   assertion must go red (the flat-chunk bug's permanent scar, mechanized).
4. The recording utility is a committed make target (real API, explicit opt-in, never
   in CI) — future re-records are one command.

## Alternatives

Synthesizing the fixture from the diagnostic dump — rejected: partial/summarized data
re-introduces the assumption gap the bug taught. Recording via the fake model —
rejected (that is the fake shape again).

## Risks / Trade-offs

[The fixture bakes in one model's behavior] — accepted: it pins the real SHAPE; content
values are not asserted. [Recording needs a key] — explicit opt-in target, like
test-live in the digest.

## Migration Plan

Record → replay test red (fixture missing) → fixture committed → green → gates →
receipts → archive → commit.

## Open Questions

(none)
