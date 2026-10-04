# DeerFlow Deep Research Harness (v3)

This independent Python project is the downstream **Deep Research Harness** for DeerFlow
2.1. It is a *runtime harness*, not a single question-to-report pipeline: it is the stable
execution and control environment that creates, drives, and disposes of research runs.

**v3 rewrite, implemented core.** The philosophy carries over from v2; the implementation
route is inverted — v3 borrows DeerFlow's native deep research capability instead of
hand-building the research graph (full telling: root `README.md`). This harness keeps:

- **Run Bundles.** Each run gets an independently deletable durable record — delete a
  Bundle and the Harness keeps working, while that run becomes permanently unavailable.
  The Harness owns no durable run state.
- **Explicit composition.** Public host routes are fixed to `all_real`; fixture recipes
  report `fixture`; the same workflow can be exercised with zero credentials. Fixture
  adapters live only in the runtime fixtures package (excluded from the production wheel).
- **Models propose, code disposes.** Candidate work, evidence, and routes are admitted
  only by deterministic owners (validators, ledger, gates).

## Entry Surfaces

The entry surface is live: the six-verb CLI (`create` / `status` / `watch` / `cancel` /
`refine` / `inspect`) over the run-bundle substrate, plus the make lanes (`test`,
`verify`, `smoke`, `create`, …). The menu with one line per command — and routing to the
procedure playbook — is [`COMMANDS.md`](COMMANDS.md).

## Quick Start

```bash
make verify    # application unit gate: stdlib unittest suite, offline-safe
make create PROBLEM="研究问题"   # zero-credential fixture research run
```

Requires Python 3.12+, `uv`, and the sibling DeerFlow gitlink at `../deerflow`
(submodule, already declared in `[tool.uv.sources]`). The release face is exactly this
tree plus that gitlink; a deterministic guard (`check_release_face.py` in the
repository's governance suite) fails loudly when the face is violated.

## Reading Map

| Need | Start here |
| --- | --- |
| Scope, layers, and boundaries | [`AGENTS.md`](AGENTS.md) |
| 边界、分层与所有权（v3 为何存在、harness 留什么） | [AGENTS.md 引言段](AGENTS.md) |
| Runtime and authority boundaries | [`docs/runtime-architecture.md`](docs/runtime-architecture.md) |
| Local commands and profiles | [`docs/local-operations.md`](docs/local-operations.md) |
| How to prove a change | [`docs/testing-and-evaluation.md`](docs/testing-and-evaluation.md) |
| Product vocabulary | [`CONTEXT.md`](CONTEXT.md) |
| Documentation index | [`docs/README.md`](docs/README.md) |
