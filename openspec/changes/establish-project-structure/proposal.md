# Proposal

## Why

The structural governance machinery is fully built and enforced — `project-structure.toml`
(contract), `required-paths.toml` (inventory), the architecture checker, and the generated
locator in the module guide — but requirement `PRS-001` sits in the registry without an
owning main spec. Three governance gates therefore fail with the same root cause
(`check_project_reqs`, `check_project_architecture`, `check_project_req_coverage`), and
every later change's closeout is blocked until the structural capability owns its spec.

## What Changes

- Add the first main spec, `openspec/specs/project-structure/spec.md`, owning `PRS-001`:
  the structural manifest is the exact structural authority; the architecture checker
  validates declared paths, kinds, import layering, and node-package grammar; the module
  guide's generated locator must match the manifest.
- Add an `@impl PRS-001` evidence annotation to the `check_project_architecture.py` module
  docstring so requirement coverage has a script-evidence anchor (no checker rule semantics
  change).
- Verify the existing `req-registry.yaml` entry for `PRS-001` still matches the established
  spec (the ID is already registered; apply verifies, it does not rewrite).
- Effect: the three red gates turn green and `check_project_gate.py --phase closeout`
  reaches exit 0 for the governance suite.

## Capabilities

### New Capabilities

- `project-structure`: owns required behavior of structural governance — the manifest
  (`project-structure.toml` contract + `required-paths.toml` inventory) as the exact
  structural authority, deterministic validation of declared structure, regeneration of the
  module guide's generated locator, the upstream gitlink as a declared metadata anchor, and
  the coupling between registered requirement IDs and owning main specs.

### Modified Capabilities

(none — this is the first main spec in the repository; no existing capability's
requirements change)

## Impact

- `openspec/specs/project-structure/spec.md` — new file, the first main spec.
- `openspec/governance/check_project_architecture.py` — module docstring gains the
  `@impl PRS-001` annotation; checker rule semantics untouched.
- Governance gate outcome: 3 red components → green; closeout aggregate reaches exit 0.
- No application code, no harness runtime behavior, no CI workflow, and no fixture
  composition changes in this change.

Boundary statement: ordinary downstream work neither modifies nor source-browses the
`deerflow/` gitlink. This change only names the gitlink metadata already declared in
`project-structure.toml` (`[upstream_gitlink]`) and establishes its owning spec; it makes
no claim about upstream runtime compatibility and runs no upstream compatibility test.

## Change Focus

- **Primary module / causal owner:** `openspec/governance` — the structural manifest and the architecture checker own the semantic decision of what structure is declared and how it is validated; this change promotes that decision into an owning main spec.
- **Seam classification:** deterministic-guardrail — the changed observable behavior is mechanical gate validation via checker exit codes; no model cognition is involved.
- **Question:** Which observable behavior must the project-structure capability guarantee so that the manifest, the architecture checker, the module guide locator, and the requirement registry stay one coherent structural authority?
- **Necessary adjacent/external contracts:** `openspec/governance/project-structure.toml` + `required-paths.toml` (answers: what exact paths, kinds, import layering, and node-package grammar are declared); `openspec/governance/req-registry.yaml` (answers: does the registered `PRS-001` description match the spec being established); `project-structure.toml` `[upstream_gitlink]` (answers: which pinned commit the metadata anchor names — metadata only, no runtime compatibility question is opened).
- **Evidence seam:** the governance checker suite at its lowest responsible seam — `check_project_architecture.py`, `check_project_reqs.py`, `check_project_req_coverage.py` exit codes through `openspec/governance/check_project_gate.py --phase closeout`, plus the governance unittest suite staying green. No new test infrastructure.
- **Not in scope:** harness application code, fixture composition, CI workflows, DeerFlow runtime compatibility evidence, checker rule-semantics changes, spec semantics of any other capability.
- **Triggered review policies:** deerflow-downstream-boundary
