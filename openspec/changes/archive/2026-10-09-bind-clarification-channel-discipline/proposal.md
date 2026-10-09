# Proposal

## Why

The 2026-10-07 real-ladder dynamic review (bundle `runs/d_20261006/5128f695-…`, completed
g1/rev5, exit 0) exposed three same-root channel-discipline failures: (1) the model
smuggled "please confirm this plan" — full plan text included — into `ask_clarification`
instead of the `<research-plan>` gate, and headless auto-answering let it through,
burning the auto_proceed budget 2/2 and re-presenting the plan twice; (2) questions
issued alongside `web_search` calls triggered the framework middleware's by-design
sibling drop, discarding three searches that were re-issued next turn; (3) after budget
exhaustion, two more `ask_clarification` calls were absorbed by the answered set with
zero journal events — a black hole in the interaction history of a product whose
principle is evidence over feeling.

## What Changes

- **Channel discipline in the plan-request framing** (prompt/contract layer): the
  framing text is extended to bind the two channels — a question turn carries ONLY
  `ask_clarification` (no sibling tool calls; the framework will drop them by design),
  and plan confirmation flows ONLY through the plan markers, never inside an
  `ask_clarification` call. This is wording-level constraint under the existing
  honest-degradation philosophy: never a hard block; compliance is measured, not
  assumed. Coverage review: the constraint rides the plan-phase framing; headless
  auto-reply message bytes stay unchanged.
- **Absorbed clarifications become observable** (engine layer): when a terminal turn's
  `ask_clarification` calls are all resolved by the turn's own answered set — the
  framework answered them in-turn without the run's hook, so the existing detection
  predicate reports False — the engine journals each as `lifecycle`/
  `clarification_absorbed` with the question text. Headless and interactive alike. The
  journal's closed category set is unchanged; state-machine facts, bound semantics, and
  terminal rules are untouched (an absorbed round is recorded, never acted on).
- **Pure detection extended, not re-invented**: a companion predicate over the existing
  `TerminalObservation` (call id present in the answered set) joins
  `unanswered_ask_clarification` in `domain/clarification.py`.
- **Acceptance is a real-ladder rerun against a driver-run TTY baseline** (the baseline
  is a human task, UNVERIFIED until performed): the journal must reconstruct every
  interaction round including absorbed ones, and the smuggling-driven duplicate plan
  presentation / budget burn must not recur.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `run-bundle`: the clarification-continuation requirement now covers absorbed rounds —
  an `ask_clarification` resolved by the terminal turn's own answered set (framework
  answered in-turn, no hook involved) SHALL be journaled as its own clarification round
  so the interaction history is fully reconstructable; it changes no state-machine fact
  and consumes no bound.
- `deerflow-wiring`: the run-engine requirement gains (a) the plan-request framing's
  channel-discipline content — question turns carry only `ask_clarification`, plan
  confirmation only via plan markers — and (b) the engine's obligation to journal
  absorbed clarifications under the unchanged terminal rules.

## Impact

- Code: `runtime/pump.py` (`PLAN_REQUEST_SUFFIX` wording; absorbed-round journaling in
  the `_drive` loop), `domain/clarification.py` (companion pure predicate).
- Tests: `tests/unit/domain/test_bundle_domain.py` (absorbed predicate, symmetric with
  the unanswered predicate), `tests/unit/runtime/test_run_engine.py` (absorbed rounds
  journaled headless and interactive; no bound consumption; terminal rules unchanged),
  integration journey coverage if the existing fixture journey can express absorption.
- Docs: `docs/playbook/run-research.md` gotcha (channel discipline + absorbed events).
- No state-machine change; no journal category change; no CLI verb or flag change;
  headless terminal dispositions unchanged (new journal events only).
- The `deerflow/` gitlink is neither modified nor source-browsed for this change: the
  design rests on framework middleware behavior already observed and recorded in the
  backlog plan (`_backlog/plans/2026-10-07-clarification-channel-discipline.md`) — the
  sibling-drop stderr and the answered-set absorption.

