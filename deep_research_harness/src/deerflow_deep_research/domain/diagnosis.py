"""Diagnosis classifier: one typed diagnosis over the bundle's persisted facts.

A projection for the operator, not a second state authority: ``classify``
consumes the typed state, the journal entries, an owner-liveness fact, and the
diagnostics presence table, and returns which declared class the run's terminal
outcome belongs to, the chain stage that owns the failing condition, and the
concrete evidence files. Pure and framework-free — the verb layer owns all I/O.

@impl DIAG-001"""

from __future__ import annotations

from dataclasses import dataclass

from .bundle import (
    CHECKPOINT_FILENAME,
    JOURNAL_RELATIVE,
    STATE_FILENAME,
    UNANSWERED_QUESTIONS_RELATIVE,
)
from .journal_policy import JournalEntry
from .state_machine import BundleState

SNAPSHOT_RELPATH = "diagnostics/assembly-snapshot.json"
FINAL_RELPATH = "final/"

# The closed diagnosis set. `running` and `delivered` are honest non-failure
# outcomes; `ambiguous` refuses to guess when distinct terminal events collide.
DIAGNOSIS_CLASSES = (
    "model_call_failed",
    "framework_crash",
    "framework_stopped",
    "clarification_exhausted",
    "cancelled",
    "owner_died",
    "completed_undelivered",
    "delivered",
    "running",
    "ambiguous",
)

_FAIL_RESUME_CLARIFICATION_REASON = "clarification bound exhausted"


@dataclass(frozen=True)
class DiagnosticsPresence:
    """Which diagnostics artifacts exist (verb layer probes the filesystem)."""

    assembly_snapshot: bool = False
    unanswered_clarifications: bool = False
    checkpoint: bool = False
    final_report: bool = False


@dataclass(frozen=True)
class Diagnosis:
    klass: str
    stage: str
    evidence: tuple[str, ...]
    detail: str


def _terminal_events(entries: list[JournalEntry]) -> list[JournalEntry]:
    return [e for e in entries if e.category == "terminal"]


def _exhausted(entries: list[JournalEntry]) -> bool:
    return any(
        e.category == "exhaustion" and e.event == "clarification_bound_exhausted"
        for e in entries
    )


def classify(
    state: BundleState,
    entries: list[JournalEntry],
    *,
    owner_alive: bool,
    diagnostics: DiagnosticsPresence,
) -> Diagnosis:
    """Classify the run's terminal outcome. See module docstring for authority."""

    terminal = _terminal_events(entries)
    distinct_events = sorted({e.event for e in terminal})
    if len(distinct_events) > 1:
        return Diagnosis(
            klass="ambiguous",
            stage="journal — contradicting terminal events",
            evidence=(str(JOURNAL_RELATIVE),),
            detail=f"distinct terminal events present: {distinct_events}; refusing to guess",
        )

    evidence: list[str] = [str(JOURNAL_RELATIVE)]

    if distinct_events == ["run_completed"]:
        if state.delivery == "admitted":
            pointers = [f"{FINAL_RELPATH} (admitted report)"] if diagnostics.final_report else []
            return Diagnosis(
                klass="delivered", stage="admission — report admitted",
                evidence=tuple(pointers), detail=f"generation {state.generation} delivered",
            )
        pointers = list(evidence)
        if diagnostics.final_report:
            pointers.append(f"{FINAL_RELPATH} (belt: file exists, state delivery={state.delivery!r})")
        return Diagnosis(
            klass="completed_undelivered",
            stage="admission — validator/gate did not record an admitted delivery",
            evidence=tuple(pointers),
            detail=f"completed but delivery is {state.delivery!r}",
        )
    if distinct_events == ["run_cancelled"]:
        return Diagnosis(
            klass="cancelled", stage="operator decision — cancellation recorded",
            evidence=(str(JOURNAL_RELATIVE), str(STATE_FILENAME)),
            detail=f"generation {state.generation} cancelled by request",
        )
    if distinct_events == ["llm_error_fallback"]:
        error_type = next(
            (str(e.detail.get("error_type")) for e in terminal if e.detail.get("error_type")),
            "unknown",
        )
        pointers = list(evidence)
        if diagnostics.assembly_snapshot:
            pointers.append(SNAPSHOT_RELPATH)
        return Diagnosis(
            klass="model_call_failed",
            stage="binding — DeerFlow model call (framework error-fallback)",
            evidence=tuple(pointers),
            detail=f"model call failed (error_type: {error_type})",
        )
    if distinct_events == ["framework_error"]:
        error_name = next(
            (str(e.detail.get("error")) for e in terminal if e.detail.get("error")),
            "unknown",
        )
        pointers = list(evidence)
        if diagnostics.checkpoint:
            pointers.append(CHECKPOINT_FILENAME)
        return Diagnosis(
            klass="framework_crash",
            stage="host runtime — DeerFlow raised through the stream",
            evidence=tuple(pointers),
            detail=f"framework exception: {error_name}",
        )
    if distinct_events == ["stop_reason"]:
        reason = next(
            (str(e.detail.get("reason")) for e in terminal if e.detail.get("reason")),
            "unknown",
        )
        return Diagnosis(
            klass="framework_stopped",
            stage="host runtime — DeerFlow reported a stop reason",
            evidence=(str(JOURNAL_RELATIVE),),
            detail=f"framework stop reason: {reason}",
        )
    if distinct_events == ["crash_detected"]:
        return Diagnosis(
            klass="owner_died",
            stage="run pump process — owner died (transferred by a status observation)",
            evidence=(str(JOURNAL_RELATIVE), str(STATE_FILENAME)),
            detail=f"crash transfer recorded for thread {state.thread_id}",
        )
    if distinct_events == ["run_failed_resume"]:
        if _exhausted(entries) or state.status == "failed-resume":
            pointers = list(evidence)
            if diagnostics.unanswered_clarifications:
                pointers.append(str(UNANSWERED_QUESTIONS_RELATIVE))
            return Diagnosis(
                klass="clarification_exhausted",
                stage="interaction — clarification bound exhausted",
                evidence=tuple(pointers),
                detail=f"auto-continuation bound {state.auto_proceed_bound} exhausted",
            )
        return Diagnosis(
            klass="ambiguous",
            stage="journal — run_failed_resume without a recognized reason",
            evidence=(str(JOURNAL_RELATIVE),),
            detail="terminal event carries no recognized failure reason",
        )

    # No terminal journal event: the passive owner-death transfer, or a live run.
    if state.status == "active":
        if not owner_alive:
            return Diagnosis(
                klass="owner_died",
                stage="run pump process — owner died before a terminal entry",
                evidence=(str(STATE_FILENAME),),
                detail=f"state active but owner PID {state.owner_pid} is gone "
                       f"(thread {state.thread_id})",
            )
        return Diagnosis(
            klass="running", stage="run pump process — still active",
            evidence=(), detail=f"generation {state.generation} is still running",
        )

    # Terminal state per state.json without a terminal journal event: honest,
    # pre-journal or torn history — report what state knows, never invent.
    return Diagnosis(
        klass="ambiguous",
        stage="journal — terminal state has no terminal event",
        evidence=(str(JOURNAL_RELATIVE), str(STATE_FILENAME)),
        detail=f"state is {state.status!r} but the journal has no terminal event",
    )
