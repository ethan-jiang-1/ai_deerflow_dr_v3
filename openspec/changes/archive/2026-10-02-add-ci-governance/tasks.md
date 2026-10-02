# Tasks

## 1. Enforcement surface (workflow and hook)

- [x] 1.1 Create `.github/workflows/governance.yml`: single job; `on:` push and pull_request
      with path filters over `openspec/**` (governance, tests, specs, changes, and config
      all gate), `deep_research_harness/**`, `.github/workflows/governance.yml`, and
      `.githooks/**`; checkout with `submodules: true`; setup Python 3.12; install the
      pinned OpenSpec CLI (`@fission-ai/openspec@1.13.1` via npm); run the canonical
      sequence — `python3 -m unittest discover -s openspec/tests/governance -q`,
      `python3 openspec/governance/check_project_gate.py --phase closeout`,
      `python3 openspec/governance/check_doc_hygiene.py`, and harness
      `UV_OFFLINE=1 make verify` from `deep_research_harness/`. Red is the current state:
      the workflow does not exist, so nothing machine-forces the suite on push. Verify:
      the file exists and contains every declared marker (triggers, path filters,
      `submodules: true`, each canonical command verbatim).
- [x] 1.2 Create executable `.githooks/pre-commit` containing exactly two checks —
      `git diff --cached --check` and
      `python3 openspec/governance/check_doc_hygiene.py` — and nothing else; document the
      one-time activation `git config core.hooksPath .githooks` in the governance README
      (task 3.5). Verify: `bash -n .githooks/pre-commit` exits 0; running the hook on a
      clean tree exits 0; the script contains the two commands and no others.

## 2. Drift-guard checker and negative controls (red-before-green)

- [x] 2.1 Create `openspec/governance/check_ci_governance.py` with `@impl CIG-001` in its
      module docstring: it validates textually that the workflow file declares the push
      and pull-request triggers, the path filters, `submodules: true`, the pinned Python
      setup and pinned OpenSpec CLI install markers, and each canonical command verbatim;
      and that the hook script contains exactly the two declared checks with no forbidden
      (test/snapshot/type-analysis/build) invocation. Red receipt: before task 1.1 lands,
      the checker against a tree without the workflow exits 1. Verify green: against the
      real files the checker exits 0.
- [x] 2.2 Create `openspec/tests/governance/test_ci_governance.py` with negative controls:
      a missing workflow fails; a workflow missing one canonical command fails; a hook
      with a forbidden command fails; a hook with an undeclared extra command fails; valid
      fixtures pass. Verify: `python3 -m unittest openspec.tests.governance.test_ci_governance`
      exits 0 — the guard is proven able to fail.
- [x] 2.3 Update `openspec/tests/governance/test_ci_governance_steps.py` from its v2
      stance to the v3 stance, recording both deliberate divergences in place: the
      workflow is `governance.yml` (not `agent-tests.yml`), path filters select all of
      `openspec/**` (the v3 governance suite is seconds-fast stdlib, and spec/delta edits
      do affect the requirement/spec checkers on active changes — the v2 cost argument
      does not exist in v3), and the governance ruff lint is deferred to its own
      follow-up change (the first v3 CI stays zero-dependency). The discover-command pin
      and the no-`-t .` rule carry over unchanged. Verify: the suite runs green with the
      pins active against the landed workflow.

## 3. Governance wiring (registry, manifest, guide, gate, docs — in dependency order)

- [x] 3.1 Register `CIG-001: ci-governance — <description>` in
      `openspec/governance/req-registry.yaml` (apply writes the registry; planning only
      reserved). This must precede the manifest update in 3.2: the architecture checker
      rejects manifest requirement IDs missing from the registry (`owner.unknown`).
      Verify: `python3 openspec/governance/check_project_reqs.py` exits 0 and
      `check_project_req_coverage.py` recognizes the `@impl CIG-001` annotation (exit 0).
- [x] 3.2 Update the structural manifest per the architecture-policy protocol: add
      `CIG-001` to `project-structure.toml` `requirement_ids` and its stale header
      comment; add `[paths.CIG-001]` in `required-paths.toml` declaring the four new
      files (workflow, hook, checker, test). Verify:
      `python3 openspec/governance/check_project_architecture.py` exits 0.
- [x] 3.3 Re-render the generated structure locator in `deep_research_harness/AGENTS.md`
      via `python3 openspec/governance/check_project_architecture.py --render-guide`
      (update the owning change and registry, never hand-edit the generated block); the
      locator deliberately does not repeat the path inventory, so the render may be
      unchanged — verify by comparison. Verify: the architecture checker's guide-drift
      validation passes (exit 0).
- [x] 3.4 Wire `check_ci_governance.py` as the eighth component in
      `openspec/governance/check_project_gate.py` (orchestration only; no rule semantics
      live in the gate) and update its component-count wording. Verify:
      `python3 openspec/governance/check_project_gate.py --phase closeout` exits 0 listing
      eight green components — the first full-suite run after all wiring is in place.
- [x] 3.5 Update `openspec/governance/README.md`: eighth component checker row and
      command, the canonical CI sequence, and the hook activation one-liner. Verify:
      `python3 openspec/governance/check_doc_hygiene.py` exits 0.
- [x] 3.6 Create the main spec `openspec/specs/ci-governance/spec.md` during apply (not by
      archive): native archive copies Purpose and Requirements but drops the `> req:` header
      line, leaving the post-archive requirement checkers red — the lesson recorded in
      change establish-project-structure's design decision 6, re-applied here. Verify:
      `python3 openspec/governance/check_project_reqs.py` exits 0 with CIG-001 alive in the
      main spec.

## 4. Local rehearsal and full verification (every exit code measured directly)

- [x] 4.1 Rehearse the exact CI command sequence locally from the repository root —
      governance unittest suite, aggregate closeout gate, document hygiene, then
      `UV_OFFLINE=1 make verify` from `deep_research_harness/` — recording each exit code
      directly (never through a pipe). Actual GitHub Actions execution is UNVERIFIED on
      this machine and is stated as such in the closeout report; the first real push is
      the live control.
- [x] 4.2 Full verification: `python3 openspec/governance/check_project_gate.py --phase closeout`
      exit 0 (eight components), `openspec validate add-ci-governance --strict` exit 0,
      `git diff HEAD --check` exit 0.
- [x] 4.3 Record scope/diff evidence: `git status --porcelain=v1 --untracked-files=all`,
      `git ls-files --stage deerflow`, `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`,
      `git diff --submodule=short`; confirm the gitlink pointer still matches the declared
      `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7` with no pointer bump proposed.

## 5. Closeout and archive

- [x] 5.1 Closeout review: compare the Change Focus against actual tasks, delivered diff,
      and evidence; state the UNVERIFIED boundary (live CI execution) plainly; every
      actionable finding becomes an unchecked task or an explicitly approved re-scope.
- [x] 5.2 After explicit user approval, archive via `openspec archive add-ci-governance`;
      re-run the aggregate gate (exit 0) and mark gap A absorbed in
      `_backlog/plans/2026-10-02-borrow-dsh-harness-gap-analysis.md` (its landing table's
      A row), leaving B/F as the next queue item.
