#!/usr/bin/env python3
"""One root-resolution rule for the governance checkers.

Five callers resolved the repository root five ways: ``Path(argv[1])`` then
``__file__``-derived, an argparse default of ``Path.cwd()``, an
``argv``-or-``parents[3]`` helper, a bare ``parents[2]`` constant, and
``Path.cwd()`` in the closeout tool. The *rule* worth sharing is small and
uniform: an explicitly supplied value wins, otherwise the caller's own default,
and the result is resolved. The *default expression* stays with each caller
because it is part of that checker's invocation contract — the closeout tool is
meant to run from the repository it inspects, while the aggregate gate must work
from anywhere.

@impl PRS-001
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["resolve_root"]


def resolve_root(value: Path | str | None, *, default: Path) -> Path:
    """Resolve the project root: an explicit ``value`` wins over ``default``.

    ``value`` is ``None`` when the caller was given no root. Both branches are
    resolved, so callers can compare roots (and read subtrees) without worrying
    about symlinked or relative forms.
    """
    return (Path(value) if value is not None else default).resolve()
