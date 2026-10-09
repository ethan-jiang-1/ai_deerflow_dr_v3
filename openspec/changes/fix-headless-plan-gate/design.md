# Design

## Context

BUG-001's confirmed root cause: `cli.py` `_plan_handler` returns None headless, and the
entry-surface spec pinned that ("no plan phase, no extra model round") — a design that
predates the skill-narrowing (the deep-research skill's plan-first methodology now makes
every research run plan-first). With no gate, the plan-shaped first turn falls through
`detected=None, awaiting_plan=False` to `completed`, and the plan is admitted as the
report. The pump's engine contract is conditional ("when a plan hook is provided") and
needs no change; the fix is at the CLI handler, plus an admission refusal face as defense
in depth. Four degenerate real bundles (2026-10-10) are the evidence; the corrected
diagnosis (the "smuggling" symptom was a misread of `answer_excerpt`) is on the BUG-001
card.

## Goals / Non-Goals

**Goals:**

- Headless first-generation `create` runs the full journey: plan proposed →
  auto-confirmed (journaled) → injected → research → report → admitted.
- Any path that still lands a plan as a report fails loudly at admission
  (`report_structure_violation`, plan-marker aspect) instead of admitting silently.
- The real-ladder acceptance: `behavior-profile`'s `min_search_calls` verdict no longer
  fires on a headless research run.

**Non-Goals:**

- No prompt/wording changes (H1 disproved: the suffix was never appended headless).
- No interactive-gate changes (TTY path untouched). No journal-vocabulary changes
  (reuses `plan_proposed`/`plan_confirmed`). No verdict-code changes (reuses
  `report_structure_violation`). No refine-path changes (generation > 1 never gated).

## Decisions

1. **Headless auto-confirm returns the plan verbatim** (not a skip): the confirmed plan
   is injected as the continuation, so the model executes its own plan — this is what
   restores the research journey. A skip would proceed without injection and leave the
   model without its plan context. Same philosophy as the clarification auto-reply
   (bounded automatic continuation); the extra model round is the deliberate price,
   now stated in the spec.
2. **The marker rule is the FIRST structure aspect** (before encoding/heading/Sources/
   envelope): a marker-wrapped text is categorically not a report — checking it first
   makes the rejection face unambiguous even when the plan mimics heading/Sources
   structure (the observed case: the plan's deliverables section satisfied the
   Sources-aspect regex).
3. **Marker constants move to `domain/plan.py`** (with `extract_plan`): the validator and
   the pump both consume them; the domain is the single owner of the shared vocabulary.
   The pump imports from the domain; no behavior change.
4. **The auto-confirm handler lives in `_plan_handler`** (not the engine): the engine's
   hook contract is unchanged; the CLI decides what its contexts provide. Tests drive
   the handler directly (unit) and the journey through `run_research` with the CLI's
   handler (integration, scripted plan→research→report).
5. **Existing headless journey tests are updated, not preserved**: fixture-lane headless
   creates now show a `plan_gate_degraded` event (the default script has no markers) and
   one extra scripted round — the smoke expectations move with the spec delta, in this
   change, with the receipts showing both reds (old expectations) and greens (new).

## Risks / Trade-offs

- [Headless cost: +1 model round per first-generation run] → stated in the spec as the
  price of the plan-first methodology; the alternative (no gate) is BUG-001.
- [Auto-confirm vs the plan-gate's human-review purpose] → the interactive path keeps
  the human gate; headless was never reviewable anyway (nobody at the terminal) — the
  choice is auto-confirm vs no gate, and no gate is the bug.
- [A legitimate report mentioning the markers] → a report that QUOTES the markers (e.g.,
  documentation about the gate) would be rejected; acceptable — the report is research
  output about the problem, and the marker literal is protocol vocabulary, not content.
  If a real case appears, the aspect wording can be refined in an owning change.
- [Smoke/fixture journey expectations shift] → updated in-change with red-green receipts.

## Migration Notes

Apply order: domain/plan.py + pump/validator imports → validator marker rule (red-first)
→ headless handler (red-first: handler is non-None and confirms verbatim) → journey
integration test → existing smoke/test expectations updated → receipts (`make verify`,
`make smoke`, doc-hygiene, closeout, validate) → archive → the real-lane acceptance run
(E-2's recording, BUG-001's criterion) → BUG-001 fixed ritual.
