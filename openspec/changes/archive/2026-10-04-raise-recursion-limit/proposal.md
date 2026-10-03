# Proposal

## Why

The five-run evidence arc on the EASA bundle closed the question: the deep-research skill's gather-then-write behavior needs ~1000 graph steps to complete a real briefing (100: raw crash; 300: 86 msgs; 800: 209 msgs; 1000: completed, generation 5). The binding's conservative 300 now has completing evidence to replace.

## What Changes

`DEEP_RESEARCH_RECURSION_LIMIT` 300 → 1000 (the framework's own max); the factory test's expectation updates red-green; the known-limitations row closes as resolved (evidence: the completing run).

## Capabilities

### New Capabilities
(none — constant change with completing evidence; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- Modified: `runtime/client.py` (constant), `tests/unit/test_wiring_mirror.py` (expectation), `docs/known-limitations.md` (row closes). No other changes.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/client.py` — the limit constant at the single stream seam.
- **Seam classification:** wiring — a constant raised on completing evidence; no policy change.
- **Question:** What limit does the binding inject now that 1000 is proven sufficient by a completed generation-5 run carrying the full evidence arc?
- **Necessary adjacent/external contracts:** the EASA bundle's five-run arc (answers: the slope 23→86→209→completed); the framework max (answers: the ceiling).
- **Evidence seam:** the factory test red-green (300→1000) plus the already-recorded completing run.
- **Not in scope:** adaptive limits, per-question budgets, spec text changes.
- **Triggered review policies:** change-admission
