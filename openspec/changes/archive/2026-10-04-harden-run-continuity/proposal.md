# Proposal

## Why

The first full deep-research run (bundle 997fe460) proved the pipeline but crashed raw: LangGraph's recursion limit (100) was exhausted mid-research and the exception propagated through the engine — a stack trace instead of the loud human failure the terminal-honesty requirements declare, with the run left active until a later status transferred it. The checkpoint kept all 13 tool results. Findings and fixes are specified in `_backlog/plans/2026-10-03-deep-run-postmortem.md`.

## What Changes

- **Exception guard** in `run_research`: a framework/stream exception during the run transfers the bundle to `failed-resume`, journals a `terminal` entry (`reason: framework_error`, the exception class), and returns — the CLI prints the human terminal line instead of a traceback.
- **Recursion limit**: `config/base.yaml` and `config/fixture.yaml` set `recursion_limit: 300` (the framework default 100 caps deep research at ~10 tool rounds; its own max is 1000).
- **CLI terminal line** names a reason pointer for failed runs ("see journal timeline").

## Capabilities

### New Capabilities

(none — conformance fix against declared RUB-001/DEW-001 fail-loud requirements; `skip_specs: true`)

### Modified Capabilities

(none)

## Impact

- Modified: `runtime/run_engine.py` (guard), `config/base.yaml` + `config/fixture.yaml`
  (recursion_limit), `cli.py` (terminal-line reason), `tests/unit/test_run_engine.py`
  (guard case, red-green). No governance/CI/deerflow changes.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/run_engine.py`
- **Seam classification:** wiring — exception-to-terminal adaptation at the framework boundary; no policy change.
- **Question:** How does a framework/stream exception during a run land as a loud failed-resume with the research material preserved and a human-readable message, and how does the recursion limit stop capping deep research at 100 steps?
- **Necessary adjacent/external contracts:** the crashed EASA run (answers: the real failure shapes this change guards — GraphRecursionError propagating raw); the configs (answers: where recursion_limit is raised to 300); RUB-001 terminal rules (answers: which transition the guard reuses).
- **Evidence seam:** unit test (stream raising RuntimeError → failed-resume + terminal journal entry) red-before-green; the crashed bundle's refine re-run as the live verification.
- **Not in scope:** retry of failed runs, subagent-stream handling, CI changes, spec text changes.
- **Triggered review policies:** change-admission
