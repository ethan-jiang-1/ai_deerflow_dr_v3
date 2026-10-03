"""The shared human rendering vocabulary: one set of phrases for the live view and
the journal projection.

Deterministic output — the golden replay pins these strings. Volatile values
(timestamps, ids) stay out of the phrases the golden asserts.

@impl ENS-001"""

from __future__ import annotations


def _msg_field(message: object, name: str, default=None):  # noqa: ANN001
    if isinstance(message, dict):
        return message.get(name, default)
    return getattr(message, name, default)


def event_line(event) -> str:  # noqa: ANN001 — live view (raw stream event)
    event_type = getattr(event, "type", "?")
    data = getattr(event, "data", None) or {}
    if event_type == "messages-tuple":
        message = data.get("message") if isinstance(data, dict) else getattr(data, "message", None)
        kind = _msg_field(message, "type", "")
        if kind in {"ai", "AIMessage", "AIMessageChunk"}:
            calls = _msg_field(message, "tool_calls", []) or []
            if calls:
                names = ", ".join(str(call.get("name", "?")) for call in calls)
                return f"model calls {names}"
            content = str(_msg_field(message, "content", "") or "").strip()
            if content:
                return f"model: {content[:80]}"
            return "model thinking"
        if kind in {"tool", "ToolMessage"}:
            name = str(_msg_field(message, "name", "tool") or "tool")
            return f"tool {name} finished"
        return "message"
    if event_type == "custom":
        detail = data.get("event", "subagent event") if isinstance(data, dict) else "subagent event"
        return f"subagent {detail}"
    if event_type == "end":
        stop_reason = data.get("stop_reason") if isinstance(data, dict) else None
        if stop_reason:
            return f"turn finished (stop reason: {stop_reason})"
        return "turn finished"
    if event_type == "values":
        return "state snapshot"
    return str(event_type)


def journal_line(entry) -> str:  # noqa: ANN001 — watch projection (journal entry)
    detail = entry.detail if isinstance(entry.detail, dict) else {}
    if entry.category == "terminal":
        if entry.event == "run_completed":
            return f"run completed (generation {detail.get('generation', '?')})"
        if entry.event == "run_cancelled":
            return "run cancelled"
        if entry.event == "stop_reason":
            return f"run failed-resume (stop reason: {detail.get('reason', '?')})"
        if entry.event == "run_failed_resume":
            return f"run failed-resume ({detail.get('reason', '?')})"
        return f"terminal: {entry.event}"
    if entry.event == "model_tool_call" and detail.get("calls"):
        return "model calls " + ", ".join(str(name) for name in detail["calls"])
    if entry.event == "model_tool_call":
        return "model answered"
    if entry.event == "tool_result":
        return "tool result received"
    if entry.event == "auto_continuation":
        return f"auto continuation {detail.get('count', '?')}/{detail.get('bound', '?')}"
    if entry.event == "disposition_recorded":
        return f"admission {detail.get('disposition', '?')} ({detail.get('result_code', '?')})"
    if entry.category == "exhaustion":
        return f"clarification bound exhausted ({detail.get('bound', '?')})"
    return f"{entry.category}: {entry.event}"
