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
    ("subagent-posture-guard", "Checked-in configurations declare no custom subagent "
     "types, and any future declaration must exclude 'task' from its "
     "disallowed_tools (the depth self-check fails closed naming the config, the "
     "offender, and the remedy)."),
    ("command-surface-guard", "COMMANDS.md, the Makefile targets, and the cli.py "
     "subcommands stay mutually consistent (docs-as-contract: the documented commands "
     "are the deliverable)."),
    ("source-traceability", "Every http(s) URL in a final report is computably "
     "checkable against the run's own search corpus; the pure verdict proves record "
     "support, never that a record is true, and cannot pass on an empty corpus."),
    ("behavior-profile", "A real run's journal derives a pure observational profile "
     "(tool selection, event composition, wall-clock span) checked against declared "
     "expectations with named violations; it observes and never admits — no "
     "admission codes, no gate consumer — and asserts no token dimension (the "
     "journal carries none)."),
    ("application-unit-gate", "make verify runs the stdlib unittest suite and exits "
     "non-zero on any failure; it never links OpenSpec content."),
    ("repository-governance-gates", "The aggregate closeout gate and its component "
     "checkers (structure, requirements, specs, guidance, dependency direction) pass "
     "with exit code 0 before any change archives."),
)
