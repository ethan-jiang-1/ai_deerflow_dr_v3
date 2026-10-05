# Tasks

## 1. 迁移与红证

- [x] 1.1 `git mv` the persistence cluster into `runtime/bundle/`
  (atomic.py, bundle_state.py, bundle_actions.py, journal.py, ledger.py,
  admission.py) and the binding cluster into `runtime/adapters/` (client.py,
  snapshot_middleware.py, subagent_posture.py, contracts/); create both
  `__init__.py` files with one-line responsibility docstrings; update
  `runtime/__init__.py` docstring to route the six responsibilities. Do NOT fix
  imports yet. Verify: run
  `PYTHONPATH=src python3 -m unittest tests.unit.test_run_engine -v` and capture
  the ImportError red output (the seam proof), quoting the failing module path.

## 2. Import cutover

- [x] 2.1 Fix intra-cluster relative depths in the moved files
  (`..domain`/`..engine` → `...domain`/`...engine` in bundle/ six and adapters/
  client/subagent_posture; cluster-internal `.atomic`/`.contracts`/
  `.snapshot_middleware` references stay unchanged). Verify:
  `grep -n "from \.\.domain\|from \.\.engine" runtime/bundle/*.py runtime/adapters/*.py`
  returns nothing (all are three-dot now).
- [x] 2.2 Cutover external consumers: `runtime/run_engine.py` (bundle_state,
  journal, lazy admission), `runtime/entry.py` (bundle_state, client),
  `runtime/interaction/cli.py` (bundle_actions, bundle_state, lazy admission
  full path), the 9 unit test files, `tests/contract/test_wiring_mirror.py`,
  `tests/integration/test_wiring_smoke.py`, `tools/record_stream.py`. Verify:
  repo-wide grep for old paths
  (`runtime.bundle_state`, `runtime.bundle_actions`, `runtime.journal`,
  `runtime.admission`, `runtime.ledger`, `runtime.atomic`,
  `runtime.client`, `runtime.contracts`, `runtime.snapshot_middleware`,
  `runtime.subagent_posture` without `bundle.`/`adapters.` prefix) returns zero
  source hits outside `openspec/changes/`.

## 3. 登记与文档

- [x] 3.1 Update `openspec/governance/required-paths.toml`: deerflow-wiring group
  paths for client/snapshot_middleware/contracts gain the `adapters/` segment;
  repo-skeleton gains `runtime/bundle/__init__.py` and
  `runtime/adapters/__init__.py` next to `runtime/__init__.py`. Verify:
  `python3 openspec/governance/check_project_architecture.py` exits 0.
- [x] 3.2 Update `deep_research_harness/docs/control-map.md` (§4 steps and §7
  routing rows) and `docs/research-process.md` module links for the ten moved
  modules. Verify: `python3 openspec/governance/check_doc_hygiene.py` exits 0
  (links resolve) and every moved-module link resolves on disk.

## 4. 全量门禁（双 lane）

- [x] 4.1 Capture the after test ID list
  (`PYTHONPATH=src python3 -m unittest discover -s tests -v`), diff against the
  captured before list, and verify ZERO difference (no ID added, removed, or
  renamed); run `make verify` (expect 125 green). Verify: diff output is empty
  and verify exits 0.
- [x] 4.2 Run `make smoke` (integration lane owed: interaction/** and entry.py
  surfaces touched). Verify: exits 0, 9 tests, none skipped unexpectedly.

## 5. Closeout 证据

- [x] 5.1 Run the full closeout set with directly-read exit codes: governance
  unittest suite, closeout gate, doc hygiene (+ self-test), architecture,
  project specs, release face, dependency checker, plan gate for this change,
  `make verify`, `make smoke`, `git diff --check`,
  `git diff --exit-code HEAD -- deerflow`. All recorded exits match expectation.
- [x] 5.2 Write the verification receipt: fresh, runner-written, argv/cwd/exit/
  stdout/stderr per check, HEAD revision, dirty status, per-file digests of all
  touched surfaces, the task-1.1 ImportError red quoted, the before/after test
  ID lists attached (or their equality asserted), UNVERIFIED notes (no local CI
  run). Verify: receipt newer than last edit, every exit matches expectation.
