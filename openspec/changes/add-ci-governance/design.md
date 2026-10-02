# Design

## Context

Verified current state: six governance component checkers and the aggregate gate pass
(exit 0, receipts from change ① closeout), but only on a machine where someone chooses to
run them — `openspec/config.yaml`'s tasks rule describes the archive-time gate as a prose
convention, `.github/workflows/` does not exist, and no versioned hook exists. The remote
is GitHub (`origin` → github.com), so GitHub Actions is the enforcement surface. v2's
audited workflow lessons are available as evidence: single-job discipline, `submodules:
true` checkout (v2 CI died at the install step until a 2026-09 audit found the default
checkout does not pull the gitlink), path-filtered triggers, and CI-carried checks that
`make verify` can never reach. The architecture-policy synchronized-change protocol
(five steps: delta, manifest, guide re-render, evidence mapping, checker pass) governs
this change because it adds structural paths. See proposal.md for motivation; the delta
spec carries the normative text.

## Goals / Non-Goals

**Goals:**

- A push/pull-request CI job that runs the canonical governance sequence and fails on any
  non-zero exit — the acceptance path becomes machine-forced.
- A versioned, dependency-free pre-commit hook restricted to two cheap high-confidence
  checks, with the prohibition against suites in the hook spelled out.
- The CI and hook declarations themselves machine-guarded (inventory pinning + an eighth
  component checker with negative controls), so the enforcement surface cannot drift
  silently.
- Every locally verifiable claim rehearsed with direct exit-code receipts; the one thing
  not verifiable on this machine — actual GitHub Actions execution — labeled UNVERIFIED.

**Non-Goals:**

- No harness application code, no lint/type coverage expansion, no multi-job or matrix
  CI, no cache tuning, no hook framework dependencies, no changes to existing checkers'
  rule semantics, and none of the B/F/C hardening items.

## Decisions

1. **Single job, no matrix.** The exhaustive governance set runs in one deterministic job.
   v2 pinned the same shape by contract test after its matrix experiments; a single-job
   gate is easier to keep green and to reason about. Alternative (split lint/test/verify
   jobs) rejected: more moving parts for zero coverage gain on a stdlib suite.
2. **`submodules: true` checkout.** The architecture checker's full mode validates the
   nested gitlink `HEAD` and porcelain state, which requires the submodule checked out;
   v2's CI died at install until this was audited. Alternative (metadata-only CI) rejected:
   it would silently weaken which governance checks run in CI versus locally.
3. **Pinned toolchain on CI.** Python via setup-python (3.12) and the OpenSpec CLI via npm
   (`@fission-ai/openspec@1.13.1`, matching the generation-alignment rule that pins CLI
   version to skill frontmatter). Unpinned floating versions were rejected: gate behavior
   must not vary with upstream releases.
4. **Versioned hooks via `core.hooksPath`, no hook framework.** A `.githooks/pre-commit`
   script activated by one `git config core.hooksPath .githooks` per clone. Alternative
   (pre-commit/lefthook framework) rejected: adds an install dependency for two stdlib
   checks, against the governance tree's zero-dependency rule.
5. **Hook is not a small CI.** Exactly two checks — staged whitespace (`git diff --cached
   --check`) and the standalone doc-hygiene checker. Tests, snapshots, type analysis, and
   builds are forbidden in the hook (this is the DSH borrowing lesson, made normative in
   the delta). Anything whose cost varies with the changed surface belongs to CI.
6. **An eighth component checker as a drift guard.** `check_ci_governance.py` validates that
   the workflow declares the required triggers and invokes each canonical command, and
   that the hook contains only the two declared checks. This gives `CIG-001` a real
   deterministic owner (`@impl`) and guards the guard: deleting or gutting the enforcement
   surface turns governance red. Alternative (inventory pinning only) rejected: existence
   checks cannot detect a gutted workflow.
7. **Textual marker validation, not YAML parsing.** The governance tree is Python-stdlib
   only and stdlib has no YAML parser, so the checker validates required markers
   textually (trigger keys, `submodules: true`, each canonical command string). This
   catches deletion and gutting; it does not validate workflow semantics — honestly
   recorded as the checker's evidence boundary.
8. **Local rehearsal instead of pretended CI verification.** The apply tasks run the exact
   CI command sequence locally with direct exit codes, and label actual GitHub Actions
   execution UNVERIFIED (no runner exists on this machine). The workflow is kept to
   standard, widely-used actions to minimize that residual risk.
9. **Five-step architecture-policy protocol followed.** Manifest contract gains the owning
   ID (`CIG-001` in `project-structure.toml`), inventory gains the new paths under
   `[paths.CIG-001]`, the generated guide locator is re-rendered via
   `check_project_architecture.py --render-guide`, and the checker passes before archive.

## Risks / Trade-offs

- [GitHub Actions execution is unverifiable on this machine] → labeled UNVERIFIED in tasks
  and closeout; mitigated by local rehearsal of the identical command sequence and a
  minimal workflow of standard actions; the first real push is the live negative/positive
  control.
- [CI adds an npm dependency for the OpenSpec CLI] → CI-only, pinned to the
  generation-aligned version; no dev-machine or governance-runtime dependency.
- [Submodule checkout makes CI slower] → accepted deliberately; correctness of the
  gitlink-metadata checks outruns checkout time, per v2's audited lesson.
- [Path filters could over- or under-trigger] → filters cover all of `openspec/**`
  (governance, tests, specs, changes, and config all gate — a pure spec-delta change
  still triggers CI), plus the harness tree, the workflow file, and the hooks directory;
  the filter list is itself marker-validated by the new checker.
- [Registry rollback asymmetry] → `CIG-001` is registered in apply; if the change were
  abandoned after registration, the append-only registry keeps the ID with a retirement
  marker rather than reuse — same discipline as every allocated ID.

## Migration Plan

Single apply following the policy protocol: land workflow, hook, checker, tests, gate
wiring, manifest updates, guide re-render, and registry entry together; rehearse the CI
command sequence locally; run the full governance suite and aggregate gate with direct
exit codes. Rollback before archive is reverting the files (registry entry then gets a
retirement marker); after archive, a revert is an ordinary follow-up change.
