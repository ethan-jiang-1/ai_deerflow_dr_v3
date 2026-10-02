# DeerFlow Deep Research Harness (v3)

This independent Python project is the downstream **Deep Research Harness** for DeerFlow
2.1. It is a *runtime harness*, not a single question-to-report pipeline: it is the stable
execution and control environment that creates, drives, and disposes of research runs.

**v3 rewrite, skeleton stage.** The philosophy carries over from v2; the implementation
route is inverted: the research cognition engine is DeerFlow's native deep research
capability (lead agent + `deep-research` skill + subagent delegation), and this harness
keeps the deterministic, inspectable parts:

- **Run Bundles.** Each run gets an independently deletable durable record — delete a
  Bundle and the Harness keeps working, while that run becomes permanently unavailable.
  The Harness owns no durable run state.
- **Explicit composition.** Public host routes are fixed to `all_real`; fixture recipes
  report `fixture`; the same graph can be exercised with zero credentials. Fixture
  adapters live only in `src_fixtures/` (excluded from the production wheel).
- **Models propose, code disposes.** Candidate work, evidence, and routes are admitted
  only by deterministic owners (validators, ledger, gates, graph).

> Skeleton notice: none of the above is implemented yet. The specification tree is
> intentionally empty; every capability grows from a v3 change, starting from the
> boundary plan at `_backlog/plans/2026-10-02-digest-deerflow-native-deep-research.md`
> in the repository root.

## Entry Surfaces

Not defined yet. The v2 ladder (CLI / TUI / debugger) is a reference shape, not a
commitment; v3 surfaces are decided by the boundary plan and its changes.

## Quick Start

```bash
make install    # skeleton stub (announces that nothing is installed yet)
make verify     # skeleton stub (announces that nothing is verified yet)
```

Requirements once implementation lands: Python 3.12+, `uv`, and the sibling DeerFlow
harness at `../deerflow/backend/packages/harness` (already declared in
`[tool.uv.sources]`).

## Reading Map

| Need | Start here |
| --- | --- |
| Scope, layers, and boundaries | [`AGENTS.md`](AGENTS.md) |
| Why v3 exists and what the harness keeps vs. delegates | [v3 direction note](AGENTS.md) + the boundary plan above |
| Runtime and authority boundaries | [`docs/runtime-architecture.md`](docs/runtime-architecture.md) |
| Local commands and profiles | [`docs/local-operations.md`](docs/local-operations.md) |
| How to prove a change | [`docs/testing-and-evaluation.md`](docs/testing-and-evaluation.md) |
| Product vocabulary | [`CONTEXT.md`](CONTEXT.md) |
| Documentation index | [`docs/README.md`](docs/README.md) |
