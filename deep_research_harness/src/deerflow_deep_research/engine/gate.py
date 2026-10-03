"""The admission gate: minimal pass/blocked derivation over declared requirements.

Pure stdlib. Requirements are declared pairs (closed artifact kind, minimum admitted
count); the derivation renders `pass` only when admitted facts cover every requirement,
and `blocked` naming exactly the unmet ones. No repair-budget mechanism exists.

@impl RUA-001"""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.admission import ARTIFACT_KINDS
from .verdicts import GateVerdict


@dataclass(frozen=True)
class GateRequirement:
    kind: str
    minimum: int

    def validate(self) -> "GateRequirement":
        if self.kind not in ARTIFACT_KINDS:
            raise ValueError(
                f"gate requirement kind {self.kind!r} is outside the closed set {ARTIFACT_KINDS}"
            )
        if self.minimum < 1:
            raise ValueError(f"gate requirement minimum must be >= 1, got {self.minimum}")
        return self


def derive_gate(
    requirements: tuple[GateRequirement, ...],
    admitted_counts: dict[str, int],
) -> GateVerdict:
    unmet: list[str] = []
    for requirement in requirements:
        requirement.validate()
        if admitted_counts.get(requirement.kind, 0) < requirement.minimum:
            unmet.append(requirement.kind)
    phase_verdict = "blocked" if unmet else "pass"
    return GateVerdict(phase_verdict=phase_verdict, unmet=tuple(unmet)).validate()
