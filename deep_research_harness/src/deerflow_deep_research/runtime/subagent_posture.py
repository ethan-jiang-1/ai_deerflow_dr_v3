"""Subagent posture guard: the depth self-check for declared custom subagents.

Pure stdlib, dependency-free (the unit gate environment has no YAML parser). The
scanning is fail-closed: a shape the scanner cannot parse is a red, never a silent
pass. The wiring plan's decision 5 rules the location (config.yaml ``subagents.*``)
and the exclusion (``task`` must be in every custom subagent's ``disallowed_tools`` —
the framework schema does not enforce it, so the harness asserts it).

@impl DEW-001"""

from __future__ import annotations

import re

from ..domain.state_machine import RuleViolation

POSTURE_MARK = "no custom subagent types"
_NAME_RE = re.compile(r"^\s{4}- name:\s*(\S+)")
_DISALLOWED_RE = re.compile(r"^\s{6}disallowed_tools:\s*(\[[^\]]*\])?\s*$")
_LIST_ITEM_RE = re.compile(r"^\s{6}-\s*(\S+)\s*$")


def _strip_comments(text: str) -> list[str]:
    """Drop comment lines (the posture block is prose-in-comments and must never be
    mistaken for a declaration) while keeping indentation of live lines."""

    lines: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        lines.append(line.rstrip())
    return lines


def declared_custom_agents(config_text: str) -> list[dict]:
    """Return the declared custom subagents as ``{"name": str, "disallowed_tools":
    list[str]}``. Raises :class:`RuleViolation` on an unparseable ``subagents`` block
    (fail closed)."""

    declared: list[dict] = []
    in_subagents = False
    in_custom = False
    current: dict | None = None
    collecting_list = False

    for line in _strip_comments(config_text):
        if not line.strip():
            continue
        if re.match(r"^subagents:\s*$", line):
            in_subagents = True
            in_custom = False
            current = None
            continue
        if re.match(r"^\S", line):
            in_subagents = False
            in_custom = False
            current = None
            continue
        if not in_subagents:
            continue
        if re.match(r"^  custom_agents:\s*$", line):
            in_custom = True
            current = None
            continue
        if in_custom:
            if re.match(r"^  \S", line):
                in_custom = False
                current = None
                continue
            name_match = _NAME_RE.match(line)
            if name_match:
                current = {"name": name_match.group(1), "disallowed_tools": []}
                declared.append(current)
                collecting_list = False
                continue
            disallowed_match = _DISALLOWED_RE.match(line)
            if disallowed_match and current is not None:
                inline = disallowed_match.group(1)
                if inline:
                    current["disallowed_tools"] = [
                        item.strip("[]\"' ") for item in inline.strip("[]").split(",") if item.strip("[]\"' ")
                    ]
                collecting_list = True
                continue
            list_item = _LIST_ITEM_RE.match(line)
            if list_item and current is not None and collecting_list:
                current["disallowed_tools"].append(list_item.group(1))
                continue
            if re.match(r"^    \S", line):
                raise RuleViolation(
                    f"unparseable subagents declaration near {line.strip()!r} — refusing "
                    "to guess (the posture guard fails closed)"
                )
    return declared


def check_custom_agents(config_text: str, *, source: str = "config") -> list[dict]:
    """The depth self-check: every declared custom subagent must exclude ``task`` from
    its ``disallowed_tools``. Returns the declared entries; raises on any violation,
    naming the config file, the offending subagent, and the remedy."""

    declared = declared_custom_agents(config_text)
    for agent in declared:
        if "task" not in agent["disallowed_tools"]:
            raise RuleViolation(
                f"{source}: custom subagent {agent['name']!r} must exclude 'task' via "
                "disallowed_tools — the framework schema does not enforce it, the "
                "harness asserts it (wiring plan decision 5). Remedy: add 'task' to "
                "the agent's disallowed_tools, or remove the declaration and bring it "
                "back through an owning change."
            )
    return declared
