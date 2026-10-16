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
from ...domain.plan import (
    PLAN_MARKER_CLOSE,
    PLAN_MARKER_OPEN,
    extract_plan as _extract_plan,
)
from ..bundle import search_log
from ..bundle.journal import append_entry


# The non-interactive continuation marker the clarification step prefixes.
AUTO_REPLY_PREFIX = "[非交互模式·系统自动应答] "


# Plan-gate framing and continuations (stable constants; scripted tests pin them).
# Markers are the ONLY engagement signal: content structure, never behavioral
# inference — a research turn ending in a plain-text report is indistinguishable
# from a plan turn by tool calls alone (the 58b5440e real-ladder regression).
# The marker literals and the extraction live in domain/plan.py (single owner —
# the validator's plan-as-report refusal face consumes the same vocabulary).
PLAN_REQUEST_SUFFIX = (
    f"\n\n请先给出研究计划（研究角度、查询策略、来源类型），全文用 {PLAN_MARKER_OPEN} 和 "
    f"{PLAN_MARKER_CLOSE} 标记包裹，然后停止等待确认；不要在此轮执行搜索。"
    "如需先澄清问题，请直接提问，获得回答后请再次输出带标记的研究计划。"
    "通道纪律：提问的一轮只携带 ask_clarification 这一个工具调用，不要同轮调用任何其他"
    "工具（同轮的兄弟调用会被直接丢弃，已做的检索全部白费）；计划确认只通过 "
    f"{PLAN_MARKER_OPEN} 标记表达，绝不要把确认请求或计划全文塞进 ask_clarification。"
)
PLAN_CONFIRM_PREFIX = "研究计划已确认（或经用户修订）。严格按以下计划执行研究并产出最终报告：\n\n"
PLAN_SKIP_MESSAGE = "跳过计划注入，按你自己的判断研究并产出最终报告。"















def _record_delivery(handle: BundleHandle, terminal: BundleState, final_text: str) -> BundleState:
    """Submit the final answer, then record the orthogonal delivery fact in state.

    The process fact (terminal) lands first; the delivery fact enriches it through
    the same revision-CAS path. Mapping: ledger admit/replay -> admitted (replay is
    reworked content that materialized), reject -> rejected, empty answer ->
    no-answer. The fine-grained disposition stays in the journal and ledger; state
    answers only "did this generation deliver?". A crash before the enrichment
    write leaves delivery unrecorded (None) — honest, never a torn fact.
    """

    text = (final_text or "").strip()
    if not text:
        delivery, artifact = "no-answer", None
    else:
        entry = _submit_final_report(handle, terminal.generation, final_text)
        if entry.disposition in {"admit", "replay"}:
            delivery, artifact = "admitted", entry.artifact_path
        else:
            delivery, artifact = "rejected", None

    from dataclasses import replace

    fresh = bundle_state.read_state(handle)
    enriched = replace(fresh, delivery=delivery, delivery_artifact=artifact)
    return bundle_state.write_state(handle, fresh, enriched)


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


def tail_journal(journal_path: Path, position: int = 0):
    """Read new journal entries from ``position`` (character offset).

    Returns ``(entries, reached_terminal, new_position)``: ``reached_terminal`` is True
    once a ``terminal`` entry has been rendered — the bounded watch exits there."""

    from ..domain.journal_policy import JournalEntry

    entries: list[JournalEntry] = []
    reached_terminal = False
    if not journal_path.is_file():
        return entries, reached_terminal, position
    text = journal_path.read_text(encoding="utf-8")
    for line in text[position:].splitlines():
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue  # a partially written tail line is re-read on the next poll
        entry = JournalEntry.from_dict(raw)
        entries.append(entry)
        if entry.category == "terminal":
            reached_terminal = True
    return entries, reached_terminal, position + len(text[position:])


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
