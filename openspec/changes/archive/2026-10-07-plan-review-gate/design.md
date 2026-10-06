# Design

## Context

`run_engine._drive` loops `_consume_turn(handle, stream_fn, message, ...)`; a turn
ending in plain text with no unanswered clarification and no stop reason currently
completes the run and submits the text through admission. The interactive
clarification change added `on_clarification` (hook → answer → same-thread
continuation; decline → bounded auto-reply). `entry.run_foreground` passes hooks to
`run_research`. The CLI gates interactivity on TTY or `DEEP_RESEARCH_INTERACTIVE`.
`request/` holds `problem.txt` and `refine-N.txt`; the journal's closed category set
admits only the eight declared categories; lifecycle entries are evictable,
admission anchors are not. Smoke drives `cli.py` as a subprocess with piped stdin
and the env override.

## Goals / Non-Goals

**Goals:**
- The operator sees and shapes the research plan before the expensive turns run.
- The confirmed plan persists as a request artifact and threads into the run.
- Headless contexts are byte-identical to today (no plan phase, no extra round).
- The gate degrades honestly when the model ignores the framing.

**Non-Goals:**
- No harness-owned planner role in `agents/` (the deferred bounded-role reopen is
  explicitly not taken — the lead agent's own planning ability is reused).
- No in-place plan text editing (append-only revision note; a text editor belongs
  to a service form).
- No plan gate on refine generations (the direction document already is one).
- No cross-process approval, no scheduled runs, no upstream changes.

## Decisions

### D1 — Plan turn inside the lead agent loop, not a harness planner role

The first message becomes problem text + a plan-request framing suffix; the agent's
plain-text reply is the plan. This reuses the continuation machinery wholesale and
avoids reopening the Phase 5 deferred `agents/` bounded-role question. Rejected
alternative: a separate cheap planner model call owned by the harness — a new
bounded cognitive role (prompt authoring, candidate contract, repair loop) is a
much larger surface than this feature needs.

### D2 — Phase detection is structural, not marker-based

A turn in the plan phase is THE PLAN iff it ends in plain text with zero tool calls
and no unanswered clarification. A first turn with tool calls means the model
researched despite the framing: journal `plan_gate_degraded`, clear the phase, and
let the existing terminal handling proceed (the run simply behaves as today). No
markers, no output-format parsing of the plan, no force-blocking. The clarification
check stays FIRST in the chain, so a vague request in the plan phase routes through
the existing ask/answer loop and the plan arrives on the next plain-text turn —
priority emerges from the model's judgment, exactly as the driver specified.

### D3 — Hook contract mirrors clarification, with a richer return

`on_plan(plan_text) -> str | None`: a string is the plan to execute (the CLI
composes amend = original plan + "用户修订意见：" + note); None means skip. Abort is
the hook raising (the CLI's `q` raises SystemExit; the active bundle takes the
existing dead-owner crash-transfer path — the same honest outcome as Ctrl-C).
Engine-side accounting: `awaiting_plan` is a loop-local phase flag, never state —
the bundle stays `active` throughout, so no state-machine or persistence semantics
change.

### D4 — Continuation messages are stable, provenance-marked where harness-authored

Confirm/amend: `研究计划已确认（或经用户修订）。严格按以下计划执行研究并产出最终报告：`
+ plan text. Skip: `跳过计划注入，按你自己的判断研究并产出最终报告。` (the plan text
remains in-thread context either way — the messages change emphasis, not memory).
The framing suffix and both continuations are stable constants alongside
AUTO_REPLY_PREFIX; scripted tests pin them.

### D5 — The confirmed plan is materialized to `request/plan-gen1.md`

The plan is the user-confirmed scope contract; the journal's lifecycle entries are
evictable, so the file — not the journal — is the durable record. Written only on
confirm/amend, atomically, before the research turns; skip/abort/degrade write
nothing (the journal still carries `plan_proposed`/`plan_skipped`/`plan_gate_degraded`).
The artifact ownership table gains one row; deletion follows the bundle.

### D6 — Gating: same switch as clarification, generation-1 only

The CLI builds the plan handler under the same TTY/`DEEP_RESEARCH_INTERACTIVE`
gate and passes it on `create` only (refine passes nothing; the engine also guards
on `generation == 1`). One switch, two gates; a user who wants no gate for a run
answers `s` at the prompt (skip is one keystroke, and the thread keeps the plan as
context).

## Risks / Trade-offs

- [The model ignores the framing and researches immediately] → D2's honest
  degradation: journaled, run proceeds under today's rules, nothing is blocked.
  The smoke's scripted turns pin both the compliance and degradation paths.
- [An extra model round per interactive run] → Interactive contexts only; `s`
  skips; one alignment round is cheap against one misdirected research run (the
  economics the driver approved).
- [Revision is append-only, not in-place editing] → Terminal-appropriate v1; noted
  in the plan card as a service-form follow-up.
- [Abort leaves an active bundle] → Identical to Ctrl-C today; `status`
  crash-transfers to `failed-resume` honestly. Documented in the prompt hint.
- [Plan-phase flag lost on crash] → The bundle restarts as a failed-resume run;
  refine can relaunch — no half-gated state can persist because the phase is
  loop-local.

## Migration Plan

Pure addition; no schema or data migration. Headless callers observe no change.
Rollback is reverting the commit.
