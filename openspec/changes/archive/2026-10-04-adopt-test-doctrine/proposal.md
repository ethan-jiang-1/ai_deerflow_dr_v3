# Proposal

## Why

The user asked for an honest assessment of our test strategy against DeerFlow's own self-testing system (the test-strategy digest, 10 files). The digest's one-line strategy — "离线确定性是默认，真实边界是显式 opt-in；测契约不测智能；每条架构规矩都有一个钉住它的测试；门禁自身也要被测试" — is largely ALREADY our shape (offline stdlib gate, opt-in real ladder, negative controls, gate red-proofs, contract mirror), but three things are missing and worth borrowing, and they should land as durable doctrine rather than verbal advice.

## What Changes

- `docs/testing-and-evaluation.md` is upgraded into the testing DOCTRINE doc: the one-line strategy, the lane table extended with an explicit 不证明什么 (what this lane does NOT prove) column, the deterministic-LLM stand-in ladder (level 1 present; level 2 content-addressed replay queued), and the borrow queue with digest citations.
- A follow-up plan card (`_backlog/plans/2026-10-04-test-doctrine-borrows.md`) queues the two borrow changes: ① content-addressed ReplayChatModel (record real runs once, replay deterministically — converts our most expensive evidence into permanent fixtures); ② skill-testing surface (the framework's SkillScan/review/waiver mechanism, serving skill customization).

## Capabilities

### New Capabilities
(none — guidance docs; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- Modified: `deep_research_harness/docs/testing-and-evaluation.md`. New: the follow-up plan card. No product code, no CI changes.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/docs/testing-and-evaluation.md` — the app-side testing doctrine doc; every future "怎么测"的问题从这里起答。
- **Seam classification:** deterministic-guardrail — the deliverable is a guidance document whose rules are backed by the existing green gates and the registered borrow queue; no model cognition and no runtime behavior change (guidance only).
- **Question:** 对照 DeerFlow 自测体系的 digest（test-strategy，10 篇），我们的测试思路与资产缺什么、借鉴什么、以什么形态沉淀（指导文档 + 挂钩实践），使纪律不再靠反复唠叨？
- **Necessary adjacent/external contracts:** the digest citation (answers: every borrowed rule carries its source anchor); the quality register (answers: where new machines/guards get registered); the follow-up plan card (answers: which borrows become changes, in what order).
- **Evidence seam:** doc hygiene + closeout gates; the doctrine's own hooks (lane table with 不证明什么 column; the borrow queue pinned in the follow-up plan card).
- **Not in scope:** implementing the borrow queue (replay model, skill-testing surface — separate changes queued via the plan card), CI duration sharding (premature at 90 tests).
- **Triggered review policies:** change-admission
