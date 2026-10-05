# Design

## Context

The bundle path contract is owned by `domain/bundle.py` (RUB-001); the runs root is
resolved in `runtime/entry.py` (`SCOPES_ROOT = HARNESS_ROOT / "scopes"`, a literal that
bypasses the domain constant `SCOPE_ROOT = "scopes"` — itself a dead constant with no
consumers). The CLI (`runtime/interaction/cli.py`) consumes `entry.SCOPES_ROOT` in seven
places. `config/fixture.yaml` `use:` seams point at
`deerflow_deep_research.runtime.fixtures`; the contract mirror
(`tests/contract/test_wiring_mirror.py`) asserts that module path appears in the config.
`agent-playbook`'s routing targets live under `playbook/`; the governance registry
(`required-paths.toml`, `project-structure.toml [ignored_paths]`) registers these paths
and is validated by `check_project_architecture.py`. Verified migration precondition:
`state.json` carries no absolute paths (`delivery_artifact` is bundle-relative), so
wholesale directory moves are safe. Local data today: `deep_research_harness/scopes/`
(~1GB, gitignored).

## Goals / Non-Goals

**Goals:**

- One name (Run Bundle), one home (`runs/` at the repository root) for runtime state.
- The application subtree contains only product code, tests, docs, config, and tools —
  no run data.
- Root README answers "entry point? where does state live? how to test?" in one screen.
- Every cross-reference (docs, tests, config, registry, .gitignore) points at the new
  layout; nothing references the retired names.

**Non-Goals:**

- No behavior change in run engine, admission, state machine, or CLI verb semantics.
- No state schema change; no registry/recovery semantics for bundles.
- No change to the composition ladder names (`fixture` / `base` config keys stay).
- No multi-operator or networked storage semantics.

## Decisions

### D1 — Runs root at the repository root, not inside the harness, not in $HOME

`<repo>/runs/` sits beside `deep_research_harness/` and `deerflow/`. Alternatives
considered: keeping it inside the harness under a new name (rejected: the physical
pollution of app-tree exploration — the actual complaint — would survive the rename);
`~/.deerflow-dr/runs` (rejected: run bundles are per-checkout working data tied to a
pinned submodule, and hidden state off-tree hurts exactly the driver legibility this
change serves; also breaks the "delete a checkout deletes its runs" containment).
Trade-off accepted: the root README must teach `runs/` explicitly, and root `.gitignore`
gains the entry.

### D2 — One constant, consumed end-to-end; env override named `DEEP_RESEARCH_RUNS_ROOT`

`domain/bundle.py` declares `RUNS_ROOT_NAME = "runs"` (retiring `SCOPE_ROOT`).
`runtime/entry.py` resolves `RUNS_ROOT = REPO_ROOT / bundle.RUNS_ROOT_NAME`, overridable
by `DEEP_RESEARCH_RUNS_ROOT` (joining the existing `DEEP_RESEARCH_*` env family used by
the recursion limit). CLI and tools keep consuming `entry.RUNS_ROOT` — the single
resolution point. Alternative considered: a config-ladder key (rejected: the root is a
checkout-level operational fact, not a per-composition research fact; ladder configs
travel with research semantics, the runs root must not).

### D3 — `runtime/fixtures` → `runtime/scripted`, ladder name untouched

The module holds the scripted-ladder providers (ScriptedChatModel, FakeWebSearchTool,
replay model). Renaming the module to `scripted` separates "the fixture ladder" (a
composition value, unchanged) from "the scripted providers" (code), killing the
collision with `tests/fixtures/` (sample data). Alternatives: `runtime/providers`
(rejected: vague), keeping the name and renaming test fixtures instead (rejected:
`tests/fixtures` is the widespread testing convention; the odd one out is the runtime
module).

### D4 — Playbook folds under `docs/playbook/`, spec delta relaxes the routing root

`agent-playbook`'s requirement changes from `playbook/` to `docs/playbook/` so the
registry and COMMANDS routing stay spec-legal. One file moves
(`run-research.md`); its internal relative links are re-based (docs/ already is the
link root, so most links get shorter).

### D5 — Physical migration is a plain `mv`, gated by a fresh pre-check

Pre-check (before the move): grep a sample of `state.json` files for `/` absolute-path
fields; verify the target `runs/` does not already exist. Move
`deep_research_harness/scopes/*` → `runs/`, then remove the empty `scopes/` directory.
Rollback is the reverse `mv` plus `git checkout` of code/doc changes — the move itself
touches no tracked file. The one-time move is recorded in this change's closeout notes,
not as a permanent migration feature (per the permanent-deletion/no-silent-migration
requirement, the code gains no migration logic; the spec's relocated-legacy-bundle
scenario locks the safety property instead).

### D6 — Root README becomes the one-screen map, routing demoted not deleted

The root README embeds: the entry chain (already drawn in harness README), the
repository directory table with one-line "what lives here / who owns it", and the three
lanes (run / debug / test) with their commands. The existing curated links move below
the map as "deep dives". The harness README keeps its role as the app-level reading
map; both now show `runs/` explicitly.

## Risks / Trade-offs

- [Root README duplication of harness README chain] → The chain diagram lives in the
  root README as the navigation entry; harness README keeps the detailed Reading Map.
  Doc-hygiene budget gate runs at closeout to catch drift.
- [Checkouts made between change and pull see stale `scopes/`] → Non-issue for the
  single-driver workflow; the closeout note names the manual `mv` for any other
  checkout.
- [Absolute paths hidden in `checkpoint.sqlite` or journals] → Journals carry relative
  paths by contract; checkpointer stores thread content, not filesystem paths. The
  pre-check samples a state.json set; any discovered absolute path aborts the move
  (go/no-go gate in tasks).
- [Mirror test and smoke depend on module path] → Mirror assertion updated in the same
  red-green step; `make smoke` (fixture ladder, real framework) re-run at closeout.
- [Two `.gitignore` files to keep in sync] → The architecture checker registers exactly
  one canonical ignore policy (`deep_research_harness/.gitignore`, now without
  `scopes/`); the root `.gitignore`'s `runs/` entry is ordinary repo infrastructure
  and stays outside the registry (extending the checker to multiple ignore files would
  be a governance change larger than this one's need).

## Migration Plan

1. Land code + docs + registry changes with red-green tests (old path tests go red on
   the new contract, then green on implementation).
2. Stop any running bundle pump (none expected: driver-attended foreground CLI).
3. Pre-check then `mv deep_research_harness/scopes runs` (same filesystem: rename, no
   copy).
4. Update `.gitignore` files; verify with `git status` that nothing tracked moved.
5. Gate: `make verify`, `make smoke`, governance checkers, `cli.py status` on one
   relocated bundle id (proves the relocated-legacy-bundle scenario).
6. Rollback: reverse `mv`, `git checkout` the change's commits — no tracked-file
   coupling.
