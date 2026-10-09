# Proposal: Fix Headless Plan Gate

## Why

BUG-001 (P1, root cause confirmed): in a headless context `_plan_handler()` returns None —
"a non-interactive context gets no handler and the engine never enters a plan phase" — so a
headless `create` with a research problem never appends the plan-request suffix and never
gates: the model (following the deep-research skill's plan-first methodology) outputs its
plan as plain text with `<research-plan>` markers, and the run falls straight through to
`completed`, admitting the 4KB plan as the final report — zero searches, zero delegation,
zero sources. Four consecutive real-ladder runs (2026-10-10) degenerated this way while
historical full-research runs worked because they were TTY runs (gate present, human
confirmed). The `behavior-profile` machine named it on real data the day it landed:
`degenerate research — 0 search-or-fetch call(s) recorded`. Two holes, one fix: the plan
gate is absent headless, and admission has no refusal face for plan-as-report.

## What Changes

- **Headless plan gate = auto-confirm** (`cli.py` `_plan_handler`): a non-interactive
  context now gets an auto-confirming handler (returns the plan verbatim — the same
  bounded-automatic-continuation philosophy as the clarification auto-reply). The headless
  journey becomes: suffix appended → plan proposed (journaled) → auto-confirmed (journaled
  `plan_confirmed`) → plan injected → research turns → completed with a real report. The
  gate lifecycle is journal-visible end to end.
- **Admission refusal face for plan-as-report** (`engine/validator.py`): the final-report
  structure rule gains a first-aspect check — content carrying `<research-plan>` markers is
  rejected as `report_structure_violation` naming the face ("a proposed plan is not a
  report"). Any other path that lands a plan as a report now fails loudly instead of
  admitting silently.
- **Marker constants move to `domain/plan.py`** (single owner): pump and validator import
  from the domain; pump's `_extract_plan` moves beside them.
- **Tests**: headless handler auto-confirm (unit); marker rejection red-green (validator
  suite); a headless plan-journey integration test (scripted plan-with-markers → research
  tool turns → report: gate fires, journal shows `plan_proposed`/`plan_confirmed`, searches
  materialize, completion carries the report not the plan).
- **Docs**: the playbook's plan-gate pitfall note gains the headless semantics; BUG-001's
  card links the fix (and records the corrected diagnosis — the original "smuggling"
  symptom was a misread of `answer_excerpt`, corrected on the card per the honest-record
  discipline).

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `entry-surface`: the non-interactive clause inverts for the plan gate — a headless
  first-generation `create` now carries an **auto-confirming plan hook** (the plan phase
  runs; the plan is confirmed verbatim and injected; the plan-phase model round is the
  deliberate price of the plan-first methodology). The clarification half is unchanged
  (headless = bounded automatic continuation, never stdin). The spec's prior "no plan
  hook (no plan phase, no extra model round)" is the fossil of a pre-skill-narrowing
  assumption — with the deep-research skill loaded, the model always plans first, so "no
  plan phase" meant the plan fell through to completion (BUG-001's root cause, spec'd
  behavior IS the bug).
- `run-admission`: the final-report structure contract gains the plan-marker refusal
  aspect (rejected as `report_structure_violation`; the closed code set is unchanged).

## Impact

- Modified: `runtime/interaction/cli.py` (headless plan handler), `engine/validator.py`
  (structure rule first aspect), `runtime/pump.py` (imports markers from domain;
  `_extract_plan` relocated), new `domain/plan.py`, playbook note, BUG-001 card link.
- Tests: `tests/unit/interaction/` or cli-handler test (auto-confirm), validator structure
  tests (marker red-green), `tests/integration/test_plan_journey.py` (headless journey).
- Not touched: `deerflow/` gitlink (read-only); the interactive plan handler (TTY path
  unchanged); the clarification auto-reply machinery; journal event vocabulary (reuses
  existing plan lifecycle events); verdict closed set (reuses `report_structure_violation`).

## Change Focus

- **Primary module / causal owner:** `runtime/interaction/cli.py`'s `_plan_handler` — the
  None-return is the root cause; the validator face and the domain relocation follow from
  it.
- **Seam classification:** deterministic-guardrail + wiring — the gate semantics and the
  admission rule are pure code paths over textual facts; red-first testable; no model,
  prompt, or state machine beyond the plan-gate flow's own rules.
- **Question:** Can the headless research journey be restored (plan → auto-confirm →
  research → report) and the plan-as-report admission hole closed permanently, so that
  `behavior-profile`'s degenerate-research verdict no longer fires on headless real runs?
- **Necessary adjacent/external contracts:** BUG-001 card (answers: the corrected
  diagnosis, the four degenerate bundles, the acceptance criterion); `deerflow-wiring`
  plan-phase requirement (answers: the gate flow this change extends to headless);
  `run-admission` structure contract (answers: the final-report dimension the marker rule
  joins); `test-evidence` capability (answers: the behavior-profile machine whose
  `min_search_calls` verdict is the acceptance signal); CLS-016/018 archived changes
  (answers: the plan-gate design this change completes for headless).
- **Evidence seam:** red-first tests — marker-wrapped report → `report_structure_violation`
  naming the face; headless handler returns the plan verbatim; scripted headless journey
  journals `plan_proposed` + `plan_confirmed` and completes with the report; `make verify`
  + `make smoke` + closeout gate exit 0; the real-ladder acceptance run (BUG-001's
  criterion: `min_search_calls` not hit, full journey journaled) runs after archive as
  E-2's recording.
- **Not in scope:** prompt/wording changes (H1 was disproved — the suffix was never
  appended headless; the wording itself stands); the interactive gate (unchanged); journal
  vocabulary; E-2/E-3 (this change unblocks them; their own slices follow).
- **Triggered review policies:** change-admission, local-context
