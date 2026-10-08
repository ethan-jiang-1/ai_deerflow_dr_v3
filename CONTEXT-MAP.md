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

## Shared words with two owners

- **profile** — 根 `profiles/` 是**本地运行配置**（宿主侧 ladder/profile，暂未注册）；
  `openspec/change-guidance/profiles/` 是**政策 profile**（change-guidance 的规则集）。
  同名异物，按目录归属读。

## Common Misreadings

- **profile** 同名异物（见上）——按目录归属读，别把运行配置当政策或反之。
- **"测试绿" ≠ "质量"**：每层证据只证明它断言的属性（车道表见
  [testing-and-evaluation](./deep_research_harness/docs/testing-and-evaluation.md)），
  单元绿不证明装配，装配绿不证明研究质量。
- **`engine/` 与 `run_engine`**：`engine/` 是裁决层（validator/gate 纯函数），
  `runtime/pump.py` 是运行泵——模块改名（2026-10-07）后旧文档若仍提
  `run_engine.py` 即已过期。

## Reading order for a fresh agent

The single entry chain is [AGENTS.md](AGENTS.md) — its routing table owns "where do I
start". This file is a vocabulary stop on that chain: read it when a boundary question
needs a term, then follow the three context files below on demand. Current active work,
if any, lives in the `_backlog` ledger ([_backlog/README.md](_backlog/README.md)).
