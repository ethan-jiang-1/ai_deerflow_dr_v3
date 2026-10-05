"""Admission actions: submit_artifact composes the validator hold point with the ledger.

Pure stdlib. The engine renders verdicts; this module selects the disposition from the
verdict plus ledger facts, places admitted content, commits the chain entry, and
journals every disposition under the `validation` category.

@impl RUA-001"""

from __future__ import annotations

from datetime import datetime, timezone

from ...domain.journal_policy import JournalEntry
from ...engine.validator import ArtifactSubmission, AdmissionContext, validate
from . import atomic
from .bundle_state import BundleHandle
from .journal import append_entry
from .ledger import (  # noqa: F401 — re-exported for the admission call site
    LedgerEntry,
    LedgerTampered,
    VerdictContradiction,
    VerdictlessCommit,
    commit_entry,
    read_ledger,
)

__all__ = [
    "submit_artifact",
    "read_admitted_counts",
    "LedgerEntry",
    "LedgerTampered",
    "VerdictContradiction",
    "VerdictlessCommit",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_context(handle: BundleHandle) -> AdmissionContext:
    admitted: set[str] = set()
    rejected: dict[str, int] = {}
    for entry in read_ledger(handle):
        if entry.disposition == "admit":
            admitted.add(entry.content_hash)
        elif entry.disposition == "reject":
            rejected[entry.content_hash] = entry.seq
    return AdmissionContext(admitted_hashes=frozenset(admitted), rejected_hashes=rejected)


def submit_artifact(handle: BundleHandle, submission: ArtifactSubmission) -> LedgerEntry:
    """The hold point: validate first, then materialize the rendered verdict.

    `reject` places nothing; `admit` places the content and records it; `replay`
    records rework of previously rejected content that now validates. Every
    disposition is journaled under the `validation` category."""

    context = _build_context(handle)
    verdict = validate(submission, context)
    # RUB-001's directory contract: final reports route to final/; everything else evidence/.
    placement = f"final/{submission.filename}" if submission.kind == "final_report" else f"evidence/{submission.kind}/{submission.filename}"
    if verdict.result_code != "ok":
        disposition, artifact_path, replay_of = "reject", "", None
    elif verdict.content_hash in context.rejected_hashes:
        disposition = "replay"
        artifact_path = placement
        replay_of = context.rejected_hashes[verdict.content_hash]
    else:
        disposition, artifact_path, replay_of = "admit", placement, None

    if disposition in {"admit", "replay"}:
        atomic.atomic_write_bytes(handle.root / artifact_path, submission.content)

    entry = LedgerEntry(
        seq=0,
        timestamp=_now_iso(),
        disposition=disposition,
        kind=submission.kind,
        filename=submission.filename,
        artifact_path=artifact_path,
        content_hash=verdict.content_hash,
        result_code=verdict.result_code,
        reasons=verdict.reasons,
        replay_of=replay_of,
        prev_hash="",
        entry_hash="",
    )
    committed = commit_entry(handle, entry, verdict=verdict)
    append_entry(
        handle,
        JournalEntry(
            timestamp=_now_iso(),
            category="validation",
            event="disposition_recorded",
            detail={
                "disposition": committed.disposition,
                "result_code": committed.result_code,
                "kind": committed.kind,
                "seq": committed.seq,
            },
        ),
    )
    return committed


def read_admitted_counts(handle: BundleHandle) -> dict[str, int]:
    """Admitted artifact counts by kind — the gate's admitted-facts input."""

    counts: dict[str, int] = {}
    for entry in read_ledger(handle):
        if entry.disposition == "admit":
            counts[entry.kind] = counts.get(entry.kind, 0) + 1
    return counts
