# Design

## Context

The unit gate is stdlib unittest discovery over tests/unit; the integration lane is a
separate discovery (`tests/integration`) run by make smoke only. The framework imports
in the integration lane legitimately touch no network either (scripted providers), but
the lane is the designated opt-in surface — the guard's boundary is the unit lane.

## Decisions

1. The guard wraps socket.socket for tests/unit only: activated in
   `tests/unit/__init__.py` (per-lane activation, no global patching), restored after
   the discovery run via atexit hooks so the integration lane is unaffected.
2. The violation names the attempting test and the blocked call — loud, diagnosable.
3. The negative control lives in tests/unit (it is the guard's own proof), marked as
   the deliberate violator via an env-var opt-out so it can demonstrate red without
   breaking the suite: the control test asserts the guard raises when a connection is
   attempted directly through the guarded path.

## Alternatives

A conftest autouse fixture (pytest) — rejected: the gate lane is stdlib unittest;
a pytest fixture would not fire there. DNS-level blocking — rejected: out of scope
for a stdlib guard.

## Risks / Trade-offs

[Legitimate localhost use (e.g. a test server) in the unit lane] — none today; if one
arrives, the guard gains an explicit allowlist entry via an owning change.
[The guard patch leaks into other lanes] — restored at discovery teardown; the
integration lane's own run path is untouched (verified by the smoke staying green).

## Migration Plan

Guard + negative control + limitation row; verify/smoke green; receipts; archive;
commit.

## Open Questions

(none)
