# Design

## Context

The plan gate (change 2026-10-07-plan-review-gate) detects the plan as "the first
plain-text turn with no tool calls". The real-ladder demo (bundle 58b5440e) proved the
assumption false on the real agent loop: the terminal picture carries only the final
AI message's tool calls, so a research turn ending in a text report has an empty
terminal tool-call set exactly like a plan turn — the gate fired on the finished
report and a skip injection caused a second research pass.

## Goals / Non-Goals

**Goals:** deterministic plan detection that no behavioral inference can fool; the
demo's exact scenario becomes a scripted regression; marker text never leaks into the
hook, the injected continuation, or the materialized file.

**Non-Goals:** no CLI/prompt changes, no materialization semantics change, no
clarification-rule changes, no negotiation if the model ignores markers (degrade is
the honest answer).

## Decisions

### D1 — Markers are the only engagement signal

The framing asks for `<research-plan>` … `</research-plan>` around the plan. The
engine gates iff the final text contains both markers; everything else — report,
chatty answer, empty, tool calls or not — degrades. This mirrors the framework's own
`deerflow_error_fallback` marker technique (a deterministic content-structure signal
on the final message). Rejected: keeping the tool-call heuristic as a secondary
signal — the demo proved it is not a signal at all on the real loop.

### D2 — Extraction and hygiene

`plan_text = final_text.split(OPEN)[1].split(CLOSE)[0].strip()` with presence checks;
if the inner text is empty, degrade. The hook, the injection, and
`request/plan-gen1.md` see the inner text only.

### D3 — The framing gains one sentence

The plan-request suffix now states the marker protocol and that after a clarification
answer the plan should be re-emitted with markers. Everything else in the framing is
unchanged.

## Risks / Trade-offs

- [The model ignores markers] → Honest degradation: the run proceeds ungated exactly
  as before the gate existed; journaled. The demo scenario (report without markers)
  is pinned as a smoke regression.
- [Marker text collides with genuine content] → The markers are distinctive enough;
  worst case the engine gates on a false positive once, the operator skips, the run
  proceeds — bounded by the same three-way prompt.

## Migration Plan

Pure logic replacement inside the plan phase; headless unchanged; rollback is revert.
