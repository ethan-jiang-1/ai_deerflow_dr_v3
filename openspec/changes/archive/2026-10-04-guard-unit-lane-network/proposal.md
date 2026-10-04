# Proposal

## Why

The digest's own gap analysis names the sharpest residual risk of offline-first testing: marker selection prevents "live-marked tests accidentally running", but nothing prevents "unmarked test code calling a real API" — one wrong test plus a host key equals accidental billing. v3 has the same exposure in its unit lane. The guard is cheap now and structural forever.

## What Changes

- A socket guard for the unit lane: `tests/unit/` tests run with `socket.socket` disabled (raising on construction/connect), wired via a small helper in the test package's `__init__` path — the integration lane (tests/integration) is exempt by construction (it is not part of the unit discovery).
- A negative control: a deliberately-connecting test placed under tests/unit fails with the guard's violation naming the attempt; the same guard does not fire for the integration lane.
- `known-limitations.md`: the unit-lane network guard noted; the digest gap reference recorded.

## Capabilities

### New Capabilities
(none — test infrastructure; `skip_specs: true`)
### Modified Capabilities
(none)

## Impact

- Modified: `tests/unit/__init__.py` (guard activation for the lane), `tests/integration/__init__.py` (explicit exemption note), a new negative-control test, `docs/known-limitations.md` row. No product code.

## Change Focus

- **Primary module / causal owner:** `tests/unit/` gate — the unit lane structurally cannot touch the network (the digest's self-identified gap #1, closed preemptively here).
- **Seam classification:** deterministic-guardrail — a socket guard over the unit lane; no product behavior.
- **Question:** How does the unit gate structurally forbid network access (so a stray test can never silently spend host credentials), while the integration/smoke lanes remain free?
- **Necessary adjacent/external contracts:** the integration lane's skipUnless guard (answers: which lanes stay network-free vs opt-in); the digest's own gap analysis (answers: the precedent — their conftest-level guard was the missing piece).
- **Evidence seam:** the unit suite green with the guard; the negative control (a deliberately-connecting test inside the unit lane turns red; the same code in tests/integration does not).
- **Not in scope:** gating the integration/smoke lane (they are the opt-in network surface), DNS-level enforcement.
- **Triggered review policies:** change-admission
