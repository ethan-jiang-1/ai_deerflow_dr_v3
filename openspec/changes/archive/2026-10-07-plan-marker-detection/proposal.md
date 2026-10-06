# Proposal

## Why

The plan gate's first real-ladder demonstration (2026-10-07, bundle 58b5440e) exposed a
determinism defect: the run engine's terminal picture carries only the final AI
message's tool calls, so a research turn that ends in a plain-text report is
structurally indistinguishable from a plan turn. The gate fired on the finished
REPORT (journaled `plan_proposed`/`plan_skipped` at the run's end), presented the
report to the operator as a "plan", and the injected skip message triggered a
wasteful second research pass (36 searches across two passes). The scripted smoke
journeys passed because their turn shapes matched the implementation's assumption;
only a real agent loop revealed it.

## What Changes

- The plan-request framing now asks the agent to wrap the proposed plan in explicit
  markers (`<research-plan>` … `</research-plan>`), the same technique the framework
  itself uses for the `deerflow_error_fallback` marker.
- The engine engages the plan gate ONLY when the final text carries the markers; the
  extracted inner text is the plan (markers never reach the hook, the injection, or
  the materialized file). A turn without the markers degrades the gate honestly —
  including a research report, a chatty non-plan answer, or an empty reply — no
  matter what tool calls the turn made. Detection is deterministic content
  structure, not behavioral inference.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `deerflow-wiring`: the plan-phase detection rule changes from "the first
  plain-text turn is the plan" to "the first final text carrying the plan markers is
  the plan; marker-less turns degrade honestly".

## Impact

- Code: `runtime/run_engine.py` (framing suffix, marker extraction, degradation
  rule), no CLI/render/entry changes.
- Tests: plan-phase unit tests move to marked turn shapes; a regression case pins
  the defect (a research-report turn without markers must complete without gating);
  smoke journeys wrap the scripted plan in markers and gain a marker-less
  degradation journey (the demo scenario, scripted).
- Docs: playbook and research-process notes gain one line each (markers are the
  gate's engagement protocol).

## Change Focus

- **Primary module / causal owner:** `runtime/run_engine.py` — owns the plan-phase detection whose heuristic was wrong.
- **Seam classification:** wiring — the fix replaces a behavioral inference with deterministic content-structure detection; no prompt semantics beyond the marker request, no admission or state rules change.
- **Question:** How does the engine distinguish a proposed plan from a research report when both end in plain text, deterministically and without force-blocking?
- **Necessary adjacent/external contracts:** deerflow-wiring engine honesty rules (does marker-less degradation keep the terminal rules intact?), smoke lane (can the defect scenario be scripted as a regression journey?).
- **Evidence seam:** red-green unit tests including the demo's exact scenario as a regression (report turn without markers completes ungated); smoke marker and degradation journeys; `make verify` + `make smoke` + checkers.
- **Not in scope:** CLI prompt changes, marker syntax negotiation with the model beyond the framing request, materialization semantics (unchanged), the clarification rules (unchanged).
- **Triggered review policies:** node-agent-workflow-integrity, control-and-recovery

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
|---|---|---|---|---|---|---|---|
| 计划请求框架消息 v2（追加标记协议） | node-agent | 不变：「按什么角度与查询策略研究」；新增唯一要求：计划全文包在 `<research-plan>` 标记内输出 | 问题文本（用户）；框架后缀（harness，任务级，与 v1 同类） | 消息不授予工具；标记只是输出格式约定，enforcer 是引擎的确定性提取 | 标记内文本为计划候选；无标记一律降级——裁决是内容结构，不是模型意图猜测 | 模型不遵循标记格式 → 诚实降级照跑（journal plan_gate_degraded）；有界：计划轮 + 既有反问预算 | journal plan_* 事件 + 脚本梯回归测试（含真梯缺陷场景的脚本化复刻） |
