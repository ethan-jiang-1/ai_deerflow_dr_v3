# Proposal

## Why

A completed run's report currently lives only inside the checkpoint — the admission machinery (validator, hash-chain ledger, hold point) has never processed a real report, so the project's core claim ("models propose, code disposes") is unexercised on the artifact that matters most. RUB-001 already declares "Final reports SHALL be routed to final/"; nothing implements it.

## What Changes

- The run engine, on a clean completion (no fallback, non-empty final answer), submits the final answer (the terminal picture's last AI message text) through `submit_artifact` as `kind="final_report"`, filename `report-gen<N>.md`, provenance producer run-engine. Fallback/failed/empty completions never submit.
- Admission placement honors the declared routing: admitted `final_report` content lands at `final/<filename>` (other kinds keep `evidence/<kind>/`).
- Specs: deerflow-wiring MODIFIED (the engine submits the final answer through the hold point at completion); run-admission MODIFIED (the admit-placement sentence routes final_report to final/).

## Capabilities

### New Capabilities
(none)
### Modified Capabilities
- `deerflow-wiring`: the terminal-honesty requirement gains the completion-submission clause and scenario.
- `run-admission`: the admit-placement requirement routes final_report to final/ (all scenarios preserved).

## Impact

- Modified: `runtime/run_engine.py` (completion submission), `runtime/admission.py` (placement branch), the two delta specs above, unit tests (`test_run_engine.py`, `test_admission_runtime.py`) red-green. No CI/governance/deerflow changes.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/run_engine.py` — the completion path owns the submission; admission owns the verdict and placement.
- **Seam classification:** deterministic-guardrail — the report passes the same hold point as every artifact; no model-decided admission.
- **Question:** How does a completed run's final answer land as an admitted final_report through the hold point, routed to final/, closing the QC loop on real runs?
- **Necessary adjacent/external contracts:** `runtime/admission.py` (answers: where the placement rule for final_report lives); the RUB-001 directory contract (answers: final/ is the declared home for final reports); the values snapshot (answers: the authoritative source of the final answer text).
- **Evidence seam:** unit red-green (engine completion submits; final_report places to final/; fallback/empty answers never submit) plus a real-ladder run landing the file and the ledger entry.
- **Not in scope:** admission of intermediate evidence artifacts (producers arrive later), report formatting beyond raw text, spec changes to RUB-001 (its routing declaration already stands).
- **Triggered review policies:** control-placement, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| The completed report is admitted through the same hold point as every artifact; the engine submits, admission disposes, final/ receives | Human judgment (the project's core: models propose, code disposes — extended to the terminal artifact) | The validator verdicts and the hash-chain ledger record the disposition; the engine cannot admit | non-bypassable | A report that skips the hold point cannot land (submit_artifact is the only path); a rejected report records reasons and places nothing | No second report writer; no CLI-side submission authority; the routing reuses RUB-001's declaration instead of inventing one | Unit red-green (submission + placement + fallback-never-submits) and the real-ladder run's final/ file + ledger entry |
