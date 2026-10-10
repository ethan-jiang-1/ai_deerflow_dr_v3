"""Admission verdict vocabularies and typed verdicts.

Pure stdlib. Small closed sets start here (v2's vocabulary-explosion lesson): the
result codes, the dispositions, the phase verdicts, and the typed verdicts that flow
from engine policy into runtime materialization.

@impl RUA-001"""

from __future__ import annotations

from dataclasses import dataclass, field

RESULT_CODES: tuple[str, ...] = (
    "ok",
    "schema_malformed",
    "missing_provenance",
    "empty_content",
    "duplicate_content",
    "report_structure_violation",
)

DISPOSITIONS: tuple[str, ...] = ("admit", "reject", "replay")

PHASE_VERDICTS: tuple[str, ...] = ("pass", "blocked")


@dataclass(frozen=True)
class ValidatorVerdict:
    """The engine's rendered decision for one submission. Runtime materializes it;
    it never edits it."""

    result_code: str
    reasons: tuple[str, ...] = field(default=())
    content_hash: str = ""

    def validate(self) -> ValidatorVerdict:
        if self.result_code not in RESULT_CODES:
            raise ValueError(
                f"result code {self.result_code!r} is outside the closed set {RESULT_CODES}"
            )
        return self


@dataclass(frozen=True)
class GateVerdict:
    phase_verdict: str
    unmet: tuple[str, ...] = field(default=())

    def validate(self) -> GateVerdict:
        if self.phase_verdict not in PHASE_VERDICTS:
            raise ValueError(
                f"phase verdict {self.phase_verdict!r} is outside the closed set {PHASE_VERDICTS}"
            )
        if self.phase_verdict == "pass" and self.unmet:
            raise ValueError("a passing gate cannot name unmet requirements")
        return self
