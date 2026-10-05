# Tasks

## 1. 基线与 guard（红先行）

- [x] 1.1 Capture the before test ID list
  (`PYTHONPATH=src python3 -m unittest discover -s tests -v`, sed-extract IDs,
  expect 125). Verify: file saved with 125 IDs.
- [x] 1.2 Write `tests/unit/test_collection_guard.py` per design decision 2
  (marker presence/absence invariants, in-process discovery namespace
  assertions) BEFORE creating the owner packages. Verify: it FAILS red naming
  the missing owner package markers (capture the red output for the receipt).

## 2. 迁移与索引修正

- [x] 2.1 `git mv` the 12 test files into the four owner directories
  (domain: test_bundle_domain; engine: test_admission_engine; runtime:
  test_bundle_runtime, test_state_read_diagnosis, test_admission_runtime,
  test_run_engine, test_event_stream_replay, test_subagent_posture;
  interaction: test_entry_composition, test_entry_surface,
  test_command_surface, test_agent_playbook); create the four `__init__.py`
  package markers. Verify: guard and `make verify` both green.
- [x] 2.2 Bump the `parents[]` indices in the 7 moved files that anchor by
  `__file__` (+1; test_event_stream_replay's `parents[1]` → `parents[2]`).
  Verify: `grep -rn "parents\[" tests/unit/` shows every moved file at the
  correct depth and verify stays green.
- [x] 2.3 Capture the after test ID list; diff against before; verify the diff
  is EXACTLY the registered prefix mapping `tests.unit.test_X` →
  `tests.unit.{owner}.test_X` with identical count (125 + guard's own tests).

## 3. 登记与文档同轮

- [x] 3.1 Update `openspec/governance/required-paths.toml` (entry-surface
  group: `tests/unit/test_entry_composition.py` →
  `tests/unit/interaction/test_entry_composition.py`). Verify:
  `python3 openspec/governance/check_project_architecture.py` exits 0.
- [x] 3.2 Update doc links: `docs/quality-register.md`, `docs/testing-and-evaluation.md`,
  `docs/control-map.md` §7, `docs/research-process.md`, `docs/run-bundle.md`,
  and `tests/README.md` (directory map, owner table paths, single-file command
  examples). Verify: `check_doc_hygiene.py` exits 0 and a repo-wide grep finds
  no `tests/unit/test_` path that lacks an owner segment.

## 4. Planted 红证与双 lane

- [x] 4.1 Planted failure: create `tests/integration/__init__.py`, run the
  guard, verify it goes RED naming the integration package marker; delete the
  planted file, verify the guard returns green (capture both outputs).
- [x] 4.2 Run both owed lanes: `make verify` (expect all green including the
  guard) and `make smoke` (expect 9 green — proving integration collection is
  unchanged by the unit regrouping). Direct exit codes only.

## 5. Closeout 证据

- [x] 5.1 Run the full closeout set with directly-read exit codes (governance
  suite, closeout gate, doc hygiene + self-test, architecture, project specs,
  release face, dependency checker, plan gate for this change, make verify,
  make smoke, git diff --check, git diff --exit-code HEAD -- deerflow).
- [x] 5.2 Write the verification receipt: fresh, runner-written, per-check
  argv/cwd/exit/stdout/stderr, HEAD revision, dirty status, per-file digests,
  both red proofs quoted (missing-owner-package red, planted-marker red),
  the before/after ID lists and prefix mapping, UNVERIFIED notes (no local CI
  run). Verify: receipt newer than last edit, every exit matches expectation.
