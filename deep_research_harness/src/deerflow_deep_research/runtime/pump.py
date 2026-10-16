"""The run pump: one stream iteration, three sinks, terminal honesty.

Framework-free: the pump consumes any iterable of objects with ``type``/``data``
attributes (the real StreamEvent shape) and a ``stream_fn(message)`` callable — the
integration smoke supplies the real client; the unit lane supplies scripted events.
Terminal decisions are the RUB-001 pure rules; this module never re-decides them.

@impl DEW-001"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ..domain import bundle, clarification
from ..domain.state_machine import BundleState, rule_run_terminal
from .bundle import bundle_state, search_log

# Re-exported for surface parity: this name used to leak through the module-level
# import of the journal writer. Kept so the module's public surface is unchanged.
from .bundle.journal import (
    append_entry,  # noqa: F401
    tail_journal,  # noqa: F401 — re-export (watch tool)
)
from .pump_parts.deliver import record_delivery as _record_delivery_impl
from .pump_parts.gates import clarification_step, plan_gate_step

# The double-hop re-exports below (turn -> pump) are this module's public surface:
# nothing in this file calls them, but callers and tests reach them here. F401 is
# therefore explicitly waived for the whole block rather than per name.
from .pump_parts.turn import (  # noqa: F401
    AUTO_REPLY_PREFIX,
    PLAN_CONFIRM_PREFIX,
    PLAN_REQUEST_SUFFIX,
    PLAN_SKIP_MESSAGE,
    TurnOutcome,
    _extract_plan,
    _is_framework_clarification_echo,
    _journal,
    _json_arguments,
    _msg_field,
    _now_iso,
)

# The module's declared surface: the entry points callers import, the vocabulary
# other layers read, and the migration-period names the tests address.
__all__ = [
    "AUTO_REPLY_PREFIX",
    "PLAN_REQUEST_SUFFIX",
    "_journal",
]

from .pump_parts.turn import (
    consume_turn as _consume_turn,
)

if TYPE_CHECKING:

    from .bundle.bundle_state import BundleHandle


# ---------------------------------------------------------------------------
# Contract-locked shells. `tests/contract/test_entry_chain.py` parses THIS file and
# requires both names here: `_record_delivery` calling `_submit_final_report`, and
# `_submit_final_report` reaching `submit_artifact` (the admission hold point). The
# state enrichment lives in `pump_parts/deliver.py`; do not "de-duplicate" these.
# ---------------------------------------------------------------------------
def _submit_final_report(handle: BundleHandle, generation: int, final_text: str):
    """A clean completion's final answer passes the admission hold point as a
    final_report (models propose, code disposes); an empty answer never submits.

    Returns the ledger entry carrying the fine-grained disposition."""

    text = (final_text or "").strip()
    if not text:
        return None
    from ..engine.validator import ArtifactSubmission
    from .bundle.admission import submit_artifact

    return submit_artifact(
        handle,
        ArtifactSubmission(
            kind="final_report",
            filename=f"report-gen{generation}.md",
            content=text.encode("utf-8"),
            provenance={"producer": "run-engine"},
        ),
    )


def _record_delivery(handle: BundleHandle, terminal: BundleState, final_text: str) -> BundleState:
    """Submit the final answer, then record the orthogonal delivery fact in state."""
    text = (final_text or "").strip()
    entry = _submit_final_report(handle, terminal.generation, final_text) if text else None
    return _record_delivery_impl(handle, terminal, final_text, entry=entry)


def run_research(
    handle: BundleHandle,
    *,
    stream_fn: Callable[[str], object],
    on_event: Callable[[object], None] | None = None,
    on_clarification: Callable[[str], str | None] | None = None,
    on_plan: Callable[[str], str | None] | None = None,
) -> BundleState:
    """Drive one research run to an honest terminal state.

    Sinks: the journal (tool/subagent events), the state machine (terminal rules),
    and the diagnostics directory (unanswered questions). Continuation turns
    re-invoke the client on the same thread with a provenance-marked reply; with a
    clarification hook the question is delivered to the human first and a
    non-empty answer continues the run as the human's own words; with a plan hook
    on a first-generation run the first plain-text turn is the proposed research
    plan, gated by the human and injected as the continuation."""

    state = bundle_state.read_state(handle)
    recorder = search_log.SearchLog(handle, generation=state.generation)
    if state.generation > 1:
        # Generation N>1 runs over its own direction document — resending the
        # original problem would be a lie about what the run researched.
        message = (
            handle.root / bundle.refine_request_relative(state.generation)
        ).read_text(encoding="utf-8").strip()
    else:
        message = (handle.root / bundle.request_problem_relative()).read_text(encoding="utf-8").strip()
        if on_plan is not None:
            message = message + PLAN_REQUEST_SUFFIX

    try:
        return _drive(
            handle, stream_fn, on_event, on_clarification, on_plan, state, message, recorder,
        )
    except Exception as exc:  # framework/stream failure: loud terminal, material preserved
        fresh = bundle_state.read_state(handle)
        failed = rule_run_terminal(fresh, "failed-resume")
        written = bundle_state.write_state(handle, fresh, failed)
        _journal(handle, "terminal", "framework_error", {"reason": "framework_error", "error": type(exc).__name__})
        return written


def _drive(handle, stream_fn, on_event, on_clarification, on_plan, state, message, recorder):
    awaiting_plan = on_plan is not None and state.generation == 1
    while True:
        # The bundle is the fact owner; a step that advances it (spending the
        # clarification bound) must not leave a stale copy in the loop.
        state = bundle_state.read_state(handle)
        outcome = _consume_turn(handle, stream_fn, message, state.thread_id, on_event, recorder)
        tool_calls = outcome.tool_calls
        answered = outcome.answered
        detected = clarification.unanswered_ask_clarification(
            clarification.TerminalObservation(
                tool_calls=tuple(tool_calls),
                answered_call_ids=frozenset(answered),
            )
        )
        # A clarification the framework answered in-turn (call id in the answered set)
        # is still a round the model asked — journal it at classification time, before
        # any terminal decision or plan-gate branch, so the interaction history has no
        # silent absorption. Recorded only: no continuation, no bound consumption.
        for absorbed_call in clarification.absorbed_ask_clarifications(
            clarification.TerminalObservation(
                tool_calls=tuple(tool_calls),
                answered_call_ids=frozenset(answered),
            )
        ):
            _journal(handle, "lifecycle", "clarification_absorbed", {
                "question": clarification.question_text(absorbed_call.arguments),
            })

        if detected:
            cont, message, advanced = clarification_step(
                handle, on_clarification, state, tool_calls
            )
            if not cont:
                return advanced
            # Spending the auto-continuation bound advanced the state; the loop must
            # carry it, or the bound would never be reached.
            state = advanced
            continue

        cont, message, terminal = _finish(
            handle, awaiting_plan, on_plan,
            outcome.final_text, outcome.fallback_error_type, outcome.stop_reason,
        )
        if not cont:
            return terminal
        # The gate has had its turn (produced, amended, skipped or degraded): it must
        # not re-open on the continuation turn.
        awaiting_plan = False
        if message is not None:
            continue


def _finish(handle, awaiting_plan, on_plan, final_text, fallback_error_type, stop_reason):
    """The plan gate first, then the ordinary terminal rules — original order, verbatim.

    The bundle is the only state carrier read here (the caller's loop variable can be
    stale after a step advanced the run); a terminal disposition is returned for the
    caller to hand back.

    ``(True, message, None)``: the plan gate produced the next turn's message.
    ``(False, None, state)``: a terminal disposition for the caller to return.
    """
    state = bundle_state.read_state(handle)
    if awaiting_plan:
        produced, message, _ = plan_gate_step(handle, on_plan, state, final_text)
        if produced:
            # A plan-shaped turn was gated: the next turn carries the confirmation,
            # the amendment, or the skip notice.
            return True, message, None
        # No plan markers: the gate degraded (journaled) and the ordinary terminal
        # rules below decide, exactly as they did before the split.
    fresh = bundle_state.read_state(handle)
    if fallback_error_type is not None:
        # The framework disguised a model-call failure as a normal AI message:
        # fail loud instead of completing (wiring plan, error-fallback guard).
        state = rule_run_terminal(fresh, "failed-resume")
        written = bundle_state.write_state(handle, fresh, state)
        _journal(
            handle,
            "terminal",
            "llm_error_fallback",
            {"reason": "llm_error_fallback", "error_type": fallback_error_type},
        )
        return False, None, written
    if fresh.cancel_requested:
        state = rule_run_terminal(fresh, "cancelled")
        written = bundle_state.write_state(handle, fresh, state)
        _journal(handle, "terminal", "run_cancelled", {"generation": written.generation})
        return False, None, written
    if stop_reason:
        state = rule_run_terminal(fresh, "failed-resume")
        written = bundle_state.write_state(handle, fresh, state)
        _journal(handle, "terminal", "stop_reason", {"reason": stop_reason})
        return False, None, written
    state = rule_run_terminal(fresh, "completed")
    written = bundle_state.write_state(handle, fresh, state)
    _journal(handle, "terminal", "run_completed", {"generation": written.generation})
    written = _record_delivery(handle, written, final_text)
    return False, None, written
