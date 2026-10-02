# Design

## Context

Verified current state (freshly measured, this session): the structural governance machinery
exists and runs — `project-structure.toml` (contract), `required-paths.toml` (inventory),
`check_project_architecture.py`, and the generated locator in the module guide — but
`PRS-001` is registered in `req-registry.yaml` with no owning main spec, and
`openspec/specs/` is empty. Three component checkers exit 1 with the same root cause:
`check_project_reqs` (registry ID missing from main spec and delta header),
`check_project_architecture` (no lifecycle-appropriate project-structure spec),
`check_project_req_coverage` (same missing-ID root). A dry run on a scratch copy has
already demonstrated the 7/7-green path: main spec with the `> req:` / `> structure:`
header lines plus requirement/scenario structure, and an `@impl` annotation in the owning
checker's docstring. See proposal.md for motivation; the delta spec carries the normative
text.

## Goals / Non-Goals

**Goals:**

- One owning main spec for `PRS-001` whose normative text describes exactly what the
  governance machinery enforces — no invented requirements, no unowned claims.
- Script-evidence anchor (`@impl PRS-001`) so requirement coverage passes with evidence
  living next to the enforcing checker.
- Closeout aggregate (`check_project_gate.py --phase closeout`) reaching exit 0 with all
  six component checkers green and the governance unittest suite unchanged-green.

**Non-Goals:**

- No checker rule-semantics changes (the annotation is docstring-only evidence).
- No registry rewrite; the append-only registry is verified, not edited.
- No harness application code, no CI workflow, no fixture composition, no upstream
  runtime compatibility evidence.

## Decisions

1. **Spec scope = what the checkers already enforce.** The delta carries three
   requirements: manifest authority (validation + generated-locator coupling), the
   metadata-only upstream gitlink anchor, and registry-ownership coupling. Alternatives:
   a broader structural-policy spec was rejected because it would create requirements no
   checker owns (unprovable claims); a single minimal requirement was rejected because it
   would leave real enforced semantics unowned and under-describe the guardrail.
2. **Evidence via `@impl PRS-001` docstring annotation in
   `check_project_architecture.py`.** Alternative: a separate evidence test file —
   rejected because the established convention (registry header, governance README) puts
   implementation evidence in the owning script's docstring, keeping evidence adjacent to
   the enforcing code with zero new moving parts.
3. **Registry verify-not-rewrite.** `PRS-001` is already registered; the apply task
   verifies the description still matches the established spec. Deleting and re-adding was
   rejected: the registry is append-only by its own header rules.
4. **Red-green without new tests.** The deterministic tests for this capability already
   exist — the six component checkers and the governance unittest suite (which includes
   negative-control cases). Red is the live measured gate state (three named red
   components, receipts recorded this session); green is the same commands after the spec
   and annotation land. Writing an additional negative-control test was rejected as
   duplication; instead the tasks require the suite to stay green (guards stay able to
   fail, proven by their existing self-tests).
5. **Gitlink spelled metadata-only.** Per the triggered `deerflow-downstream-boundary` policy,
   the spec states explicitly that pin validation compares pointers only and asserts nothing
   about upstream runtime behavior, so no future reader mistakes the anchor for a
   compatibility claim.
6. **Main spec created during apply, not by archive.** Verified on a scratch copy: native
   archive copies Purpose and Requirements into the main spec but drops the `> req:` and
   `> structure:` header lines, which leaves the post-archive architecture checker
   (`spec.reference_missing` on the main spec) and the coverage checker (missing owned IDs)
   red. Creating the main spec manually during apply — with both header lines — keeps every
   phase green: pre-archive the architecture checker accepts the manual main spec, and at
   archive the CLI detects the requirements are already in sync and changes nothing (no
   duplication). The alternative, relying on native archive alone, was rejected on this
   measured evidence.

## Risks / Trade-offs

- [Spec text drifts from checker semantics over time] → the checker is the enforcer; any
  semantic change to structure governance must move manifest, spec, and checker in the
  same owning change, and the closeout gate will refuse partial moves.
- [Over-specification of internals] → scenarios reference only checker exit codes and
  named violations; no internal function or class names appear in the spec.
- [Three known reds mask a latent fourth] → the apply tasks measure the full aggregate
  closeout gate (all six components) plus strict validation, not only the three named
  components.

## Migration Plan

Single apply: land the main spec and the docstring annotation together, then measure —
governance unittest suite, the six component checkers, the aggregate closeout gate
(exit code read directly, never through a pipe), and `openspec validate
establish-project-structure --strict`. Rollback is reverting the two files; the registry
is untouched throughout, so no data migration exists.
