# Proposal

## Why

Operators must reconstruct the execution chain from several guides, while the root CLI mixes presentation with runtime assembly and an event recorder sits inside executable tests. Make the existing responsibility boundaries visible in both directories and navigation so maintenance starts at the lowest responsible test seam.

## Change Focus

- **Primary module / causal owner:** Harness entry surface: command parsing/presentation and its existing runtime composition.
- **Seam classification:** wiring — relocates presentation and composition without changing cognition, state rules or admission.
- **Question:** Can operators locate and exercise interaction, assembly, deterministic control, test contracts, sample data, and developer tooling without reconstructing the whole research run?
- **Necessary adjacent/external contracts:** project-structure manifest: register relocated paths while retaining four ownership layers; deerflow-wiring: preserve lazy imports, config and stream assembly; entry-surface: preserve all six verbs and their observable effects; delivery-lanes: preserve offline discovery and separate framework smoke; release-face: retain root CLI and sibling gitlink checkout layout.
- **Evidence seam:** CLI help and fixture subprocess journey; focused composition/renderer/contract tests; actual unittest discovery; architecture and documentation checks with negative controls.
- **Not in scope:** Model cognition/prompts/tools, new product behavior, lifecycle or persisted schema changes, immediate refine execution, worker/service deployment, live API quality evaluation, upstream modifications/source browsing, resolving the main structure spec's inventory-scope discrepancy.
- **Triggered review policies:** local-context, agent-information-map, authority-and-projections, change-admission

Cognition is not causal: this change reorganizes existing deterministic presentation and wiring without changing model-visible assignment, tools, outputs, or admission. Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink.

## What Changes

- Keep `cli.py` as the stable launcher; place the CLI implementation and shared renderer together in `runtime/interaction/`.
- Extract filesystem locations, pin resolution, Bundle lookup and foreground client assembly into `runtime/entry.py`; state/admission rules remain with existing owners.
- Move the developer event recorder to `tools/`, remove its imports of private CLI helpers, and retain the `make record-stream` command and overwrite semantics.
- Make `tests/contract/` executable and move the existing interface mirror tests there. Preserve offline gate discovery; keep framework tests in integration and samples in fixtures.
- Consolidate the operator control map in the application README and repository map; give commands, fixtures and tools clear destinations; fix unsupported dependency, packaging and coverage claims.
- Update affected imports, config references only if needed, structural inventory, proof-lane selectors and current navigation. Preserve all pre-existing worktree edits.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a behavior-preserving refactor and documentation/tooling correction; `.openspec.yaml` declares `skip_specs: true`. Existing main specs remain authoritative. No new layer or normative test-evidence policy is introduced.

## Impact

Application launcher, `runtime/`, tests, developer tools, README/AGENTS/COMMANDS/maps, and path inventory. Public CLI invocations, configuration names/provider paths, Run Bundle data and DeerFlow pin remain compatible. Internal renderer/test/tool import locations converge directly on the new layout; enumerate and update all repository consumers. No credentialed external run, push, history rewrite or deletion of user data is required.
