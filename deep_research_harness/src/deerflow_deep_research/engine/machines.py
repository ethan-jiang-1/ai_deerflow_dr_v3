"""The declared quality machines (RT10): the code-backed source of the register.

Pure stdlib. This list is what `docs/quality-register.md` must name — a unit test
fails on drift, so the register cannot silently rot. Adding or removing a machine is
an owning-change decision, never an edit in passing.

@impl RUA-001"""

from __future__ import annotations

# (machine name as it must appear in the register, the invariant it guarantees)
DECLARED_MACHINES: tuple[tuple[str, str], ...] = (
    ("validator", "No artifact content enters the bundle without a rendered verdict; "
     "rejections carry closed result codes and reasons."),
    ("gate", "A phase renders exactly pass or blocked, derived purely from declared "
     "requirements versus admitted facts; blocked names the unmet."),
    ("ledger-chain-verification", "evidence/submissions.jsonl is a sha256 hash chain: "
     "any field edit, insertion, or deletion fails the read at the first broken link."),
    ("application-unit-gate", "make verify runs the stdlib unittest suite and exits "
     "non-zero on any failure; it never links OpenSpec content."),
    ("repository-governance-gates", "The aggregate closeout gate and its component "
     "checkers (structure, requirements, specs, guidance, dependency direction) pass "
     "with exit code 0 before any change archives."),
)
