# Proposal

## Why

The structural manifest still declares a graph layer and a `NODE_SPEC` node-package
grammar that v3 never used: `graph/` holds two skeleton `__init__.py` files,
`tests/graph/` a single `.gitkeep` (verified against the tree), and no code, doc, or
test ever consumes the grammar. The digest boundary decision — outer orchestration is a
plain state machine, research cognition is DeerFlow's native capability — retired that
design, and the wiring plan's decision 3 撤s it. Leaving a dead grammar inside the
"exact structural authority" misdescribes the project just before the first product
change lands real code under the surviving layers, and `runtime`'s declared import
allowance still points at the layer being removed.

## What Changes

- Contract (`openspec/governance/project-structure.toml`): `ownership_layers` 5 → 4
  (`graph` removed); `[imports]` 6 keys → 4 (`graph` and `nodes` keys removed;
  `runtime` drops `graph`); the `[node_packages]` section is deleted. Declaring a
  `graph`/`nodes` layer, any ownership layer beyond the canonical four, or a
  `[node_packages]` table becomes a loud governance failure — reintroducing the grammar
  requires a `project-structure` spec change.
- Checker (`openspec/governance/check_project_architecture.py`): the layer vocabulary
  (`INTERNAL_LAYERS`) and the fixed non-weakenable internal-import policy drop
  `graph`/`nodes`; a manifest declaring `[node_packages]` or a non-canonical ownership
  layer now fails validation with a named violation; node-package validation and the
  nodes-layer import exceptions are deleted; the generated locator renders four layers
  and no node-grammar line. Also corrects the stale "owned by PRS-002" comment to the
  actual owner PRS-001.
- Inventory (`openspec/governance/required-paths.toml`): `PRS-001` drops the two graph
  `__init__.py` files; `CIG-001` drops the `graph/`, `graph/nodes/`, and `tests/graph/`
  directories.
- Tree: delete `deep_research_harness/src/deerflow_deep_research/graph/__init__.py`,
  `deep_research_harness/src/deerflow_deep_research/graph/nodes/__init__.py`, and
  `deep_research_harness/tests/graph/.gitkeep`, together with the now-empty directories.
- Guide and routing text: re-render the generated locator in
  `deep_research_harness/AGENTS.md`; reassign its "Composition, routing, or capability
  injection" row to `runtime/`; align the remaining hand-authored graph mentions in
  `deep_research_harness/AGENTS.md`, `deep_research_harness/README.md`,
  `deep_research_harness/tests/README.md`,
  `deep_research_harness/docs/runtime-architecture.md`,
  `openspec/governance/README.md`, `openspec/governance/architecture-policy.md`, and
  `openspec/change-guidance/local/deep-research.md`.
- Registry: PRS-001's description in `openspec/governance/req-registry.yaml` drops
  "节点语法" (the append-only ID discipline itself is untouched).
- Red controls: the governance unittest suite gains negative controls proving the
  removed grammar fails loudly — a manifest with a `[node_packages]` table, an
  ownership layer beyond the canonical four, or an `[imports]` key beyond the four
  layers each fails with a named violation.

No application behavior changes: the harness has no runtime code yet; this is a
governance-contract correction that keeps every surviving guard intact.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `project-structure`: the requirement "Structural manifest is the exact structural
  authority" drops the node-package grammar from the declared inventory, pins the
  closed four-layer vocabulary, and gains a scenario making the removed grammar fail
  loudly. The other two requirements are untouched.

## Impact

- Modified: `openspec/governance/project-structure.toml`,
  `openspec/governance/required-paths.toml`,
  `openspec/governance/check_project_architecture.py`,
  `openspec/tests/governance/test_split_manifest.py`,
  `openspec/governance/architecture-policy.md`,
  `openspec/governance/req-registry.yaml` (PRS-001 description only),
  `openspec/governance/README.md`, `openspec/change-guidance/local/deep-research.md`,
  `deep_research_harness/AGENTS.md` (generated block re-rendered + hand-authored rows),
  `deep_research_harness/README.md`, `deep_research_harness/tests/README.md`,
  `deep_research_harness/docs/runtime-architecture.md`.
