# Proposal: Exempt Verification Receipts From the Dependency Guard

## Why

The closeout gate is red on exactly one component: `check_harness_dependency_direction.py`
flags `deep_research_harness/docs/skills/deep-research/verification-receipt.json` because
the receipt's recorded governance command argv contains the literal token `openspec/`.
The red is a false positive with two verified root causes: the checker's literal token
scan cannot distinguish an application *dependency* from a governance command *record*,
and the receipt that trips it is invisible to git because the unanchored `.gitignore`
rule `skills/` (written for a v2-era runtime-materialized profile root whose
`configure.py` no longer exists) swallows `deep_research_harness/docs/skills/` whole —
its sibling SOP files are tracked while the evidence file silently is not. The result
is machine-dependent governance (a fresh clone is green; this workspace is red), which
blocks every subsequent change's closeout and violates the repo's own rule that
conclusions must not depend on one machine's workspace.

## What Changes

- **Receipts become a structurally recognized exemption** in the dependency-direction
  checker: a file is exempt only when it is named `verification-receipt.json` AND
  parses as a JSON object carrying a top-level non-empty `checks` list of
  command-record objects (the invariant core of every receipt written in this repo).
  Recognition is structural, not nominal — a file that merely has the name but not
  the shape stays scanned.
- **The guard's semantics get a spec home**: a new `dependency-direction` capability
  replaces the docstring-only authority (following the CIG/DOB/RLF/PRS `@impl`
  pattern).
- **Negative controls land in the governance unittest suite**
  (`test_harness_dependency_direction.py`, red-first): a valid receipt recording
  governance commands is not a violation; a source file with a forbidden token is; a
  receipt-named file without receipt shape is.
- **The gitignore rule is anchored** (`skills/` → `/skills/`): it keeps ignoring the
  repo-root runtime-materialized profile root it was written for and stops swallowing
  `deep_research_harness/docs/skills/`.
- **The existing receipt is tracked and registered**:
  `deep_research_harness/docs/skills/deep-research/verification-receipt.json` becomes a
  tracked evidence file registered in `required-paths.toml`, so its deletion fails
  architecture governance (like its sibling `provenance.json`).
- **Governance README and manifest comment updated**: the checker's row records the
  exemption and its `@impl DEP-001` marker; the marker is registered in the
  `project-structure.toml` comment block.
- No runtime code changes; no changes to other checkers, the gate inventory, or CI
  workflow semantics.

## Capabilities

### New Capabilities

- `dependency-direction`: owns the required behavior of the harness→governance
  dependency guard — scan semantics, the structural receipt exemption, and the
  negative-control obligation.

### Modified Capabilities

<!-- none -->

## Impact

- Modified: `openspec/governance/check_harness_dependency_direction.py` (exemption +
  `@impl DEP-001` docstring), `.gitignore` (anchor one rule),
  `openspec/governance/required-paths.toml` (register the receipt and the new test
  file), `openspec/governance/project-structure.toml` (comment registry),
  `openspec/governance/README.md` (checker row).
- New: `openspec/tests/governance/test_harness_dependency_direction.py`, the
  capability spec `openspec/specs/dependency-direction/spec.md` (via this change's
  delta), git-tracked
  `deep_research_harness/docs/skills/deep-research/verification-receipt.json`.
- Not touched: the other five component checkers, the `check_project_gate.py`
  inventory, the CI workflow, harness runtime/CLI, harness doc/runtime reorganization
  (later phases of the 2026-10-05 architecture plan), the receipt format itself.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change reads nothing inside it.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_harness_dependency_direction.py`
  — the false positive and its exemption are this checker's scan semantics; the
  gitignore anchor and receipt tracking are conformance repairs of a surface it
  guards.
- **Seam classification:** deterministic-guardrail — scan-boundary semantics of a
  stdlib governance checker; no model, prompt, or state machine.
- **Question:** Can the receipt false positive be closed by a structural exemption
  whose red is demonstrated before green — a real governance reference in a source or
  config file still trips, a nominal receipt rename without receipt shape still trips
  — while the swallowed evidence file becomes tracked, registered, and the closeout
  gate machine-independently green?
- **Necessary adjacent/external contracts:** `project-structure` capability
  (answers: the manifest/inventory update protocol for registering the receipt and the
  new test file); the closeout gate inventory in `check_project_gate.py` (answers:
  this checker stays a registered component — no inventory change); the repo's
  runner-receipt convention (answers: the JSON shape structural recognition must
  match — a top-level `checks` list of command records, with `revision` and
  `completed_at`, as observed across existing receipts).
- **Evidence seam:** the new governance unittest `test_harness_dependency_direction.py`
  (purpose-built fixture trees, subprocess exit codes read directly, red-first), the
  checker's exit 0 on the real tree, the full closeout gate, `make verify`, and
  `git check-ignore` proving the anchored rule no longer matches `docs/skills/`.
- **Not in scope:** any other exemption class (prose, docs, or config files — a real
  dependency in any of them still trips); harness doc/runtime reorganization (plan
  phases 1–4); receipt format redesign; CI workflow or gate inventory changes; skill
  selection or any product behavior.
- **Triggered review policies:** control-placement, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| Which files the dependency guard scans (receipts exempt) | Human judgment (operator chose design A: structural exemption + gitignore narrowing, over receipt relocation or receipt-format change) | Structural recognition inside the checker: exact filename + JSON object + top-level non-empty `checks` command-record list | non-bypassable | A forbidden token in any non-receipt file still trips loudly; a receipt-named file without receipt shape still trips; recovery is removing the reference or restoring true receipt shape | The per-machine receipt-deletion workaround is retired; evidence stops being conflated with coupling | Red-first unittest: receipt fixture → exit 0, source-reference fixture → non-zero, fake-receipt fixture → non-zero |
| `.gitignore` `skills/` rule scope | Human judgment (same ruling) | Anchored pattern `/skills/` in `.gitignore` | non-bypassable | Deleting the tracked receipt then fails architecture governance via `required-paths.toml`; recovery is `git restore`, and an unregistered deletion fails loudly naming the path | The v2-era over-broad rule stops silently swallowing `docs/skills/` evidence | `git check-ignore` exit codes on both paths; architecture checker exit 0 with the registered path present |
| The skills-snapshot receipt becomes tracked evidence | Human judgment (tracking chosen over leaving it untracked-visible) | `required-paths.toml` registration entry | bounded-repair | Deletion fails loudly; the receipt is historical evidence with its own `scope`/`unverified` fields, not a claim about current behavior | Machine-dependent checker behavior retired — every clone sees the same evidence file and the same green | Architecture checker exit 0; dependency checker green on a tree containing the tracked receipt |
