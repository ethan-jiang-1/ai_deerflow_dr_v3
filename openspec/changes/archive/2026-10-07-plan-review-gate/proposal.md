# Proposal

## Why

The interactive clarification change gave the agent a voice when it judges a request
vague, but the real-ladder demonstration exposed the gap: deepseek-flash's ask
threshold is high, so a merely-fuzzy prompt sails straight into an expensive run on
guessed intent. Benchmarking Gemini Deep Research (the driver's investigation,
2026-10-07) identified the category's highest-value human gate: a visible, editable
research plan presented for confirmation BEFORE the run spends budget — alignment on
a concrete artifact rather than abstract Q&A. The driver approved building it.

## What Changes

- The run engine gains an optional plan hook (`on_plan`), used only for generation-1
  runs in interactive contexts. The first turn's message becomes the problem text
  plus a plan-request framing; the first plain-text terminal (no tool calls, no
  unanswered clarification) is the PROPOSED PLAN — not the final answer, never
  admitted.
- The hook receives the plan text and returns the plan to execute (approved or
  amended — the CLI appends the operator's revision note to the original) or None
  (skip: proceed without plan injection). Aborting raises from the hook (the CLI's
  `q` path; the bundle takes the honest crash-transfer outcome).
- The approved/amended plan is injected as the continuation message on the same
  thread, and materialized as `request/plan-gen1.md` — the user-confirmed scope
  contract joins the evidence chain (journal lifecycle entries are evictable; the
  request artifact is not).
- Clarification composes naturally: if the agent finds the request too vague to plan,
  it may call `ask_clarification` in the plan phase — the existing hook answers it,
  and the next turn's plain text is the plan. "Ask when vague, plan when clear" is
  the model's judgment, not a hardcoded rule.
- Honest degradation: if the model ignores the framing and researches in the first
  turn (tool calls present), the gate journals `plan_gate_degraded` and the run
  proceeds under today's rules — the gate never force-blocks the agent.
- CLI three-way prompt on the shared renderer: Enter = confirm · typed text = append
  revision note · `s` = skip · `q` = abort. Refine (generation > 1) is exempt — its
  direction document already IS a user-authored plan.
- Headless behavior (no TTY, no `DEEP_RESEARCH_INTERACTIVE`) is byte-identical to
  today: no plan phase, no extra model round.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `entry-surface`: the optional-hook pattern extends to the plan hook; the proposed
  plan renders through the shared module; the confirmation prompt is a stable
  phrase; interactive gating matches clarification (TTY or env override), and a
  non-interactive context never enters a plan phase.
- `deerflow-wiring`: the run-engine requirement gains the plan-phase preamble —
  with a plan hook on a generation-1 run, the first plain-text terminal is the
  proposed plan (never admitted), clarification may interleave under existing
  rules, the confirmed plan is injected as the continuation, and a tool-bearing
  first turn degrades the gate honestly.
- `run-bundle`: new requirement — the approved research plan is materialized as a
  request artifact (`request/plan-gen1.md`) before the research turns; skip, abort,
  and degradation create no file; deletion follows the bundle.

## Impact

- Code: `runtime/run_engine.py` (plan-phase state, hook, journal events,
  materialization), `runtime/interaction/cli.py` (handler, three-way prompt),
  `runtime/interaction/render.py` (plan rendering + prompt hint),
  `runtime/entry.py` (pass-through).
- Tests: `tests/unit/runtime/test_run_engine.py` (plan turn, amendment, skip,
  degrade, clarification-during-plan), new interaction tests (gating, three-way
  handler, wiring), smoke journeys with piped confirm/amend.
- Docs: playbook gotcha, harness README chain note, research-process note,
  run-bundle artifact table (+ plan-gen1.md), tests/README registrations.
- No state-machine change; no journal category change; no CLI verb change;
  headless/smoke behavior unchanged.

## Change Focus

- **Primary module / causal owner:** `runtime/run_engine.py` — owns the turn loop
  that must distinguish a plan-phase terminal from a research terminal and inject
  the confirmed plan; the re-invocation loop owner per the run-bundle spec.
- **Seam classification:** human-decision — the gate inserts a human decision
  (approve/amend/skip) between the agent's proposal and the expensive research;
  the framing message and injection are wiring, but the decision point is human.
- **Question:** How does the harness obtain a research plan from the lead agent,
  hand it to the operator for approval before budget is spent, and continue the
  run with the confirmed plan — without breaking headless contexts, the
  clarification rules, or the terminal/admission honesty?
- **Necessary adjacent/external contracts:** entry-surface hook-and-render contract (does the plan render and prompt through the shared module with the same gating?), deerflow-wiring engine honesty (is the plan-phase terminal excluded from admission and the injection on the same thread?), run-bundle request artifacts (where does the confirmed plan persist?), smoke lane (can a subprocess drive the three-way prompt without a TTY?).
- **Evidence seam:** red-green on `tests/unit/runtime/test_run_engine.py` with
  scripted plan turns first; interaction gating/handler tests; smoke journeys with
  piped stdin; `make verify` + `make smoke` + governance checkers as the gate.
- **Not in scope:** a harness-owned planner model role in `agents/` (the deferred
  Phase 5 bounded-role reopen is explicitly not taken), in-place text editing of
  the plan (append-only revision note), plan gates on refine generations,
  cross-process plan approval, scheduled/async runs, upstream changes.
- **Triggered review policies:** node-agent-workflow-integrity, human-interaction-integrity, control-and-recovery

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
|---|---|---|---|---|---|---|---|
| 计划请求框架消息（首轮注入的任务级框架） | node-agent | 「这个问题值得按什么角度、查询策略与来源类型研究？」——仅请求一份计划，不请求研究本身 | 问题文本来自 request/problem.txt（用户）；框架后缀由 harness 撰写，任务级内容，与 AUTO_REPLY 同类；不改 system prompt | 消息不授予任何工具/权限/路由；agent 可见面不变；引擎只组合消息，enforcer 是现有 stream 缝 | 计划文本（自由格式候选）；裁决在 on_plan 人工闸门（确认/修订/跳过），引擎物化决定，不自动接纳 | 模型无视框架直接开搜 → 闸门诚实降级（journal plan_gate_degraded，按现行规则跑完）；有界：一个计划轮 + 既有反问预算 | journal plan_* 事件 + 脚本梯 unit/smoke（伪造计划轮与降级轮） |
| 确认/修订注入消息（继续轮的指导内容） | node-agent | 「按已批准（或经用户修订）的计划执行研究并产出最终报告」 | 计划文本经用户确认（人工权威）；框架前缀由 harness 撰写；用户修订意见原样附加 | 同上：不授予工具；执行仍受既有 recursion/终态规则约束 | 最终报告；准入仍走既有 validator/admission，本表面零改动 | 既有终态规则（stop_reason/error-fallback/取消）不变 | checkpoint 线程 + request/plan-gen1.md + searches/ 证据链 |
| CLI 三路确认提示与计划物化 | no-agent | 纯确定性表面：渲染计划、读一行输入、写一个文件；无模型参与 | 输入来自操作者（人工）；物化内容由引擎传入 | 无工具；TTY/env 门控沿用 interactive-clarification 的既有 enforcer | 物化的 plan-gen1.md 与 journal 决定事件；文件写入原子（atomic write） | EOF/异常 → 拒答/放弃路径（既有 crash-transfer）；无认知失败面 | interaction unit 测试 + smoke 管道旅程 |
