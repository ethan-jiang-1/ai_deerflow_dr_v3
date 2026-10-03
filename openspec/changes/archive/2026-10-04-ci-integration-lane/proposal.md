# Proposal

## Why

The integration lane (wiring smoke + CLI journey, zero-credential) runs only locally — CI installs nothing beyond the stdlib gate, so the framework-dependent proof surface never runs on push. The committed uv.lock makes the environment reproducible; the lane can ride CI.

## What Changes

- The workflow gains a pinned setup-uv step and a `make smoke` step after the unit gate; the Makefile smoke target materializes its environment (`uv sync` then `uv run --no-sync`) so local warm-cache and cold CI share one target.
- `check_ci_governance.py` required markers gain the new steps, and the governance test fixture follows — the trio (workflow, checker, fixture) moves together or the suite fails.

## Capabilities

### New Capabilities
(none — CI plumbing; `skip_specs: true`)
### Modified Capabilities
(none — the ci-governance spec's mechanism requirements (single job, declaration-checked) are unchanged; only the declared step list grows.)

## Impact

- Modified: `.github/workflows/governance.yml`, `openspec/governance/check_ci_governance.py`,
  `openspec/tests/governance/test_ci_governance.py`, `deep_research_harness/Makefile`.
  No product code; no credentials in CI (fixture lane only).

## Change Focus

- **Primary module / causal owner:** `.github/workflows/governance.yml` — the CI job owns which lanes run on every push.
- **Seam classification:** wiring — CI plumbing; no product behavior change.
- **Question:** How does the integration lane run in CI — uv environment from the committed lock, submodule present — with the declaration trio in sync?
- **Necessary adjacent/external contracts:** `check_ci_governance.py` + its gov test fixture (answers: the trio that must move together); the Makefile smoke target (answers: environment materialization); the committed uv.lock (answers: reproducibility).
- **Evidence seam:** the governance unittest suite green against the edited trio plus local `make smoke` green; the pushed CI run itself is UNVERIFIED-until-push (no local CI — stated honestly).
- **Not in scope:** real-ladder runs in CI (credentials never enter CI), extra artifact caching, workflow dispatch triggers.
- **Triggered review policies:** change-admission
