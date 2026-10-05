# Tasks

## 1. 红先行（全部测试先落盘）

- [x] 1.1 Create `tests/unit/interaction/test_refine_foreground.py`: (a) a wiring
  test patching `entrypoint.run_foreground` (record calls) and stubbing
  `bundle_actions.refine`/`resolve_bundle` — assert cmd_refine drives the
  foreground chain once with config_name mapped from the refined composition and
  thread_id from the refined state, and prints a terminal line; (b) a
  table-driven test for `entry.config_name_for_composition` (fixture→fixture,
  all_real→base, mixed/unknown→loud error naming the value). Verify: both FAIL
  red for the expected reasons (run_foreground not called; function absent) —
  capture for the receipt.
- [x] 1.2 Extend `tests/unit/runtime/test_run_engine.py`: a generation-2 handle
  (problem.txt + refine-2.txt both present) whose scripted stream records the
  message it receives — assert the first stream call carries the refine-2
  direction text, not the problem text. Verify: FAILS red (current code sends
  problem.txt). Also extend `tests/unit/runtime/test_bundle_runtime.py`: refine
  on a terminal bundle sets `owner_pid == os.getpid()` and journals "refined".
  Verify: the owner assertion FAILS red (current code inherits the old pid).
- [x] 1.3 Extend the journey test (`tests/integration/test_cli_journey.py`):
  `_cli` gains an optional env-merge parameter; the refine call injects a
  distinct `DEERFLOW_FAKE_SCRIPT` answer; assertions become returncode 0 +
  generation-2 started line + `state: completed` + `final/report-gen2.md`
  exists + admitted counts include the gen-2 report. Verify: `make smoke` FAILS
  red at the refine step (current behavior prints `state: active`) — capture
  for the receipt.

## 2. 实现（四点）

- [x] 2.1 `run_engine.run_research`: select the first message by
  `state.generation` (1 → `request/problem.txt`; >1 →
  `request/refine-{generation}.txt` via the domain bundle path helper; a missing
  file fails loudly with its path). Verify: the 1.2 message test turns green and
  the existing generation-1 tests stay green.
- [x] 2.2 `bundle_actions.refine`: set `owner_pid=os.getpid()` on the refined
  state before writing (action-layer pattern, matching `start`). Verify: the 1.2
  owner test turns green; existing refine tests stay green.
- [x] 2.3 `entry.py`: add `config_name_for_composition` with the loud
  mixed/unknown error. Verify: the 1.1 table test turns green.
- [x] 2.4 `interaction/cli.py cmd_refine`: after refine, print the started line,
  drive `entrypoint.run_foreground` (config_name from the composition mapping,
  thread_id from the refined state, pin, live renderer), map ImportError to the
  same remedy wording shape as create (naming refine), print terminal + state
  lines. Verify: the 1.1 wiring test turns green; `make verify` fully green.

## 3. 双 lane 全绿

- [x] 3.1 Run `make verify` (all unit + contract green) and `make smoke`
  (journey green incl. the new refine-completion assertions and report-gen2
  admit). Direct exit codes only; capture the smoke output showing the
  previously-red step now green.

## 4. 文档与 spec 同轮

- [x] 4.1 Update docs: `COMMANDS.md` (refine line: 创建并前台跑完该代，延续
  composition 梯), `docs/control-map.md` (verb-table refine row; REMOVE the
  "refine 自动重跑" entry from the not-implemented list), `docs/run-bundle.md`
  (lifecycle refine line), `playbook/run-research.md` (two refine mentions),
  `tests/README.md` (journey description row + the "未覆盖" line: refine 再执行
  至完成 is now covered). Verify: repo-wide grep finds no stale "refine 不自动
  执行 / 只创建下一代" claim outside the change dir; `check_doc_hygiene.py`
  exits 0.

## 5. Closeout 证据

- [x] 5.1 Run the full closeout set with directly-read exit codes (governance
  suite, closeout gate, doc hygiene + self-test, architecture, project specs,
  release face, dependency checker, plan gate for this change, make verify,
  make smoke, git diff --check, git diff --exit-code HEAD -- deerflow).
- [x] 5.2 Write the fresh verification receipt (argv/cwd/exit/stdout/stderr,
  HEAD revision, dirty status, per-file digests, all red outputs quoted
  (unit×3 groups + smoke journey red), UNVERIFIED notes incl. no real-ladder
  refine run). Verify: receipt newer than last edit, every exit matches
  expectation.
