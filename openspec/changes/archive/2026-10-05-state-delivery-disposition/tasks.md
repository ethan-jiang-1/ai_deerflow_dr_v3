# Tasks

## 1. 红先行

- [x] 1.1 Domain red tests (extend `tests/unit/domain/test_bundle_domain.py`):
  construct states with `delivery="admitted"`/`"rejected"`/`"no-answer"`/None and
  assert validate passes and to_dict/from_dict roundtrips; assert validate rejects
  `delivery="bogus"`, `admitted` without artifact, and `rejected` WITH an artifact.
  Verify: FAILS red (the field does not exist — TypeError/AttributeError) — capture.
- [x] 1.2 Run-engine red tests (extend `tests/unit/runtime/test_run_engine.py`):
  (a) clean completion → reread state has `delivery="admitted"` and
  `delivery_artifact="final/report-genN.md"`; (b) an empty-answer completion →
  `delivery="no-answer"`; (c) refine with a duplicate final answer (identical text to
  generation 1's admitted report) → `delivery="rejected"` while status stays
  completed and refine-after-rejected remains legal. Verify: all three FAIL red
  (delivery never written) — capture.
- [x] 1.3 Status line red (new `tests/unit/interaction/test_status_delivery.py`):
  patch pattern like test_refine_foreground — cmd_status with a fake state carrying
  each delivery value asserts the printed `delivery:` line, including
  `(not recorded)` for None. Verify: FAILS red (no delivery line printed).
- [x] 1.4 Journey red (extend `tests/integration/test_cli_journey.py`): after the
  create status call assert `delivery: admitted (final/report-gen1.md)`; after the
  refined generation assert `delivery: admitted (final/report-gen2.md)`. Run
  `make smoke` and verify the journey FAILS red at the delivery assertion — capture.

## 2. 实现

- [x] 2.1 `domain/state_machine.py`: add `delivery` and `delivery_artifact` optional
  fields, validate rules (closed set; admitted ⇔ artifact non-empty), from_dict
  `.get()` tolerance, to_dict always writes both keys. Verify: 1.1 turns green;
  the backward-compat lock (strip the keys from a written state.json → read_state
  returns delivery None) passes.
- [x] 2.2 `runtime/run_engine.py` `_submit_final_report`: return the delivery
  outcome (disposition mapping admit/replay → admitted, reject → rejected, empty →
  no-answer, plus artifact path); the completion path then rereads state and writes
  the enrichment via the existing CAS `write_state` (status unchanged, revision +1).
  Verify: 1.2's three tests turn green.
- [x] 2.3 `runtime/interaction/cli.py cmd_status`: print the `delivery:` line
  composing status and delivery (admitted includes the artifact path; None renders
  `(not recorded)`). Verify: 1.3 turns green; `make verify` fully green.

## 3. 双 lane 全绿

- [x] 3.1 Run `make verify` (all green) and `make smoke` (journey green incl. both
  delivery assertions). Direct exit codes; capture the previously-red steps green.

## 4. spec 与文档同轮

- [x] 4.1 Sync docs: `docs/run-bundle.md` (state.json row gains the delivery fact;
  the 状态≠交付≠质量 section becomes two-checks-from-state + file belt),
  `docs/research-process.md` (判断完成 paragraph names state.delivery as the
  primary answer), `tests/README.md` (journey description row). Verify: hygiene
  exits 0 and no doc still claims state cannot answer delivery.

## 5. Closeout 证据

- [x] 5.1 Full closeout set with directly-read exit codes (governance suite, closeout
  gate, doc hygiene + self-test, architecture, project specs, release face,
  dependency checker, plan gate for this change, make verify, make smoke,
  git diff --check, git diff --exit-code HEAD -- deerflow).
- [x] 5.2 Fresh verification receipt (argv/cwd/exit/stdout/stderr, HEAD revision,
  dirty status, per-file digests, all red outputs quoted, UNVERIFIED notes incl.
  no real-ladder run). Verify: receipt newer than last edit, every exit matches.
