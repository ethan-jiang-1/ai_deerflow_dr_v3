# Context Map

This repository has three related contexts. Each has its own vocabulary so product
responsibility, host integration, and change governance do not blur together.

## Contexts

- [DeerFlow Host](./CONTEXT.md) - provides the host platform and public integration boundary.
- [Deep Research Product](./deep_research_harness/CONTEXT.md) - helps people obtain research outcomes.
- [OpenSpec Governance](./openspec/CONTEXT.md) - turns agreed product decisions into reviewable changes.

## Relationships

- **DeerFlow Host -> Deep Research Product**: the host supplies the runtime boundary; the product owns its user-facing research outcome.
- **OpenSpec Governance -> Deep Research Product**: approved requirements constrain product changes; governance does not become runtime behavior.
- **DeerFlow Host <-> OpenSpec Governance**: host boundaries constrain a change's scope; governance records rather than expands those boundaries.

## Reading order for a fresh agent

1. [AGENTS.md](AGENTS.md) — scope and boundaries.
2. [_backlog/plans/2026-10-02-digest-deerflow-native-deep-research.md](_backlog/plans/2026-10-02-digest-deerflow-native-deep-research.md) — the v3 front door: how this rewrite leverages DeerFlow's native deep research capability, and the open boundary questions. (骨架期占位；首个 walkthrough 落地后替换为本产品的 run lifecycle 前门。)
3. The three context files below — dictionaries, read on demand.
