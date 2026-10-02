# Proposal

## Why

The governance checkers all pass, but they live only as prose convention: the archive-time
gate run is a task-list instruction an agent executes on trust, `.github/workflows/` does
not exist, and `.git/hooks` holds no versioned hook. Nothing machine-forceful rejects a
change at the moment it is pushed. The DSH borrowing analysis (gap A) names this the
largest structural gap: enforced gates, not prose conventions, are what agents reliably
follow. Change ① just closed the loop on spec ownership; this is the hardening batch's
first change, arriving at the recorded position "immediately after change ①".

## What Changes

- Add a single-job CI workflow `.github/workflows/governance.yml`, triggered by push and
  pull request with path filters, that checks out with submodules, sets up Python 3.12 and
  the OpenSpec CLI (1.13.1), and runs the canonical sequence: governance unittest suite,
  aggregate closeout gate, document hygiene, and the harness `make verify`. A non-zero
  exit anywhere fails the job.
- Add a versioned pre-commit hook `.githooks/pre-commit` (staged whitespace check plus
  document hygiene), activated once per clone via `git config core.hooksPath .githooks`;
  tests, snapshots, type analysis, and builds are explicitly forbidden in the hook.
- Add an eighth governance component checker `openspec/governance/check_ci_governance.py`
  (`@impl CIG-001`) that machine-validates the CI workflow's triggers and canonical
  commands and the hook wiring, so the enforcement surface itself cannot drift silently.
- Add negative-control tests `openspec/tests/governance/test_ci_governance.py` proving the
  new checker fails on a missing or gutted workflow.
- Wire the new checker into `check_project_gate.py`, update the structural manifest
  (`project-structure.toml` requirement IDs + `required-paths.toml` inventory), re-render
  the generated guide locator, update the governance README, and register `CIG-001` in the
  requirement registry during apply.

## Capabilities

### New Capabilities

- `ci-governance`: owns required behavior of the acceptance path — CI runs the governance
  suite on every push and pull request, the local hook runs only cheap high-confidence
  checks, and the CI/hook declarations are themselves machine-validated against drift.

### Modified Capabilities

(none — `project-structure`'s requirements are unchanged; this change only appends
inventory entries under a new owning ID following the architecture-policy update protocol)

## Impact

- New files: `.github/workflows/governance.yml`, `.githooks/pre-commit`,
  `openspec/governance/check_ci_governance.py`,
  `openspec/tests/governance/test_ci_governance.py`.
- Modified: `openspec/governance/check_project_gate.py` (eighth component),
  `openspec/governance/required-paths.toml` (`[paths.CIG-001]`),
  `openspec/governance/project-structure.toml` (requirement IDs),
  `deep_research_harness/AGENTS.md` (generated locator re-render),
  `openspec/governance/README.md` (component list, checker command, hook activation),
  `openspec/governance/req-registry.yaml` (CIG-001 registration in apply).
- v2 lessons adopted verbatim: single job (no matrix), `submodules: true` checkout (v2 CI
  died at install until audited), path-filtered triggers, pinned tool versions.
- No harness application code changes; `make verify` remains a loud stub until its owning
  change replaces it — CI runs it as-is and it honestly verifies nothing today.

Boundary statement: ordinary downstream work neither modifies nor source-browses the
`deerflow/` gitlink. The CI workflow reads the pinned gitlink via a standard checkout with
submodules; no gitlink contract question is opened and no upstream runtime compatibility
is claimed or tested.

## Change Focus

- **Primary module / causal owner:** `openspec/governance` — the new checker, the gate wiring, and the manifest entries own the semantic decision of what the acceptance path enforces; the workflow and hook are its execution surface.
- **Seam classification:** deterministic-guardrail — the changed observable behavior is machine validation (CI job exit codes, checker exit codes); no model cognition is involved.
- **Question:** How does the governance suite become machine-forced on the push/pull-request acceptance path, and how are the CI and hook declarations themselves guarded against silent drift?
- **Necessary adjacent/external contracts:** `openspec/governance/check_project_gate.py` (answers: how an eighth component joins the aggregate without owning rule semantics); `openspec/governance/required-paths.toml` + `project-structure.toml` (answers: which new paths are declared and under which owning ID, per the architecture-policy synchronized-change protocol); `openspec/governance/architecture-policy.md` (answers: the five-step update protocol for structural changes, including guide re-render); v2 workflow `agent-tests.yml` (answers: audited lessons — single job, submodules, path filters — used as evidence, not as contract).
- **Evidence seam:** the new checker's direct exit codes with negative controls (missing workflow → red, gutted commands → red), the governance unittest suite staying green, and a local rehearsal of the exact CI command sequence with every exit code measured directly. No credentialed or live-external evidence is required; GitHub Actions execution itself is UNVERIFIED locally and labeled as such.
- **Not in scope:** harness application code, lint/type coverage expansion, multi-job or matrix CI, cache tuning, the B/F and C hardening items, hook framework dependencies (pre-commit/lefthook), and any change to checker rule semantics of existing components.
- **Triggered review policies:** none: CI only reads the pinned gitlink via checkout; no DeerFlow public-interface, gitlink-contract, or upstream-compatibility question is opened.
