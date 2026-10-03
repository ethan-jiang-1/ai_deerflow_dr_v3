"""Admission closed vocabularies shared by engine and runtime.

Pure stdlib. The artifact kinds a submission may declare; anything outside the set is
rejected at the boundary.

@impl RUA-001"""

from __future__ import annotations

ARTIFACT_KINDS: tuple[str, ...] = ("evidence", "final_report")
