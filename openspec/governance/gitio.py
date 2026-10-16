#!/usr/bin/env python3
"""One subprocess seam for the governance checkers' git calls.

Six checkers used to carry their own git wrapper, each with a different error
posture: one raised ``ContractViolation``, one swallowed ``OSError`` and returned
``None``, one had no guard at all, one returned bytes, and one lived in a test.
The duplication worth removing is *how the subprocess is invoked*; the difference
in *what a caller does when git is unavailable* is each checker's own error
semantics and stays with the caller.

``run_git`` therefore never raises and never interprets the exit code. The import
path is resolved by the caller: every entry point and every implementation
subpackage puts the governance directory on ``sys.path`` before importing this
module (see the bootstrap in ``check_project_architecture.py`` and the
``__init__`` of each ``*_check`` package).

@impl PRS-001
"""

from __future__ import annotations

import subprocess
from pathlib import Path

__all__ = ["run_git"]


def run_git(
    arguments: list[str],
    *,
    cwd: Path | str | None = None,
    text: bool = True,
) -> subprocess.CompletedProcess:
    """Invoke git and return the completed process, whatever its exit code.

    ``arguments`` excludes the leading ``git`` (it is added here). ``text=True``
    decodes stdout/stderr; ``text=False`` keeps bytes for callers that decode
    themselves. An unavailable git binary surfaces as ``OSError`` from the
    underlying call — the caller decides what that means.
    """
    return subprocess.run(
        ["git", *arguments],
        cwd=None if cwd is None else str(cwd),
        check=False,
        capture_output=True,
        text=text,
    )


def run_git_in(repository: Path, *arguments: str, text: bool = True) -> subprocess.CompletedProcess:
    """Convenience form: ``git -C <repository> <arguments...>``."""
    return run_git(["-C", str(repository), *arguments], text=text)
