# Proposal

## Why

The doctrine doc landed with the strategy and ladder; the digest's three philosophy items and the crash idiom are the remaining Tier B hooks — they make the discipline survive personnel and time (the user's requirement: guidance docs + hooked practices, not verbal repetition).

## What Changes

- Doctrine doc gains: "evidence over a green check" (CI is a signal, not a verdict), the no-coverage-gate trade-off rationale (structural gates over gaming proxy metrics), the static-discovery to runtime-proof workflow naming, and the as-if-restarted crash idiom (rebuild-from-store, no process kill).
- `pyproject.toml` dev group gains why-comments (pytest: the integration lane's runner; ruff: lint — the zero-product-deps stance documented).
- Capabilities: none (`skip_specs: true` — guidance).

## Capabilities

### New Capabilities
(none)
### Modified Capabilities
(none)

## Impact

- Modified: `docs/testing-and-evaluation.md`, `pyproject.toml`. No product code.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/docs/testing-and-evaluation.md` — the doctrine doc is where the hooks land (philosophy paragraphs + the as-if-restarted idiom).
- **Seam classification:** deterministic-guardrail — guidance whose rules are backed by existing gates (A4's command-surface guard landed this round).
- **Question:** How do the three digest philosophy items (evidence over a green check; the no-coverage-gate trade-off; static-discovery-to-runtime-proof workflow) and the as-if-restarted crash idiom land as durable doctrine — with the dev-dependency governance comments (B4) in pyproject?
- **Necessary adjacent/external contracts:** `deep_research_harness/pyproject.toml` (answers: B4's why-comments on dev deps); the quality register (answers: where the machines stay registered).
- **Evidence seam:** doc hygiene + closeout gates green; the doctrine text citing its backing gates.
- **Not in scope:** A2 (content-addressed replay — own change), A5' (skill-review surface — own change), coverage tooling.
- **Triggered review policies:** change-admission
