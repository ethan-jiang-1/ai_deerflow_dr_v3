"""One stream turn: the stream-to-observation adapter.

Framework-free: the pump consumes any iterable of objects with ``type``/``data``
attributes (the real StreamEvent shape) and a ``stream_fn(message)`` callable — the
integration smoke supplies the real client; the unit lane supplies scripted events.
Terminal decisions are the RUB-001 pure rules; this module never re-decides them.

@impl DEW-001"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from ...domain import clarification, journal_policy
from ..bundle import search_log
from ..bundle.journal import append_entry


@dataclass(frozen=True)
class TurnOutcome:
    """What one stream turn yielded, by name rather than by position.

    The pump used to unpack a five-tuple here; naming the fields is the point of
    the decomposition — the plan gate, the clarification step and the finish step
    each read two or three of them.
    """

    tool_calls: list[clarification.TerminalToolCall]
    answered: set[str]
    stop_reason: str | None
    fallback_error_type: str | None
    final_text: str


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


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


def consume_turn(
    handle: BundleHandle,
    stream_fn: Callable[[str], object],
    message: str,
    thread_id: str,
    on_event: Callable[[object], None] | None = None,
    recorder: search_log.SearchLog | None = None,
) -> tuple[list[clarification.TerminalToolCall], set[str], str | None, str | None, str]:
    """One stream turn: journal tool/subagent events, and derive the terminal picture
    from the final ``values`` snapshot (complete message list) with streamed chunks as
    the fallback — chunk-level tool_calls are partial; the snapshot is authoritative."""

    tool_calls: list[clarification.TerminalToolCall] = []
    answered: set[str] = set()
    stop_reason: str | None = None
    values_calls: list[clarification.TerminalToolCall] = []
    values_answered: set[str] = set()
    values_fallback_error_type: str | None = None
    turn_text: list[str] = []
    saw_values = False
    values_final_text: list[str] = []
    for event in stream_fn(message):
        if on_event is not None:
            on_event(event)
        event_type = getattr(event, "type", None)
        data = getattr(event, "data", None) or {}
        if event_type == "values":
            saw_values = True
            messages = data.get("messages", []) if isinstance(data, dict) else []
            values_calls, values_answered = [], set()
            for message_item in messages:
                kind = _msg_field(message_item, "type", "")
                if kind in {"ai", "AIMessage", "AIMessageChunk"}:
                    # Only the LAST AI message's calls count (the terminal picture) —
                    # older turns' clarifications are history, not pending questions.
                    values_final_text = [str(_msg_field(message_item, "content", "") or "")]
                    calls = _msg_field(message_item, "tool_calls", []) or []
                    values_calls = [
                        clarification.TerminalToolCall(
                            call_id=str(call.get("id", "")),
                            name=str(call.get("name", "")),
                            arguments=_json_arguments(call),
                        )
                        for call in calls
                    ]
                    if recorder is not None:
                        for call in calls:
                            recorder.note_call(
                                str(call.get("id", "")), str(call.get("name", "")), _json_arguments(call)
                            )
                    # The framework's error-handling middleware disguises a model-call
                    # failure as a normal AI message (deerflow_error_fallback marker):
                    # the terminal picture must carry it (wiring plan, error-fallback
                    # guard).
                    extra = _msg_field(message_item, "additional_kwargs", {}) or {}
                    marker = extra.get("deerflow_error_fallback") if isinstance(extra, dict) else None
                    values_fallback_error_type = (
                        str(extra.get("error_type", "unknown")) if marker else None
                    )
                elif kind in {"tool", "ToolMessage"}:
                    answered_id = str(_msg_field(message_item, "tool_call_id", "") or "")
                    if answered_id and not _is_framework_clarification_echo(message_item, answered_id):
                        values_answered.add(answered_id)
                        if recorder is not None:
                            recorder.note_result(
                                answered_id, str(_msg_field(message_item, "content", "") or "")
                            )
        elif event_type == "messages-tuple":
            # The real stream's data IS the message chunk (flat dict, token-grained —
            # verified by the live dump; see the plan's protocol notes).
            chunk = data if isinstance(data, dict) else {}
            kind = str(chunk.get("type", ""))
            if kind in {"ai", "AIMessage", "AIMessageChunk"}:
                calls = chunk.get("tool_calls") or []
                for call in calls:
                    tool_calls.append(
                        clarification.TerminalToolCall(
                            call_id=str(call.get("id", "")),
                            name=str(call.get("name", "")),
                            arguments=_json_arguments(call),
                        )
                    )
                    if recorder is not None:
                        recorder.note_call(
                            str(call.get("id", "")), str(call.get("name", "")), _json_arguments(call)
                        )
                text = str(chunk.get("content", "") or "")
                if text:
                    turn_text.append(text)
            elif kind in {"tool", "ToolMessage"}:
                answered_id = str(chunk.get("tool_call_id", "") or "")
                if answered_id and not _is_framework_clarification_echo(chunk, answered_id):
                    answered.add(answered_id)
                    if recorder is not None:
                        recorder.note_result(answered_id, str(chunk.get("content", "") or ""))
        elif event_type == "custom":
            _journal(handle, "subagent", str(data.get("event", "subagent_event")), dict(data))
        elif event_type == "end":
            stop_reason = data.get("stop_reason") if isinstance(data, dict) else None
    # One aggregated model_tool entry per turn (token chunks never journal
    # individually — the ledger stays at event granularity).
    if turn_text or tool_calls:
        excerpt = "".join(turn_text)[-80:]
        detail = (
            {"calls": [call.name for call in tool_calls], "answer_excerpt": excerpt}
            if tool_calls
            else {"answer_excerpt": excerpt}
        )
        _journal(handle, "model_tool", "model_tool_call", detail)
    if saw_values or values_calls or values_answered or values_fallback_error_type is not None:
        return TurnOutcome(values_calls, values_answered, stop_reason, values_fallback_error_type, "".join(values_final_text))
    return TurnOutcome(tool_calls, answered, stop_reason, values_fallback_error_type, "".join(turn_text))
