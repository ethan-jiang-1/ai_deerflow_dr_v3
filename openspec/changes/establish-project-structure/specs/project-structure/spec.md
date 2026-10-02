> req: PRS-001
> structure: openspec/governance/project-structure.toml

# Spec Delta

## Purpose

Owns the required behavior of structural governance: the declared structural manifest is
the exact structural authority for the repository, validation of declared structure is
deterministic and fails loudly on drift, and the pinned upstream gitlink is treated as a
metadata-only anchor that claims no runtime compatibility.

## ADDED Requirements

### Requirement: Structural manifest is the exact structural authority

The project SHALL declare its complete structural inventory — required files and
directories with their kinds, source-root ownership layers, import layering, node-package
grammar, and ignored paths — in the structural manifest
(`openspec/governance/project-structure.toml` contract plus
`openspec/governance/required-paths.toml` inventory), and that manifest SHALL be the only
structural authority. The architecture governance checker SHALL validate the checked-out
tree against the manifest and SHALL fail, naming the violation, whenever declared structure
is missing or undeclared structure is present. The generated structure locator inside the
module guide (`deep_research_harness/AGENTS.md`) SHALL be renderable from the manifest and
SHALL NOT be maintained by hand; a locator that disagrees with the manifest SHALL fail
governance validation.

#### Scenario: Matching tree validates clean

- **WHEN** the architecture governance checker runs from the repository root against a tree
  whose inventory matches the manifest
- **THEN** the checker exits 0 and reports no structural violations

#### Scenario: Drift or forbidden structure fails loudly

- **WHEN** a declared required path is missing, a source file appears in a forbidden root
  or shared-module location, or an import violates the declared layering
- **THEN** the checker exits non-zero and names the violated declaration

#### Scenario: Hand-edited locator is rejected

- **WHEN** the generated structure locator block in the module guide disagrees with the
  manifest while the manifest is unchanged
- **THEN** governance validation exits non-zero and identifies the generated block as the
  drifted surface

### Requirement: Upstream gitlink is a metadata-only anchor

The structural manifest SHALL declare the pinned upstream gitlink (submodule path and
pinned commit) as declared metadata. Gitlink validation SHALL be metadata-only: it SHALL
compare the declared commit with the checked-out gitlink pointer and SHALL NOT test,
claim, or imply upstream runtime compatibility. Downstream work SHALL neither modify nor
source-browse the gitlink unless a change explicitly owns and approves that boundary.

#### Scenario: Pointer disagreement fails

- **WHEN** the declared gitlink commit differs from the checked-out submodule pointer
- **THEN** governance validation exits non-zero and names the disagreement

#### Scenario: Pointer agreement proves metadata only

- **WHEN** the checked-out gitlink pointer matches the declared commit while the upstream
  content itself is untested by this governance
- **THEN** gitlink validation passes without running or asserting anything about upstream
  runtime behavior

### Requirement: Registered requirements are owned by specs

Every requirement ID registered in `openspec/governance/req-registry.yaml` SHALL be owned
by a main spec (declared on the spec's `> req:` line before its first heading) or by an
active change's delta spec header. A registered ID owned by neither SHALL fail requirement
governance and be reported as an orphan, with the legal resolution being an owning spec,
an active delta, or explicit retirement marked in the registry. The registry SHALL be
append-only: allocated IDs are never reused, and retired IDs stay declared with a
retirement marker.

#### Scenario: Orphan registry ID fails governance

- **WHEN** requirement governance runs while a registered ID appears in no main spec and
  no active delta header
- **THEN** validation exits non-zero and reports the ID as an orphan with the legal
  resolutions

#### Scenario: Retired ID is declared, never reused

- **WHEN** a registered ID is marked retired in the registry
- **THEN** the ID remains declared in the registry, is reported as retired rather than
  orphan, and allocating the same ID again fails governance