## Change Focus

- **Primary module / causal owner:** `runtime/pump.py` — owns the turn loop that
  classifies stream terminals, journals interaction rounds, and composes the framing
  message; both remedies land where those two responsibilities already live.
- **Seam classification:** deterministic-guardrail — the change adds an honest journal
  trace for a turn shape the detector previously let pass silently, plus a wording-level
  contract on the framing message; no admission rule, terminal rule, state-machine
  transition, or human decision point changes, and no prompt capability is authored
  (LLM-Node gate step 1: the model-bearing symptom is answered by deterministic
  observability and channel wording, cognition untouched).
- **Question:** When the model smuggles a plan confirmation through `ask_clarification`
  or asks alongside sibling tool calls the framework will drop, how does the harness
  keep the interaction history fully reconstructable and bind plan confirmation to the
  plan-marker channel — without modifying the framework middleware or force-blocking
  the agent?
- **Necessary adjacent/external contracts:** `domain/clarification.py` pure predicate
  family (can absorbed detection stay a pure function over the terminal observation?);
  run-bundle journal contract (does the new event name fit the closed `lifecycle`
  category without touching the category set?); framework middleware semantics
  (read-only: sibling-drop and in-turn self-answer behavior, taken as observed).
- **Evidence seam:** red-green on `tests/unit/domain/test_bundle_domain.py` +
  `tests/unit/runtime/test_run_engine.py` (scripted absorbed-ask stream) first; smoke
  journey with piped answers; a driver-run TTY acceptance baseline measures
  marker/channel compliance before any wording is judged effective (UNVERIFIED until
  then); `make verify` + `make smoke` + governance checkers as the gate.
- **Not in scope:** modifying or buffering around the framework's sibling-drop
  middleware; new CLI verbs or flags; state-machine transitions; journal category
  changes; hard-blocking smuggled plan confirmations; guaranteeing model compliance
  (measured via baseline, not enforced); refine-generation gates (no plan gate there).
- **Triggered review policies:** node-agent-workflow-integrity, control-and-recovery, deerflow-downstream-boundary, change-admission

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
|---|---|---|---|---|---|---|---|
| 计划请求框架消息（`PLAN_REQUEST_SUFFIX` 通道纪律扩展措辞） | node-agent | 「先澄清则只提问、计划确认只走标记」——仅约束通道用途，不新增认知能力；与 plan-review-gate 的框架消息同类 | 问题文本来自 `request/problem.txt`（用户）；框架后缀由 harness 撰写；不改 system prompt、不改可见工具面 | 消息不授予任何工具/权限/路由；纪律是措辞约束，无运行时强制器——故配 journal 事件测量遵从率（诚实降级哲学） | 计划文本候选仍由 on_plan 人工闸门裁决；走私进反问通道的计划确认不被接纳为计划（无标记即不触发闸门），只留事件痕迹 | 模型无视措辞 → 不硬拦：走私轮按现行反问规则消耗预算并诚实失败，`clarification_absorbed`/既有 plan_* 事件留全痕；有界：既有 N=2 反问预算不变 | 脚本梯 unit 钉措辞常量 + journal 事件；真梯 TTY 基线（驾驭者跑）测遵从率 |
| 吸收反问 journal 事件（`clarification_absorbed`） | no-agent | 纯确定性表面：terminal observation 谓词扩展 + journal 追加；无模型参与 | 输入是流终态的 tool_calls 与 answered 集合（合同 mirror 已锁形状） | 无工具授予；事件是观察事实的投影 | 无候选：只记账，不改终态、不触发续跑、不消耗预算；准入合同零接触 | 无认知失败面；谓词误报由红绿+负对照测试锁定 | unit 红绿（吸收谓词 + 事件落账 + 无预算消耗负对照）+ journal 形状断言 |
