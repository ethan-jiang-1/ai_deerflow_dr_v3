# Design

## Context

See [proposal.md](proposal.md). Current checked-out sources have four ownership layers. `cli.py` owns parsing, rendering, pin lookup, Bundle search and foreground assembly. The event recorder imports private CLI helpers and is invoked as `tests.integration.record_stream`, although integration deliberately lacks a package marker. Twelve unit files and three integration files exist; contract is an empty placeholder. Existing navigation edits are user work and are retained.

Verified baseline: 116 offline tests pass; architecture/doc-hygiene pass from read-only audit. Live API and clean checkout cold start are unverified. Main spec promises complete inventory while the checker only checks registered paths plus selected source/import prohibitions; this is a recorded discrepancy, not authority to change governance here.

## Goals / Non-Goals

Use directory placement to distinguish command interaction, runtime wiring, tests, data and tools. Keep one short operator entry with an execution spine and action-to-test map. No new canonical ownership layer, state rule, model role, public verb or storage schema.

## Decisions

### 1. Interaction remains owned by runtime, in a named subpackage

`runtime/interaction/cli.py` owns argument parsing, output, watch polling and command projections; `runtime/interaction/render.py` keeps the existing shared phrase functions. The root `cli.py` is a stable launcher that adds local src to the path and calls main. This gives interaction its own directory without violating the four-layer contract.

`runtime/entry.py` owns explicit checkout locations, read-only git pin resolution, Bundle lookup and assembly/foreground execution. It delegates to bundle_actions, client and run_engine, and returns existing typed state. It accepts the already-created handle/config and the event sink. The existing CLI PyYAML reader moves with assembly; register `yaml` as a runtime external namespace and authorize it in the checker whitelist (no new runtime behavior or dependency installation). Keep print, argv and polling out of assembly; keep transitions/admission with their current owners. CLI creates the Bundle and prints the start line before invoking foreground execution, preserving ordering and missing-dependency failure behavior.

### 2. Converge private imports; retain public commands and persisted paths

| Surface | Grade | Cutover |
| --- | --- | --- |
| `python3 cli.py <verb>` / make targets | Operator public | Preserve launcher and six verbs |
| scopes Bundle schema/path/checkpoint | Persisted | No change, no data migration |
| config provider paths under runtime.fixtures | Config-consumed | Preserve; explain provider code versus input samples |
| runtime.render import | Repository internal | Move to runtime.interaction.render; migrate all active consumers; no redundant shim |
| tests.unit.test_wiring_mirror | Developer internal | Move to tests.contract.test_wiring_mirror and update documented selectors |
| tests.integration.record_stream | Developer internal | Retire; target invokes tools/record_stream.py |

No known external import compatibility promise exists for the internal renderer or recording module. Archived artifacts remain historical; active docs/registries/consumers follow new paths.

### 3. Offline contract tests are still part of verify

Add contract/__init__.py and move the existing wiring mirror file, preserving all assertions and the offline gate. No integration/__init__.py: the default gate must still exclude framework tests. Verify exact collected test IDs before/after, translating only the relocated prefix. The actual framework constructor/event comparison stays integration because it requires that environment. Mixed test concerns remain explicit in the asset map; do not split every file merely to fit names.

### 4. Tools are explicitly invoked, data is consumed by tests

Move record_stream.py into tools and update its path calculation/entry imports and Makefile invocation. Preserve model ladder selection and direct sample overwrite; validate with help/import or fixture-only temporary outputs, never update retained real samples as a side effect. A tools README explains execution and effects. A fixtures README maps files to consumers and provenance gaps. runtime.fixtures remains where dynamic config can load it; do not rename this configured seam for cosmetic consistency.

### 5. Navigation has one short start and focused destinations

Application README carries the short execution spine, directory responsibilities, run/observe/test commands and routes. Repository map expands ownership and the four operating concerns. Runtime map explains run data/release/current limitations; research-process focuses cognition/binding; tests README selects assets/lane. AGENTS stays a short trigger router and within existing budgets. Avoid adding another overlapping control-map document.

Correct current-fact claims: runtime needs DeerFlow/uv sync; stdlib/offline describes the default test gate. Providers are included by current wheel configuration; wheel is not a full release. State is durable in per-Bundle directories, no central run database. Refine enters next generation but does not execute it. Inspect currently shows journal/evidence/snapshot, not a checkpoint summary. Final-report coverage is claimed only after a fixture journey asserts report and admission entry.

## Ownership And Failure

State remains domain.state_machine + runtime.bundle_actions/bundle_state; checkpoint remains Bundle sync saver; accepted artifacts remain validator + admission/ledger; diagnostics/journal are projections. Entry assembly is a caller, not a second controller. Existing run_engine bounded continuation, cancellation and failed-resume behavior remains intact. Failed imports still disclose environment remedy; missing Bundle remains permanently unavailable. No retry/recovery policy is added.

## Migration Plan

1. Capture current discovery IDs and focused baseline; add meaningful assembly/launcher regression examples and observe expected failures.
2. Extract entry wiring; move interaction files, tests and tool in bounded slices; update imports after each slice.
3. Update inventory/selectors/navigation with each affected path; regenerate locator with existing checker.
4. Verify discovery membership, offline gate, fixture CLI journey/report/admission, recorder path without external calls, and governance/doc/strict checks.
5. Runner writes fresh command/exit/revision/digest receipts. Review only this change atop preserved pre-existing edits. Archive once all tasks and checks close.

Rollback is source-only: repair failing slice or restore this change's edits from the captured baseline, without git reset or overwriting pre-existing work. No Bundle or retained fixture deletion. If one slice fails, keep change active and complete repair; no partial success claim.

## Risks / Trade-offs

- Discovery can silently broaden or shrink → compare IDs, preserve integration exclusion, add known-failing offline contract example in temporary discovery sandbox.
- Text-based command guard may read launcher instead of implementation → test actual help/parsing and route the guard to its owner.
- Moving imports outside architecture scan → interaction stays under runtime and tools only orchestrates approved package interfaces; architecture/import checks remain applicable.
- Navigation drift and long guides → reuse existing map files, exact paths in manifest, selective README routes and fresh link checks.
- Model quality is outside deterministic evidence → fixture journey proves wiring only; explicitly retain live quality/cold-start gaps.

## Alternatives

- Add a fifth application or UI ownership layer: rejected; interaction is already runtime-owned and a named subpackage closes clarity without changing import policy.
- Documentation only: rejected for this round; user requested both map and physical organization, and CLI/tool placement contains actual responsibility mixing.
- Rename runtime.fixtures or move providers into tests: rejected; checked-in config loads this namespace, release includes provider code, and test data already has a separate consumer role.
- Broad relocation of every runtime file into storage/adapter packages: rejected; increases import churn without a concrete ambiguous owner.
- Start implementing refine rerun/worker: rejected; changes product semantics and requires separate human decision.
