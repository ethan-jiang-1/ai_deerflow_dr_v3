# Proposal

## Why

Measured: one deep-research bundle's checkpoint.sqlite reached 1.0G (five generations x 1000 steps in the framework's default `full` mode — every per-step write stores the whole message list), while short runs cost 192K. Deep research on a per-question basis is unsustainable at that slope; the framework ships the fix as a config knob (`checkpoint_channel_mode: delta` with `snapshot_frequency`), which the harness never declared.

## What Changes

- Both checked-in configs declare `database: {checkpoint_channel_mode: delta, checkpoint_delta: {snapshot_frequency: 10}}` — full snapshots every 10 per-step writes (the framework's documented default cadence), materially smaller checkpoints, coarser resume granularity accepted.
- The known-limitations row (checkpoint growth) closes as addressed-by-declaration, with the honest caveat: the delta path relies on the framework's delta-history patch, which carries a version-validation warning on langgraph 1.2.12 — the smoke and the real-run read path are the coverage.

## Capabilities

### New Capabilities
(none — a config declaration; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- Modified: `config/base.yaml`, `config/fixture.yaml`, `docs/known-limitations.md`.
  No code changes; existing bundles' full-mode data stays readable (mode affects writes).

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/config/` — the framework's database checkpoint mode is a config-face knob; the harness declares it explicitly.
- **Seam classification:** wiring — a config declaration with a measured problem and a measured fix.
- **Question:** How does checkpoint growth stop exploding on deep research (1.0G for one five-generation bundle vs 192K for short runs) — by declaring the framework's delta checkpoint mode (full snapshots every 10 per-step writes) — with function verified on the real stack and the size effect measured on a real run?
- **Necessary adjacent/external contracts:** the framework's database config (answers: checkpoint_channel_mode/snapshot_frequency semantics and the restart/agreement requirements); the InMemorySaver delta-history patch warning on langgraph 1.2.12 (answers: the risk the smoke must cover).
- **Evidence seam:** smoke green (multi-turn + readable checkpoint on the delta mode) plus a small real run measured against the 192K short-run baseline, with the prior-thread read path (get_tuple) exercised.
- **Not in scope:** migrating existing bundles' DBs (old bundles keep full-mode data; reads stay compatible), snapshot_frequency tuning beyond the framework default.
- **Triggered review policies:** change-admission