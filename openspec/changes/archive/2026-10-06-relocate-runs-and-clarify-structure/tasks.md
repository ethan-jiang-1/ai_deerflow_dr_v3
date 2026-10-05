# Tasks

## 1. Path contract and runs root (red-green)

- [x] 1.1 Red: update `tests/unit/domain/test_bundle_domain.py` to assert the new root
  name (`runs/d_...`) and `bundle_dir` naming; run and confirm failure names the old
  contract (exit non-zero)
- [x] 1.2 Red: extend `tests/unit/interaction/test_entry_composition.py` with cases for
  `DEEP_RESEARCH_RUNS_ROOT` override (redirects root) and default (repo-root `runs/`,
  outside `deep_research_harness/`); confirm failure
- [x] 1.3 Green: `domain/bundle.py` — replace `SCOPE_ROOT` with `RUNS_ROOT_NAME`,
  rename `bundle_dir` parameter and error text (scope→run); `runtime/entry.py` —
  `RUNS_ROOT` from `REPO_ROOT / bundle.RUNS_ROOT_NAME` with env override; update
  `runtime/interaction/cli.py` references; `make verify` green
- [x] 1.4 Add the relocated-legacy-bundle test: create a bundle-shaped directory,
  move it wholesale, assert status/inspect still resolve it (locks the migration
  safety property)

## 2. Scripted providers rename

- [x] 2.1 Red: `tests/contract/test_wiring_mirror.py` asserts config `use:` seams point
  at `deerflow_deep_research.runtime.scripted`; confirm failure
- [x] 2.2 Green: `git mv` `runtime/fixtures` → `runtime/scripted`; update
  `config/fixture.yaml` seams, docstring, and any imports; `make verify` green

## 3. Physical data migration

- [x] 3.1 Go/no-go pre-check: sample every `state.json` under `scopes/` — assert no
  absolute filesystem paths; assert target `runs/` absent; abort on any failure
- [x] 3.2 `mv deep_research_harness/scopes runs`; remove empty `scopes/`; `git status`
  shows no tracked-file change; `python3 cli.py status <relocated-bundle-id>` succeeds
  against one moved bundle

## 4. Playbook fold-in

- [x] 4.1 `git mv deep_research_harness/playbook/run-research.md
  deep_research_harness/docs/playbook/run-research.md`; re-base its internal links;
  update routing lines in `COMMANDS.md`, harness `README.md`, `AGENTS.md` info map
- [x] 4.2 Verify every routing target resolves (all `docs/playbook/` links exist);
  `make verify` green

## 5. Vocabulary and map updates (docs)

- [x] 5.1 Sweep retired vocabulary: replace `scopes`/`scope root` references in harness
  `README.md`, `docs/control-map.md`, `docs/run-bundle.md`,
  `docs/testing-and-evaluation.md`, `docs/known-limitations.md` (history note kept as
  history), `tests/README.md`, `tools/README.md`, `tools/record_stream.py`
  (`--runs-root`), root `README.md`
- [x] 5.2 Root `README.md` becomes the one-screen map: embedded entry chain, directory
  table (incl. `runs/`), run/debug/test lanes; curated links demoted below the map
- [x] 5.3 Harness `README.md` and `docs/control-map.md` directory tables show the new
  layout (`runs/`, `docs/playbook/`, `runtime/scripted/`)

## 6. Governance registry sync and gates

- [x] 6.1 Update `openspec/governance/required-paths.toml`: playbook paths →
  `docs/playbook/`, `runtime/fixtures` → `runtime/scripted`; update
  `project-structure.toml [ignored_paths]` (harness `scopes/` out) and the actual
  `.gitignore` files (harness drops `scopes/`; root gains `runs/` as plain repo
  infrastructure, not registry-registered)
- [x] 6.2 Run architecture and governance checkers (`check_project_architecture.py`
  and the governance suite) — all green; `make verify` green; `make smoke` green
  (fixture ladder, real framework)
- [x] 6.3 Fresh receipt: record command, exit code, revision for verify/smoke/status
  checks; archive the change via the OpenSpec workflow
