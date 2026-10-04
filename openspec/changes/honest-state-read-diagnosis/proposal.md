# Proposal: Honest State Read Diagnosis

## Why

A fresh diagnosis (this change's investigation, read-only with fixture-level
experiments) overturned the standing known-limitation "large bundles transiently miss
state.json (suspected FS pressure)". Evidence: the state write path is atomic
(`mkstemp` + fsync + `os.replace` + dir fsync) with no in-app deleter; the incident
bundle's state.json existed continuously through the incident window (mtime and
revision unchanged); `Path.is_file()` only reports False for the ENOENT family, so
"FS pressure" (EIO/ENFILE/ENOSPC) cannot produce the observed signature. A controlled
experiment reproduced the signature exactly by transiently renaming the bundle
directory away — proving the signature comes from directory-level invisibility
(external interference with the gitignored `scopes/` tree), not from the file or the
checkpoint mode. Today `read_state` misreports that directory-level event as
`StateCorruption: state.json is missing`, and a `FileNotFoundError` raised between the
existence check and the read escapes as a bare exception.

## What Changes

- **`read_state` diagnosis honesty** (`runtime/bundle_state.py`, error
  classification only — no write-path change): when the state file is not present at
  stat time, the checker first distinguishes directory-level unavailability — the
  bundle root itself is absent → `BundleUnavailable` (the existing permanent-deletion
  semantics; a transiently invisible directory is indistinguishable from deleted) —
  from genuine file-level corruption → `StateCorruption` enriched with the stat errno
  and the `.tmp-*` sibling listing (crash-scene evidence). A `FileNotFoundError`
  escaping the read is folded into the same directory-vs-file classification instead
  of escaping bare.
- **known-limitations rewritten** to the diagnosis: atomic write path with no
  in-app deleter; the incident file persisted through the window; root cause
  directory-level external interference, orthogonal to checkpoint full/delta; the
  fail-loud fallback worked by design (and its secondary-read failure left the bundle
  recoverable via crash-transfer). UNVERIFIED items recorded: which external process
  touched `scopes/`, and the original gen-7 exception masked by the fallback.
- **No write-path, state-machine, journal, or CLI changes.**

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `run-bundle`: the state-authority requirement's read-failure classification gains a
  scenario — directory-level unavailability is reported as the bundle being
  unavailable, and file-level absence as corruption with evidence; the loud-read /
  no-torn-write guarantee itself is unchanged.

## Impact

- Modified: `deep_research_harness/src/deerflow_deep_research/runtime/bundle_state.py`
  (`read_state` classification only), `deep_research_harness/docs/known-limitations.md`,
  new unit test `tests/unit/test_state_read_diagnosis.py`.
- Not touched: `atomic.py`, `bundle_actions.py`, `run_engine.py`, state machine, CLI,
  checkers, `deerflow/` gitlink (read-only).

## Change Focus

- **Primary module / causal owner:** `runtime/bundle_state.py` — the owner of
  state.json read/write semantics; the fix changes how a read failure is classified,
  not what the write path guarantees.
- **Seam classification:** deterministic-guardrail — error classification over
  filesystem facts; the misclassification was itself demonstrated by a controlled
  experiment.
- **Question:** Can the directory-level-vs-file-level distinction be made observable
  and red-first (the rename experiment as the negative path), without weakening the
  atomic-write guarantee or the permanent-deletion semantics?
- **Necessary adjacent/external contracts:** `run-bundle` capability (answers: the
  loud-read guarantee and permanent-deletion semantics the new classification must
  preserve); `agent-playbook`/`doc-truthfulness` content rules (answers: the
  known-limitations rewrite stays within budget and marker rules).
- **Evidence seam:** red-first unit tests (rename experiment → directory-level
  signal; external unlink → corruption with evidence; concurrent-writer negative
  control → zero missing-shaped failures), full closeout gate, `make verify`.
- **Not in scope:** the write path, crash-transfer behavior, full-mode reproduction
  on real hardware (UNVERIFIED — environment cannot be reconstructed), any checker
  change.
- **Triggered review policies:** change-admission

## Impact on resident budgets

`docs/known-limitations.md` is a docs-layer file (unbudgeted, but scope-registered);
the rewrite is roughly size-neutral and stays within the registered docs scope.
