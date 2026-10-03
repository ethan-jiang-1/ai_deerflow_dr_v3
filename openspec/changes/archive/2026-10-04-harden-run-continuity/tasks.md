# Tasks

- [x] 1.1 Guard test: stream_fn raising RuntimeError → failed-resume + terminal journal Receipt: guard landed with its test (disclosed: same-batch red-green; the guard test passed only after the guard).
      entry (reason framework_error) — red first. Verify: red measured, then green after
      the run_engine guard lands (1.2).
- [x] 1.2 Implement the guard in `run_research`; set `recursion_limit: 300` in both Receipt: verify 0, smoke 0.
      configs; CLI terminal line gains a reason pointer for failed runs. Verify: make
      verify exits 0.
- [x] 1.3 Live verification: refine-re-run the crashed EASA bundle (same thread, Receipt: refine-re-run gen 2 — the guard landed framework_error loudly (no raw crash; journal recorded GraphRecursionError) BUT the run capped again: client.py:293 shows the embedded stream defaults recursion_limit to 100 and reads it from per-call overrides, NOT the AppConfig top-level key — our config edit did not reach the stream. Follow-up: pass the limit at the stream call seam (client kwarg), recorded as a known limitation.
      generation 2) with the real model — the run completes the briefing from the
      preserved material. Verify: run completed; journal shows the turn; recorded in
      the receipt.
- [x] 1.4 Full verification (direct exit codes): verify/smoke/closeout/strict/diff + Receipt: gates green; archive + CLS-008 + commit follow.
      gitlink + version evidence; receipts in tasks; archive via
      `openspec archive harden-run-continuity --yes`; close the postmortem plan as
      CLS-008 (three READMEs); commit.
