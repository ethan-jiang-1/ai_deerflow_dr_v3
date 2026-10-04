# Tasks

## 1. Red-first unit tests

- [x] 1.1 New `tests/unit/test_state_read_diagnosis.py`: (a) build a real bundle via
  `bundle_actions.start` on the fixture ladder, rename the bundle root away, assert
  `read_state` raises the bundle-unavailable signal (red: current code raises
  `StateCorruption "state.json is missing"`); (b) with the directory present, unlink
  `state.json` externally, assert state corruption carrying read evidence
  (phase + `.tmp-*` siblings) — red: current message carries neither; (c) concurrent
  negative control: two writer threads and three reader threads over atomic
  replacements assert zero missing-shaped failures.
- [x] 1.2 Run the unit suite; verify the new tests fail (red) against the current
  `read_state`.

## 2. Classification implementation (green)

- [x] 2.1 Implement the two-shape classifier in `read_state` per design decisions
  1–3 (stat-time and read-time windows both route through it). Verify: the new tests
  turn green; `UV_OFFLINE=1 make verify` exits 0 with the full suite.

## 3. Known-limitations rewrite

- [x] 3.1 Rewrite the state.json entry in `docs/known-limitations.md` to the
  diagnosed truth: atomic write path with no in-app deleter; the incident file
  persisted through the window; directory-level external interference as root cause,
  orthogonal to checkpoint mode; fail-loud fallback worked as designed;
  UNVERIFIED bounds recorded (external process identity; masked original exception).
  Verify: doc-hygiene checker exit 0; no stale "疑似 FS 压力" claim remains.

## 4. Closeout

- [x] 4.1 From the repo root: `python3 openspec/governance/check_project_gate.py
  --phase closeout`; from `deep_research_harness/`: `UV_OFFLINE=1 make verify`; from
  the repo root: `openspec validate honest-state-read-diagnosis --strict`,
  `git diff HEAD --check`. Verify: all exit 0 read directly.
- [x] 4.2 Record scope/submodule evidence (gitlink pointer unchanged at `ceebf97f`,
  nested worktree clean) and the diagnosis provenance (investigation report,
  experiment counts: 2984-write negative control; rename round-trip positive
  attribution) in the change's closing notes.

## Closing notes

- Diagnosis provenance: read-only investigation with fixture-level experiments —
  negative control (2 writers + 3 readers, 2984 atomic replacements, zero
  missing-shaped failures) and positive attribution (directory rename round-trip
  reproduced the exact "missing" signature while the file never moved). Root cause:
  directory-level external interference with the gitignored scopes/ tree; the
  FS-pressure hypothesis is refuted (is_file reports False only for the ENOENT family).
- UNVERIFIED (recorded, not silently dropped): which external process touched scopes/
  during the incident; the original gen-7 exception masked by the fallback's secondary
  read_state failure. Real-hardware reproduction would require a 1GB full-mode rerun
  with fs_usage observation — environment not reconstructable.
- Scope/submodule evidence: gitlink 160000 ceebf97f unchanged, nested worktree clean.
- The count-pinning rule proved itself again during this change: the archive count
  moved 32 -> 33 at this change's own archive and the rule flagged the stale README
  number immediately.
