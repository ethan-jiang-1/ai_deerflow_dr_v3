> req: PRS-001
> structure: openspec/governance/project-structure.toml

# Spec Delta

## MODIFIED Requirements

### Requirement: Structural manifest is the exact structural authority

The project SHALL declare its complete structural inventory — required files and
directories with their kinds, source-root ownership layers, import layering, and ignored
paths — in the structural manifest
(`openspec/governance/project-structure.toml` contract plus
`openspec/governance/required-paths.toml` inventory), and that manifest SHALL be the only
structural authority. The manifest SHALL declare exactly the canonical ownership layers
`runtime`, `domain`, `engine`, and `agents`, its `[imports]` table SHALL define exactly
those four layers, and it SHALL NOT declare a node-package grammar: a `graph` or `nodes`
layer, an ownership layer or `[imports]` key beyond the canonical four, or a
`[node_packages]` table SHALL fail governance validation, naming the removed grammar. The
architecture governance checker SHALL validate the checked-out tree against the manifest
and SHALL fail, naming the violation, whenever declared structure
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

#### Scenario: Removed node grammar fails loudly

- **WHEN** the manifest declares a `graph` or `nodes` layer, an ownership layer or
  `[imports]` key beyond the canonical four, or a `[node_packages]` table
- **THEN** the architecture governance checker exits non-zero and names the removed
  node-package grammar as the violation
