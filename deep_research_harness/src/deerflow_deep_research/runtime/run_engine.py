"""The run engine: one stream iteration, three sinks, terminal honesty.

Framework-free: the engine consumes any iterable of objects with ``type``/``data``
attributes (the real StreamEvent shape) and a ``stream_fn(message)`` callable — the
integration smoke supplies the real client; the unit lane supplies scripted events.
Terminal decisions are the RUB-001 pure rules; this module never re-decides them.

@impl DEW-001"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Callable

from ..domain import bundle, clarification, journal_policy
from ..domain.state_machine import BundleState, rule_clarification_step, rule_run_terminal
from . import bundle_state
from .journal import append_entry

AUTO_REPLY_PREFIX = "[非交互模式·系统自动应答] "


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _journal(handle: BundleHandle, category: str, event: str, detail: dict) -> None:
    append_entry(
        handle,
        journal_policy.JournalEntry(
            timestamp=_now_iso(), category=category, event=event, detail=detail
        ).validate(),
    )


def _msg_field(message: object, name: str, default=None):  # noqa: ANN001 — dict/object adapter
    if isinstance(message, dict):
        return message.get(name, default)
    return getattr(message, name, default)


def _json_arguments(call: dict) -> str:
    args = call.get("args")
    if isinstance(args, str):
        return args
    return json.dumps(args if args is not None else {}, ensure_ascii=False)


def _is_framework_clarification_echo(message: object, answered_id: str) -> bool:
    """The framework's clarification tool answers its own tool call with the question
    echo (content '❓ …', id 'clarification:…'). Mechanically answered; semantically
    it is the question awaiting human input — never counted as an answer."""

    name = str(_msg_field(message, "name", "") or "")
    return name == clarification.ASK_CLARIFICATION_TOOL or answered_id.startswith("clarification:")


def _consume_turn(
    handle: BundleHandle, stream_fn: Callable[[str], object], message: str, thread_id: str
) -> tuple[list[clarification.TerminalToolCall], set[str], str | None]:
    """One stream turn: journal tool/subagent events, and derive the terminal picture
    from the final ``values`` snapshot (complete message list) with streamed chunks as
    the fallback — chunk-level tool_calls are partial; the snapshot is authoritative."""

    tool_calls: list[clarification.TerminalToolCall] = []
    answered: set[str] = set()
    stop_reason: str | None = None
    values_calls: list[clarification.TerminalToolCall] = []
    values_answered: set[str] = set()
    for event in stream_fn(message):
        event_type = getattr(event, "type", None)
        data = getattr(event, "data", None) or {}
        if event_type == "values":
            messages = data.get("messages", []) if isinstance(data, dict) else []
            values_calls, values_answered = [], set()
            for message_item in messages:
                kind = _msg_field(message_item, "type", "")
                if kind in {"ai", "AIMessage", "AIMessageChunk"}:
                    # Only the LAST AI message's calls count (the terminal picture) —
                    # older turns' clarifications are history, not pending questions.
                    calls = _msg_field(message_item, "tool_calls", []) or []
                    values_calls = [
                        clarification.TerminalToolCall(
                            call_id=str(call.get("id", "")),
                            name=str(call.get("name", "")),
                            arguments=_json_arguments(call),
                        )
                        for call in calls
                    ]
                elif kind in {"tool", "ToolMessage"}:
                    answered_id = str(_msg_field(message_item, "tool_call_id", "") or "")
                    if answered_id and not _is_framework_clarification_echo(message_item, answered_id):
                        values_answered.add(answered_id)
        elif event_type == "messages-tuple":
            message_chunk = data.get("message") if isinstance(data, dict) else getattr(data, "message", None)
            kind = _msg_field(message_chunk, "type", "")
            if kind in {"ai", "AIMessage", "AIMessageChunk"}:
                calls = _msg_field(message_chunk, "tool_calls", []) or []
                for call in calls:
                    tool_calls.append(
                        clarification.TerminalToolCall(
                            call_id=str(call.get("id", "")),
                            name=str(call.get("name", "")),
                            arguments=_json_arguments(call),
                        )
                    )
                _journal(
                    handle,
                    "model_tool",
                    "model_tool_call",
                    {"calls": [call.get("name", "") for call in calls]} if calls else {"text": True},
                )
            elif kind in {"tool", "ToolMessage"}:
                answered_id = str(_msg_field(message_chunk, "tool_call_id", "") or "")
                if answered_id and not _is_framework_clarification_echo(message_chunk, answered_id):
                    answered.add(answered_id)
                _journal(handle, "model_tool", "tool_result", {"tool_call_id": answered_id})
        elif event_type == "custom":
            _journal(handle, "subagent", str(data.get("event", "subagent_event")), dict(data))
        elif event_type == "end":
            stop_reason = data.get("stop_reason") if isinstance(data, dict) else None
    if values_calls or values_answered:
        return values_calls, values_answered, stop_reason
    return tool_calls, answered, stop_reason


def run_research(
    handle: BundleHandle,
    *,
    stream_fn: Callable[[str], object],
) -> BundleState:
    """Drive one research run to an honest terminal state.

    Sinks: the journal (tool/subagent events), the state machine (terminal rules),
    and the diagnostics directory (unanswered questions). Continuation turns
    re-invoke the client on the same thread with a provenance-marked reply."""

    state = bundle_state.read_state(handle)
    problem = (handle.root / bundle.request_problem_relative()).read_text(encoding="utf-8").strip()
    message = problem

    while True:
        tool_calls, answered, stop_reason = _consume_turn(handle, stream_fn, message, state.thread_id)
        detected = clarification.unanswered_ask_clarification(
            clarification.TerminalObservation(
                tool_calls=tuple(tool_calls),
                answered_call_ids=frozenset(answered),
            )
        )

        if not detected:
            fresh = bundle_state.read_state(handle)
            if fresh.cancel_requested:
                state = rule_run_terminal(fresh, "cancelled")
                return bundle_state.write_state(handle, fresh, state)
            if stop_reason:
                state = rule_run_terminal(fresh, "failed-resume")
                written = bundle_state.write_state(handle, fresh, state)
                _journal(handle, "terminal", "stop_reason", {"reason": stop_reason})
                return written
            state = rule_run_terminal(fresh, "completed")
            return bundle_state.write_state(handle, fresh, state)

        last_question = tool_calls[-1].arguments if tool_calls else ""
        if state.auto_proceed_count < state.auto_proceed_bound:
            state = rule_clarification_step(state, detected=True)
            state = bundle_state.write_state(handle, bundle_state.read_state(handle), state)
            _journal(
                handle,
                "lifecycle",
                "auto_continuation",
                {"count": state.auto_proceed_count, "bound": state.auto_proceed_bound},
            )
            message = AUTO_REPLY_PREFIX + clarification.question_text(last_question)
            continue

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
        return written
