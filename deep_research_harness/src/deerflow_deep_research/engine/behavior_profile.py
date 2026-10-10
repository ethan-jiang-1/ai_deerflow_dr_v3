"""Behavior profile: what a real research run actually did (stunt-ladder level 4).

Pure stdlib. Derives an observational profile from a run's recorded journal
(``diagnostics/journal.jsonl``): per-tool call counts from ``model_tool_call``
entries, event-kind composition, and the wall-clock span between the first and
last recorded timestamps. This observes, never admits: the outputs are profiles
and violated-expectation names — no admission codes, no run-admission consumer
(test-evidence spec, observe-not-admit).

Known boundaries (deliberate, evidence-recorded):

- Token totals are NOT derived — the journal carries no structured token field,
  and parsing content strings would fake the dimension.
- Unknown tool names surface in ``unknown_tools``; they are never silently
  bucketed into the known vocabulary.

@impl TES-002"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

#: Closed known-tool vocabulary, from the recorded run corpus (2026-10-03..07).
KNOWN_TOOLS: tuple[str, ...] = (
    "web_search",
    "web_fetch",
    "task",
    "ask_clarification",
)

#: Tools whose absence marks a degenerate research run (it never researched).
SEARCH_TOOLS: tuple[str, ...] = ("web_search", "web_fetch")


@dataclass(frozen=True)
class BehaviorProfile:
    """Observational profile of one recorded run. Carries no verdict codes."""

    tool_calls: Mapping[str, int] = field(default_factory=dict)
    unknown_tools: tuple[str, ...] = ()
    event_counts: Mapping[str, int] = field(default_factory=dict)
    event_total: int = 0
    span_seconds: float | None = None


def _parse_ts(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def profile_journal(events: Sequence[Mapping[str, Any]]) -> BehaviorProfile:
    """Derive the profile from parsed journal lines (pure; no I/O here).

    ``events`` are the decoded jsonl records of one run's journal. Tool names
    come from ``model_tool_call`` entries' ``detail.calls`` lists; timestamps
    from each entry's ``ts``; event kinds from ``event`` (falling back to
    ``kind``). Absent timestamps leave ``span_seconds`` as ``None``.
    """
    tool_calls: dict[str, int] = {}
    unknown: list[str] = []
    event_counts: dict[str, int] = {}
    stamps: list[datetime] = []
    total = 0
    for event in events:
        total += 1
        name = str(event.get("event") or event.get("kind") or "?")
        event_counts[name] = event_counts.get(name, 0) + 1
        stamp = _parse_ts(event.get("ts"))
        if stamp is not None:
            stamps.append(stamp)
        if name == "model_tool_call":
            detail = event.get("detail")
            calls = detail.get("calls", []) if isinstance(detail, Mapping) else []
            for tool in calls:
                tool = str(tool)
                tool_calls[tool] = tool_calls.get(tool, 0) + 1
                if tool not in KNOWN_TOOLS and tool not in unknown:
                    unknown.append(tool)
    span = (max(stamps) - min(stamps)).total_seconds() if stamps else None
    return BehaviorProfile(
        tool_calls=tool_calls,
        unknown_tools=tuple(unknown),
        event_counts=event_counts,
        event_total=total,
        span_seconds=span,
    )


def check_expectations(
    profile: BehaviorProfile,
    *,
    tool_calls: Mapping[str, int] | None = None,
    event_counts: Mapping[str, int] | None = None,
    event_total: int | None = None,
    span_seconds: float | None = None,
    min_search_calls: int | None = None,
) -> tuple[str, ...]:
    """Check a profile against declared expectations; return violated names.

    Pure comparison — an empty tuple means every expectation holds. Only the
    expectations actually declared are checked. ``min_search_calls`` is the
    degenerate-research guard: a run with fewer search-or-fetch tool calls than
    declared is named as degenerate research, not as a failed admission (this
    machine never renders admission outcomes).
    """
    violations: list[str] = []
    if tool_calls is not None:
        for tool, expected in tool_calls.items():
            actual = profile.tool_calls.get(tool, 0)
            if actual != expected:
                violations.append(
                    f"tool_calls.{tool}: expected {expected}, got {actual}"
                )
    if event_counts is not None:
        for kind, expected in event_counts.items():
            actual = profile.event_counts.get(kind, 0)
            if actual != expected:
                violations.append(
                    f"event_counts.{kind}: expected {expected}, got {actual}"
                )
    if event_total is not None and profile.event_total != event_total:
        violations.append(
            f"event_total: expected {event_total}, got {profile.event_total}"
        )
    if span_seconds is not None:
        if profile.span_seconds is None:
            violations.append("span_seconds: no timestamps in journal")
        elif abs(profile.span_seconds - span_seconds) > 1e-6:
            violations.append(
                f"span_seconds: expected {span_seconds}, got {profile.span_seconds}"
            )
    if min_search_calls is not None:
        actual = sum(profile.tool_calls.get(tool, 0) for tool in SEARCH_TOOLS)
        if actual < min_search_calls:
            violations.append(
                f"min_search_calls: degenerate research — {actual} search-or-fetch "
                f"call(s) recorded, expected at least {min_search_calls}"
            )
    return tuple(violations)
