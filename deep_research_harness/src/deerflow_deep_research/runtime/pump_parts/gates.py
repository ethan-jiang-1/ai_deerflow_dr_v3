"""Gate steps of the drive loop: the plan gate and the clarification step.

Each step answers with an explicit signal — ``(True, message, None)`` produced the
next turn's message, ``(False, _, terminal)`` reached a terminal disposition. The
drive loop keeps every branch in its original order; extracting the steps changed
neither that order nor a single journal entry.

@impl DEW-001"""

from __future__ import annotations

import json

from ...domain import bundle, clarification
from ...domain.state_machine import rule_clarification_step
from ..bundle import bundle_state
from .turn import (
    AUTO_REPLY_PREFIX,
    PLAN_CONFIRM_PREFIX,
    PLAN_SKIP_MESSAGE,
    _extract_plan,
    _journal,
)


def plan_gate_step(handle, on_plan, state, final_text: str):
    """The first-generation plan gate: propose, then confirm/amend/skip.

    ``(True, message, None)`` continues the run with that message;
    ``(False, None, None)`` means no plan-shaped turn arrived, so the caller falls
    through to its ordinary terminal rules (the honest degradation).
    """
    plan_text = _extract_plan(final_text or "")
    if plan_text is None:
        # No plan markers (a report, a chatty answer, or nothing plan-shaped):
        # degrade honestly, never force-block, fall through to today's rules.
        _journal(handle, "lifecycle", "plan_gate_degraded", {
            "reason": "no_plan_markers",
        })
        return False, None, None
    _journal(handle, "lifecycle", "plan_proposed", {"plan_preview": plan_text[:200]})
    approved = on_plan(plan_text)
    if approved is not None and str(approved).strip():
        approved = str(approved).strip()
        event = "plan_confirmed" if approved == plan_text else "plan_amended"
        _journal(handle, "lifecycle", event, {"plan_preview": approved[:200]})
        from ..bundle.atomic import atomic_write_text

        atomic_write_text(
            handle.root / bundle.plan_request_relative(state.generation),
            approved + "\n",
        )
        return True, PLAN_CONFIRM_PREFIX + approved, None
    _journal(handle, "lifecycle", "plan_skipped", {})
    return True, PLAN_SKIP_MESSAGE, None


def clarification_step(handle, on_clarification, state, tool_calls):
    """A detected unanswered clarification: ask the human, or spend the bound.

    ``(True, message, state)`` continues the run with that message — the human's own
    words, or the provenance-marked automatic reply — and hands back the (possibly
    advanced) state, because spending the bound is a state transition the caller's
    loop variable must see. ``(False, "", terminal)`` means the bound was exhausted
    and the caller returns that terminal state.
    """
    last_question = tool_calls[-1].arguments if tool_calls else ""
    if on_clarification is not None:
        question_text = clarification.question_text(last_question)
        _journal(handle, "lifecycle", "clarification_asked", {"question": question_text})
        answer = on_clarification(question_text)
        if answer is not None and str(answer).strip():
            # The human's own words continue the run — raw, no provenance prefix.
            _journal(
                handle, "lifecycle", "clarification_answered", {"question": question_text},
            )
            return True, str(answer).strip(), state
        # Declined (empty answer): fall back to the bounded automatic reply.
        _journal(handle, "lifecycle", "clarification_declined", {"question": question_text})
    if state.auto_proceed_count < state.auto_proceed_bound:
        state = rule_clarification_step(state, detected=True)
        state = bundle_state.write_state(handle, bundle_state.read_state(handle), state)
        _journal(
            handle,
            "lifecycle",
            "auto_continuation",
            {"count": state.auto_proceed_count, "bound": state.auto_proceed_bound},
        )
        return True, AUTO_REPLY_PREFIX + clarification.question_text(last_question), state

    exhausted = rule_clarification_step(state, detected=True)
    written = bundle_state.write_state(handle, bundle_state.read_state(handle), exhausted)
    questions_path = handle.root / bundle.UNANSWERED_QUESTIONS_RELATIVE
    questions_path.parent.mkdir(parents=True, exist_ok=True)
    questions_path.write_text(
        json.dumps(
            {"questions": [clarification.question_text(last_question)]},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _journal(
        handle,
        "exhaustion",
        "clarification_bound_exhausted",
        {"bound": state.auto_proceed_bound},
    )
    _journal(handle, "terminal", "run_failed_resume", {"reason": "clarification bound exhausted"})
    return False, "", written
