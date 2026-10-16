"""The terminal outcome vocabulary: one declaration, four consumers.

A run ends by writing one terminal journal entry. That event name used to be a
string protocol spread over four files — the pump that writes it, the diagnosis
classifier that reads it, the watch renderer that prints it, and the CLI's
status-to-event mapping — with no single place declaring which names exist or what
each one means. This module is that place.

`TERMINAL_OUTCOMES` is the declaration; the table below it is what each consumer
reads. Adding an outcome means adding one declaration and, if the classifier needs
bespoke evidence, one branch (the classifier's conditions read diagnostics and
state, which no static row can carry).

@impl RUB-001"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# The declared event names. These are journal vocabulary: a rename is a contract
# change, not a refactor.
# ---------------------------------------------------------------------------
RUN_COMPLETED = "run_completed"
RUN_CANCELLED = "run_cancelled"
RUN_FAILED_RESUME = "run_failed_resume"
LLM_ERROR_FALLBACK = "llm_error_fallback"
FRAMEWORK_ERROR = "framework_error"
RUN_CRASH_DETECTED = "crash_detected"
STOP_REASON = "stop_reason"

TERMINAL_OUTCOMES: tuple[str, ...] = (
    RUN_COMPLETED,
    RUN_CANCELLED,
    RUN_FAILED_RESUME,
    LLM_ERROR_FALLBACK,
    FRAMEWORK_ERROR,
    RUN_CRASH_DETECTED,
    STOP_REASON,
)


@dataclass(frozen=True)
class TerminalOutcome:
    """One declared outcome: its name, its watch line, and its classification.

    ``render`` receives the journal entry's ``detail`` mapping. ``klass`` is the
    diagnosis class the name maps to when no bespoke evidence is required; the
    classifier owns the branch whenever it must read diagnostics or state.
    """

    name: str
    render: Callable[[dict], str]
    klass: str | None = None
    stage: str | None = None
    detail_key: str | None = None


def _generation(detail: dict) -> str:
    return str(detail.get("generation", "?"))


_TERMINAL_TABLE: tuple[TerminalOutcome, ...] = (
    TerminalOutcome(
        RUN_COMPLETED,
        lambda detail: f"run completed (generation {_generation(detail)})",
        klass=None,  # delivery splits this one: the classifier owns the branch
    ),
    TerminalOutcome(RUN_CANCELLED, lambda detail: "run cancelled", klass="cancelled",
                    stage="operator decision — cancellation recorded"),
    TerminalOutcome(
        RUN_FAILED_RESUME,
        lambda detail: f"run failed-resume ({detail.get('reason', '?')})",
        klass=None,  # exhausted vs ambiguous depends on the journal history
    ),
    TerminalOutcome(
        LLM_ERROR_FALLBACK,
        lambda detail: f"run failed-resume ({detail.get('reason', '?')})",
        klass="model_call_failed",
        stage="binding — DeerFlow model call (framework error-fallback)",
        detail_key="error_type",
    ),
    TerminalOutcome(
        FRAMEWORK_ERROR,
        lambda detail: f"terminal: {FRAMEWORK_ERROR}",
        klass="framework_crash", stage="host runtime — DeerFlow raised through the stream",
        detail_key="error",
    ),
    TerminalOutcome(
        RUN_CRASH_DETECTED,
        lambda detail: f"terminal: {RUN_CRASH_DETECTED}",
klass="owner_died",
        stage="run pump process — owner died (transferred by a status observation)",
    ),
    TerminalOutcome(
        STOP_REASON,
        lambda detail: f"run failed-resume (stop reason: {detail.get('reason', '?')})",
        klass="framework_stopped", stage="host runtime — DeerFlow reported a stop reason",
        detail_key="reason",
    ),
)

OUTCOMES: dict[str, TerminalOutcome] = {row.name: row for row in _TERMINAL_TABLE}


def render_terminal_line(event: str, detail: dict) -> str:
    """The watch line for one terminal event; unknown names fall through verbatim."""
    row = OUTCOMES.get(event)
    return row.render(detail) if row is not None else f"terminal: {event}"


# Status -> terminal event, for the CLI's status projection (the state machine's
# status vocabulary mapped onto the journal's outcome vocabulary).
STATUS_TO_OUTCOME: dict[str, str] = {
    "completed": RUN_COMPLETED,
    "cancelled": RUN_CANCELLED,
    "failed-resume": RUN_FAILED_RESUME,
}


def outcome_for_status(status: str) -> str:
    """The terminal event a status projects to; unknown statuses fail-resume."""
    return STATUS_TO_OUTCOME.get(status, RUN_FAILED_RESUME)
