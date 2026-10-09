"""Clarification continuation: the pure detection predicate and question extraction.

Pure stdlib. The embedded event shapes are mirrored by the wiring change, which adapts
them onto these minimal typed structures — deliberately no deerflow types here.

@impl RUB-001"""

from __future__ import annotations

import json
from dataclasses import dataclass

ASK_CLARIFICATION_TOOL = "ask_clarification"


@dataclass(frozen=True)
class TerminalToolCall:
    call_id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class TerminalObservation:
    """The stream-terminal picture: the final AI message's tool calls plus the call
    ids that received a tool result."""

    tool_calls: tuple[TerminalToolCall, ...]
    answered_call_ids: frozenset[str]


def unanswered_ask_clarification(observation: TerminalObservation) -> bool:
    """True when the terminal message carries an ask_clarification call that no tool
    message answered (the wiring 决策 8 detection predicate, as a pure function)."""

    return any(
        call.name == ASK_CLARIFICATION_TOOL and call.call_id not in observation.answered_call_ids
        for call in observation.tool_calls
    )


def absorbed_ask_clarifications(
    observation: TerminalObservation,
) -> tuple[TerminalToolCall, ...]:
    """The ask_clarification calls the terminal turn itself resolved — the framework
    answered them within the same turn, so their call ids appear in the answered set
    and the unanswered predicate reports False (the 5128f695 silent-absorption shape).
    Symmetric to ``unanswered_ask_clarification``: together the two partition every
    ask_clarification the turn carries. Recorded, never acted on."""

    return tuple(
        call
        for call in observation.tool_calls
        if call.name == ASK_CLARIFICATION_TOOL and call.call_id in observation.answered_call_ids
    )


def question_text(arguments: str) -> str:
    """The unanswered question's text: the JSON `question` field when the arguments
    parse, otherwise the raw argument text (provenance honesty over prettiness)."""

    try:
        parsed = json.loads(arguments)
    except (json.JSONDecodeError, TypeError):
        return arguments
    if isinstance(parsed, dict) and isinstance(parsed.get("question"), str):
        return parsed["question"]
    return arguments
