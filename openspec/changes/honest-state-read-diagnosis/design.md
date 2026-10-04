# Design

## Context

The diagnosis (delivered with the change request) established, with a negative
control (2984 concurrent atomic writes → zero missing-shaped failures) and a positive
attribution experiment (directory rename round-trip → the exact "missing"
signature while the file never moved), that:

- the state write path (`atomic.atomic_write_text`) has no read window;
- no in-app code deletes a published state.json;
- `Path.is_file()` reports False only for the ENOENT family, so "FS pressure" cannot
  produce the signature;
- the incident bundle's state.json persisted through the incident window.

Requirement-ID tracking is retired (`1ee535a`); the delta carries no `> req:` header.

## Goals / Non-Goals

**Goals:** classify the two absence shapes at read time; carry crash-scene evidence
(phase, errno, `.tmp-*` siblings) in the file-level report; fold the bare
`FileNotFoundError` escape into the same classification; rewrite the
known-limitations entry to the diagnosed truth with UNVERIFIED bounds.

**Non-Goals:** no write-path change; no retry/repair of external interference; no
crash-transfer behavior change; no reproduction of the 1GB full-mode incident (the
environment cannot be reconstructed — recorded as UNVERIFIED, not silently dropped).

## Decisions

1. **Directory-absent → `BundleUnavailable`.** A transiently invisible directory is
   indistinguishable from deletion, and deletion is already declared permanent with
   no recovery path — reusing that signal avoids inventing a third state. Callers
   that could read before get the same type they would see for a deleted bundle.
2. **File-absent-with-directory-present → `StateCorruption` with evidence.** The
   directory existing while the file vanishes is genuine state damage (external
   unlink) — corruption semantics stay, and the message gains the failure phase and
   the `.tmp-*` sibling listing as crash-scene evidence.
3. **The read-window `FileNotFoundError` joins the same classifier.** The window
   between the existence check and the read is re-tested against the directory, so a
   directory-level event during the window gets the same honest classification
   instead of escaping bare.
4. **Negative control locks the write-path guarantee.** A concurrent
   writer/reader unit test asserts zero missing-shaped failures across atomic
   replacements — the experiment that overturned the FS-pressure hypothesis becomes
   a permanent regression test.

## Risks / Trade-offs

- [Callers that matched the old "missing" message could mis-route] → no caller or
  test matched it (verified by grep); the classification is a strictly more precise
  contract.
- [`BundleUnavailable` for a transient condition reads as permanent] → it is the
  honest reading: the CLI already documents absence as permanent with no recovery;
  transient external interference is not detectable as different from deletion at
  read time.
- [The concurrent negative control is timing-based] → it asserts only the absence of
  missing-shaped failures (the atomicity guarantee), never the presence of conflicts;
  conflicts are legal and allowed to appear or not.

## Migration Plan

Red-first unit tests (rename experiment, external unlink, concurrent negative
control) → classification implementation → known-limitations rewrite → full gate.
Rollback: revert the commit; no persisted-format or CLI surface change.

## Open Questions

None. The UNVERIFIED items (which external process touched `scopes/`; the masked
original gen-7 exception) are recorded as bounds in the known-limitations rewrite,
not as open questions of this change.
