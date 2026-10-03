"""The admission validator: the bundle's hold point, as pure ordered rules.

Pure stdlib. Every proposed artifact is rendered a verdict before anything is placed;
rejections carry the result code plus human-readable reasons, and nothing is repaired
silently. The runtime layer materializes verdicts; it never renders them.

@impl RUA-001"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import PurePosixPath

from ..domain.admission import ARTIFACT_KINDS
from .verdicts import ValidatorVerdict


@dataclass(frozen=True)
class ArtifactSubmission:
    kind: str
    filename: str
    content: bytes
    provenance: dict


@dataclass(frozen=True)
class AdmissionContext:
    """Ledger facts as of the submission: which content hashes are already admitted,
    and which were rejected (hash -> rejecting entry sequence)."""

    admitted_hashes: frozenset[str]
    rejected_hashes: dict[str, int]


def _content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _filename_is_safe(filename: str) -> bool:
    if not filename or filename in {".", ".."}:
        return False
    if "/" in filename or "\\" in filename or "\x00" in filename:
        return False
    return PurePosixPath(filename).name == filename


def validate(submission: ArtifactSubmission, context: AdmissionContext) -> ValidatorVerdict:
    """Ordered closed rules: first failure wins; every verdict carries the content
    hash (rejections included — the replay discipline matches against them)."""

    digest = _content_hash(submission.content)

    def verdict(code: str, *reasons: str) -> ValidatorVerdict:
        return ValidatorVerdict(result_code=code, reasons=reasons, content_hash=digest).validate()

    if submission.kind not in ARTIFACT_KINDS:
        return verdict(
            "schema_malformed",
            f"artifact kind {submission.kind!r} is outside the closed set {ARTIFACT_KINDS}",
        )
    if not _filename_is_safe(submission.filename):
        return verdict(
            "schema_malformed",
            f"filename {submission.filename!r} is not a safe single path segment",
        )
    producer = submission.provenance.get("producer") if isinstance(submission.provenance, dict) else None
    if not isinstance(producer, str) or not producer.strip():
        return verdict(
            "missing_provenance",
            "provenance must name a non-empty 'producer' (models propose, code disposes — "
            "the proposal must say who proposed it)",
        )
    if not submission.content:
        return verdict("empty_content", "artifact content is empty")
    if digest in context.admitted_hashes:
        return verdict(
            "duplicate_content",
            f"content hash {digest} is already admitted — duplicates are never silent "
            "overwrites",
        )
    return ValidatorVerdict(result_code="ok", reasons=(), content_hash=digest).validate()
