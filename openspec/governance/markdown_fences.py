#!/usr/bin/env python3
"""One rule for "what is a fenced code block" (CommonMark 4.5, and 4.4 for the edge).

Two governance tools used to answer that question differently, and the older answer
was the more permissive one: it treated a four-space-indented fence and a backtick
fence whose info string contains a backtick as fences, so it blanked headings that
CommonMark says are real (BUG-004). The rule lives here once, per the spec:

* An opening fence is up to three spaces of indentation, then three or more backticks
  or tildes, then an optional info string. A **backtick** fence's info string may not
  contain a backtick — such a line is not a fence at all. Four spaces of indentation is
  an *indented code block* (4.4), not a fence.
* A closing fence is the **same character** repeated **at least as many times** as the
  opening fence, followed by spaces or tabs only.
* An unclosed fence runs to the end of the document, which is why the scan is a single
  pass rather than a search for a partner line.

Imported by name: these scripts run with the governance directory on ``sys.path`` (as
a script, that is automatic; the governance tests insert it explicitly).

@impl PRS-001
"""

from __future__ import annotations

import re
from collections.abc import Iterator

# An opening-or-closing candidate: up to three spaces, then three or more backticks or
# tildes, then whatever follows (an info string when opening, only whitespace when
# closing).
FENCE_LINE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<rest>.*)$")


def fence_flags(lines: list[str]) -> list[bool]:
    """One flag per line: True when the line belongs to a fenced code block.

    The opening fence, its content, and the closing fence are all flagged, so callers
    that blank the flagged lines keep the surrounding line numbering intact.
    """
    flags: list[bool] = []
    open_fence: str | None = None
    for line in lines:
        match = FENCE_LINE.match(line)
        if open_fence is None:
            # A backtick info string may not contain a backtick (4.5): if it does, the
            # line is ordinary text, not a fence.
            opens = match is not None and not (
                match.group("fence").startswith("`") and "`" in match.group("rest")
            )
            flags.append(bool(opens))
            if opens:
                open_fence = match.group("fence")
            continue
        flags.append(True)
        if (
            match is not None
            and match.group("fence")[0] == open_fence[0]
            and len(match.group("fence")) >= len(open_fence)
            and not match.group("rest").strip()
        ):
            open_fence = None
    return flags


def iter_outside_fences(lines: list[str]) -> Iterator[str]:
    """Yield only the lines that are not part of a fenced code block."""
    for line, fenced in zip(lines, fence_flags(lines), strict=True):
        if not fenced:
            yield line


def strip_fenced_code_blocks(content: str) -> str:
    """Blank out fenced code blocks, keeping every line and its number.

    Line numbering is the contract this function exists for: callers report violations
    by line, so removing the fenced lines outright would silently shift every later
    line number.
    """
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(
        "" if fenced else line for line, fenced in zip(lines, fence_flags(lines), strict=True)
    )
