# Design

## Context

The EASA arc (five caps to finish one briefing on a 209-message thread) is the evidence;
the plan card pins the direction. Policy routing: change-admission.

## Decisions

1. The rule stays pure: the caller supplies the fresh thread id; the rule migrates and
   records lineage. Default behavior (no id) is unchanged — no silent migration.
2. The summary is a mechanical projection (counts + question + prior-answer excerpt),
   written by deterministic code; the model decides how to USE it, never what it says.
3. prior_thread_ids defaults to an empty tuple (backward-compatible from_dict).

## Alternatives

Model-written summaries — rejected (cognitive authority). Always-fresh refine —
rejected (silent behavior change; the caller opts in).

## Risks / Trade-offs

[Summary loses detail the model needed] -> the prior checkpoints remain replayable
(lineage recorded); a heavier seed is a later, evidenced adjustment.

## Migration Plan

Unit red-green -> real EASA refine on the light thread completing -> receipts ->
archive -> commit.

## Open Questions

(none)
