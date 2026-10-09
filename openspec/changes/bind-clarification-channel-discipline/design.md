# Design

## Context

See proposal.md — Why. Mechanically, the black hole exists because the run engine's
turn classification has exactly two outcomes for clarification-shaped terminals:
unanswered (drives the hook / bounded continuation) or everything else. The framework's
ClarificationMiddleware answering a call in-turn lands that call in the answered set,
so the terminal is classified "everything else" and no clarification round is recorded
— even though the model did ask, and the answer it received was the framework's, not a
human's. The smuggling (phenomenon 1) and sibling-drop (phenomenon 2) are the same
confusion seen from the prompt side: the framing asks for a plan, but nothing binds
which channel carries which intent. The app owns the framing text and the journal; the
middleware is read-only upstream. Backlog plan:
`_backlog/plans/2026-10-07-clarification-channel-discipline.md`.

## Goals / Non-Goals

- Goals: complete interaction-history reconstruction (every clarification round
  journals exactly once); channel-discipline wording on the plan-request framing; all
  of it as deterministic guardrail work with red-green evidence.
- Non-Goals: changing the middleware (no buffering, no sibling execution); changing
  terminal rules, bound semantics, admission, or state-machine transitions; blocking
  or rewriting smuggled plan confirmations; any headless behavior change beyond new
  journal events; extend the discipline to `AUTO_REPLY_PREFIX` (headless message bytes
  stay as-is — see Decision 3).

## Decisions

1. **Companion predicate, same home** — `absorbed_ask_clarifications(observation)` in
   `domain/clarification.py`: the ask_clarification calls whose call id IS in
   `answered_call_ids`. Exactly symmetric to `unanswered_ask_clarification`, so the
   two together partition every ask_clarification the turn carries. Alternative
   (one classifier returning per-call dispositions) rejected: the existing pattern is
   single-purpose pure predicates consumed by the runtime; symmetry keeps the wiring
   dumb and the tests obvious. The framework-echo exclusion
   (`_is_framework_clarification_echo`) is untouched: a self-echoed question awaiting
   human input is still "unanswered" and keeps driving the hook path.
2. **Journal at the classification site** — `_drive` journals
   `lifecycle`/`clarification_absorbed` (detail `{"question": <question_text>}`, one
   entry per absorbed call, via `clarification.question_text`) immediately after the
   `detected` computation, before any terminal decision or plan-gate branch. So an
   absorbed round is recorded even when the same turn then degrades the plan gate or
   completes the run. Alternative (journaling inside `_consume_turn`) rejected: that
   function owns stream consumption and tool-result materialization; round
   classification is the turn-loop decision and already owns the sibling
   `clarification_*` events. No new journal category — `lifecycle` already carries
   `clarification_asked/answered/declined`; the closed category set is untouched.
3. **Wording rides the plan-phase framing only** — `PLAN_REQUEST_SUFFIX` gains two
   explicit sentences: a question turn carries ONLY `ask_clarification` and no other
   tool call (siblings are dropped by design — naming the consequence makes the cost
   legible to the model), and plan confirmation travels ONLY through the plan markers,
   never inside an `ask_clarification` call. Constants stay stable (scripted tests pin
   them). `AUTO_REPLY_PREFIX` and `PLAN_SKIP_MESSAGE` stay byte-identical: the observed
   smuggling happened in the plan phase, where the framing is the model-visible
   contract; extending the auto-reply would change headless bytes for unproven
   benefit. If the TTY baseline shows absorption outside the plan phase, that is a
   recorded finding for a follow-up card, not silent scope growth here.
4. **No hard block, compliance measured** — a smuggled confirmation is recorded and
   then handled by today's rules (the plan-gate wording already asks the model to
   re-present a marked plan after an answered question). Whether the wording works is
   a real-ladder measurement against a driver-run TTY baseline — a declared human
   prerequisite for acceptance, run before the wording change is judged, not after.
5. **deerflow/ stays closed** — the middleware's drop and in-turn answer behavior is
   taken as observed (recorded in the backlog plan with bundle ids); nothing in the
   framework is read beyond its already-recorded public behavior, and nothing in it is
   modified.

## Risks / Trade-offs

- [措辞遵从率不保证——模型可能继续走私] → 诚实降级哲学照旧：不硬拦，
  `clarification_absorbed` 让每次走私留下可测痕迹；TTY 基线先行，遵从率是测量结果
  而不是假设。
- [吸收检测依赖框架 answered 集的事件形状] → 形状已由合同 mirror 锁定（纯类型
  结构）；若上游改变回答方式使 call id 不再进入 answered 集，检测退化为现行
  "未答" 路径（今天的行为），不会更糟。
- [journal 体积增长] → 吸收轮是低频事件；`lifecycle` 的既有有界淘汰策略照旧，
  无新增保留义务。
- [先修提示词可能改变反问频率] → TTY 验收基线先行（backlog plan 风险表的约定），
  避免无基线调参；apply 阶段不解读基线，只叠加事件。

## Migration Plan

Additive only: one pure function, one journal event name, one message-constant
extension. No data migration; bundles whose journals lack the new event read exactly
as before. Rollback = revert the commit; old journals remain valid. The renderer's
journal display must be checked to show the new event name generically (task 3.4) so
`watch`/`inspect` never silently swallow it.

## Open Questions

- none — the TTY acceptance baseline is a declared human task inside the task
  breakdown (5.1), not an open design question.