- Deleted: the two graph `__init__.py` files and `tests/graph/.gitkeep` with their
  directories.
- New: one delta spec (`specs/project-structure/spec.md`, MODIFIED requirement). No new
  data files, no new checkers, no new requirement IDs.
- No application code (none exists yet), no CI workflow change (the checker and unittest
  suite already ride the canonical sequence), no `deerflow/` contact — ordinary
  downstream work neither modifies nor source-browses the `deerflow/` gitlink; this
  change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/project-structure.toml` — the
  manifest is the exact structural authority, so the decision "which ownership layers
  and package grammars exist" lives there; every other edit synchronizes to it.
- **Seam classification:** deterministic-guardrail — the changed observable behavior is
  machine-checked structure validation (checker exit codes and the rendered locator);
  no model cognition is involved.
- **Question:** How does the declared-but-never-used graph layer and node grammar leave
  the structural authority completely — contract, inventory, checker vocabulary, fixed
  import policy, guide locator, routing text, and tree — without loosening any
  surviving guard, and what makes its return loud?
- **Necessary adjacent/external contracts:** `openspec/governance/check_project_architecture.py` (answers: where the fixed
  non-weakenable internal-import policy and the closed layer vocabulary are enforced,
  and how the removed grammar becomes a named validation failure);
  `openspec/governance/required-paths.toml` (answers: which inventory entries the
  deleted tree paths release so declared-paths-exist stays exactly true);
  `deep_research_harness/AGENTS.md` (answers: how the generated locator re-renders from
  the manifest and where composition/routing questions route now that `graph/` is
  gone); `openspec/governance/architecture-policy.md` +
  `openspec/governance/req-registry.yaml` (answers: what the manifest update protocol
  and the PRS-001 description must say once the grammar is gone);
  `openspec/tests/governance/test_split_manifest.py` (answers: which fixtures and
  negative controls prove the new guards red and the surviving guards green).
- **Evidence seam:** the architecture checker's direct exit codes on the real tree, the
  governance unittest suite including the new negative controls (invalid fixtures red
  by construction), the plan/closeout project gates, and
  `openspec validate remove-graph-layer --strict`.
- **Not in scope:** the checker's v2-inherited fixture-package machinery
  (`fixture_root` / `fixture_imports` / `ResearchGraphRecipe`) and its sibling v2
  leftover, the checker-internal `tool` layer special case for a root `tool.py` that v3
  has no owner for — both are real dead vocabulary, and retiring them is their own
  argued change (this change touches neither);
  `openspec/config.yaml`'s authoring vocabulary ("graph route", StateGraph routing) —
  DeerFlow-framework terminology, not a claim that the harness owns a graph layer; the
  fixture strings in `openspec/tests/governance/test_terminology_rules.py`; any new
  ownership layer; any `deerflow/` change.
- **Triggered review policies:** control-placement, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| The harness no longer declares a graph composition layer or a node-package grammar; composition/routing authority is DeerFlow's own assembly surface, reachable later through the `runtime/` binding layer | Human judgment (digest boundary decision: outer orchestration = plain state machine; cognition = DeerFlow native); this change only lands it in the authority | The structural manifest enumerates exactly the four canonical ownership layers; `check_project_architecture.py` fails loudly, naming the violation, on the removed grammar | non-bypassable | A revived grammar cannot re-enter silently: the manifest vocabulary is closed-set checked, and reintroduction requires a `project-structure` spec change; no replacement control layer is created — the composition routing row re-points to `runtime/` | Deletes a five-surface grammar (contract section, checker policy, node validation, guide line, inventory entries) that guarded nothing | Architecture checker exit codes; governance unittest negative controls on invalid manifests |
