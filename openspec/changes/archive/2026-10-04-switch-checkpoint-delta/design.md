# Design

## Context

Measured baseline: short real runs 192K; the EASA five-generation deep bundle 1.0G
(full mode). The framework example documents the delta mode and its cadence knob; the
client reads the mode from the app config (freeze_checkpoint_channel_mode). The
langgraph-version warning on the delta-history patch is the risk item. Policy routing:
change-admission; skip_specs.

## Decisions

1. Declare delta + snapshot_frequency 10 in both configs (one knob face, both ladders).
2. Coverage: the fixture smoke's multi-turn + readable-checkpoint case runs ON the
   delta mode; the real verification run also exercises the prior-thread read
   (get_tuple) so materialization is proven on the actual stack.
3. Old bundles stay as-is: mode affects writes, not reads; no migration.

## Alternatives

Stay full + accept the slope — rejected (measured 1GB). Higher snapshot_frequency —
deferred (the default cadence first; tune on evidence).

## Risks / Trade-offs

[Delta patch on langgraph 1.2.12] — the smoke + real-read coverage; a failure fails
loud in both. [Coarser resume granularity] — accepted (every 10 steps).

## Migration Plan

Configs -> smoke green -> real run measured vs 192K + read path exercised ->
receipts -> archive -> commit.

## Open Questions

(none)
