# Proposal

## Why

The new smoke lane extended CI runtime, but the workflow has no concurrency cancellation and no timeout budget — an outdated push keeps burning a superseded run, and a hung test has no ceiling. The digest names both as declared contracts ("same-PR new push cancels the old run"; "timeout is red, no gray area for slow tests").

## What Changes

- `governance.yml`: add `concurrency: {group: governance-<branch>, cancel-in-progress: true}` and `timeout-minutes: 30` on the job; `check_ci_governance.py` markers + the gov test fixture move together.

## Capabilities

### New Capabilities
(none — CI plumbing; `skip_specs: true`)
### Modified Capabilities
(none — the single-job and declaration-mechanism requirements are unchanged)

## Impact

- Modified: `.github/workflows/governance.yml`, `openspec/governance/check_ci_governance.py`, `openspec/tests/governance/test_ci_governance.py`. No product code, no deerflow changes.

## Change Focus

- **Primary module / causal owner:** `.github/workflows/governance.yml` — the CI job now owns an execution budget (concurrency cancel + per-job timeout) alongside its lanes.
- **Seam classification:** deterministic-guardrail — machine-enforced execution budget; no product behavior.
- **Question:** How does the CI job gain an execution budget (same-PR cancel, timeout) without violating the single-job declaration — with the declaration trio synced?
- **Necessary adjacent/external contracts:** `check_ci_governance.py` + the gov test fixture (answers: the trio that must move together); the digest citation (answers: why the budget is a declared contract, not a convenience).
- **Evidence seam:** the governance unittest suite against the edited trio + closeout 0.
- **Not in scope:** sharding, matrix, other workflows.
- **Triggered review policies:** change-admission
