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
from .bundle import bundle_state
from .bundle.journal import append_entry

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
    handle: BundleHandle,
    stream_fn: Callable[[str], object],
    message: str,
    thread_id: str,
    on_event: Callable[[object], None] | None = None,
) -> tuple[list[clarification.TerminalToolCall], set[str], str | None, str | None, str]:
    """One stream turn: journal tool/subagent events, and derive the terminal picture
    from the final ``values`` snapshot (complete message list) with streamed chunks as
    the fallback — chunk-level tool_calls are partial; the snapshot is authoritative."""

    tool_calls: list[clarification.TerminalToolCall] = []
    answered: set[str] = set()
    stop_reason: str | None = None
    fallback_error_type: str | None = None
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
                text = str(chunk.get("content", "") or "")
                if text:
                    turn_text.append(text)
            elif kind in {"tool", "ToolMessage"}:
                answered_id = str(chunk.get("tool_call_id", "") or "")
                if answered_id and not _is_framework_clarification_echo(chunk, answered_id):
                    answered.add(answered_id)
        elif event_type == "custom":
            _journal(handle, "subagent", str(data.get("event", "subagent_event")), dict(data))
        elif event_type == "end":
            stop_reason = data.get("stop_reason") if isinstance(data, dict) else None
    # One aggregated model_tool entry per turn (token chunks never journal
    # individually — the ledger stays at event granularity).
    if turn_text or tool_calls:
        excerpt = "".join(turn_text)[-80:]
        detail = {"calls": [call.name for call in tool_calls], "answer_excerpt": excerpt} if tool_calls else {"answer_excerpt": excerpt}
        _journal(handle, "model_tool", "model_tool_call", detail)
    if saw_values or values_calls or values_answered or values_fallback_error_type is not None:
        return values_calls, values_answered, stop_reason, values_fallback_error_type, "".join(values_final_text)
    return tool_calls, answered, stop_reason, values_fallback_error_type, "".join(turn_text)



def _submit_final_report(handle: BundleHandle, generation: int, final_text: str) -> None:
    """A clean completion's final answer passes the admission hold point as a
    final_report (models propose, code disposes); an empty answer never submits."""

    text = (final_text or "").strip()
    if not text:
        return
    from .bundle.admission import submit_artifact
    from ..engine.validator import ArtifactSubmission

    submit_artifact(
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


def run_research(
    handle: BundleHandle,
    *,
    stream_fn: Callable[[str], object],
    on_event: Callable[[object], None] | None = None,
) -> BundleState:
    """Drive one research run to an honest terminal state.

    Sinks: the journal (tool/subagent events), the state machine (terminal rules),
    and the diagnostics directory (unanswered questions). Continuation turns
    re-invoke the client on the same thread with a provenance-marked reply."""

    state = bundle_state.read_state(handle)
    problem = (handle.root / bundle.request_problem_relative()).read_text(encoding="utf-8").strip()
    message = problem

    try:
        return _drive(handle, stream_fn, on_event, state, message)
    except Exception as exc:  # framework/stream failure: loud terminal, material preserved
        fresh = bundle_state.read_state(handle)
        failed = rule_run_terminal(fresh, "failed-resume")
        written = bundle_state.write_state(handle, fresh, failed)
        _journal(handle, "terminal", "framework_error", {"reason": "framework_error", "error": type(exc).__name__})
        return written


def _drive(handle, stream_fn, on_event, state, message):
    while True:
        tool_calls, answered, stop_reason, fallback_error_type, final_text = _consume_turn(
            handle, stream_fn, message, state.thread_id, on_event
        )
        detected = clarification.unanswered_ask_clarification(
            clarification.TerminalObservation(
                tool_calls=tuple(tool_calls),
                answered_call_ids=frozenset(answered),
            )
        )

        if not detected:
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
                return written
            if fresh.cancel_requested:
                state = rule_run_terminal(fresh, "cancelled")
                written = bundle_state.write_state(handle, fresh, state)
                _journal(handle, "terminal", "run_cancelled", {"generation": written.generation})
                return written
            if stop_reason:
                state = rule_run_terminal(fresh, "failed-resume")
                written = bundle_state.write_state(handle, fresh, state)
                _journal(handle, "terminal", "stop_reason", {"reason": stop_reason})
                return written
            state = rule_run_terminal(fresh, "completed")
            written = bundle_state.write_state(handle, fresh, state)
            _journal(handle, "terminal", "run_completed", {"generation": written.generation})
            _submit_final_report(handle, written.generation, final_text)
            return written

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
        _journal(handle, "terminal", "run_failed_resume", {"reason": "clarification bound exhausted"})
        return written
