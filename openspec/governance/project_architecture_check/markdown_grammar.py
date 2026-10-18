"""The fence grammar has exactly one implementation.

The same grammar was hand-written five times before this rule: in the closeout tool, in
the specs checker, in three different shapes inside doc-hygiene, and again inside
change-guidance. Each rewrite brought its own class of misjudgement — an example read
as a task, a real heading hidden as an example, a checker going quietly blind, a valid
change falsely rejected. They were consolidated onto `markdown_fences.py`; this rule
keeps it that way.

What counts as re-implementing it
---------------------------------
A string literal containing a run of three or more backticks or tildes, used in a
*detection position*:

* an argument to a regex/search/split call (``compile``, ``match``, ``search``,
  ``findall``, ``finditer``, ``sub``, ``fullmatch``, ``startswith``, ``endswith``,
  ``find``, ``index``, ``count``, ``split``, ``partition``), or
* the left operand of ``in`` / ``not in``.

That narrowing is not a stylistic choice, it is measured. The naive rule — "any fence
literal in code" — flags **seven** places in this tree, all of them fixture *content*
in `doc_hygiene_battery/fixtures.py` (document snippets a test writes into a temporary
tree). A guard that cries wolf gets turned off, so fence literals used as content, in
messages, or in docstrings are deliberately out of scope. What is in scope is using the
marker as a *predicate*, which is the act of rewriting the grammar.

@impl PRS-001"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

from .contract import ContractViolation

CANONICAL_MODULE = "markdown_fences.py"

# Two files may spell the marker: the canonical implementation, and this rule — which
# necessarily *searches* for it. (On its first run the rule flagged itself, which is the
# mechanism working; the exemption is the honest resolution, not a workaround.)
EXEMPT_MODULES = frozenset({CANONICAL_MODULE, "markdown_grammar.py"})

# Calls whose string argument is being used to *find* something.
DETECTION_CALLS = frozenset({
    "compile", "match", "search", "findall", "finditer", "sub", "fullmatch",
    "startswith", "endswith", "find", "index", "count", "split", "partition",
})


def _module_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*.py") if "__pycache__" not in path.parts)


def _docstring_nodes(tree: ast.Module) -> set[int]:
    """The ids of string constants that are docstrings (they may describe fences)."""
    found: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                found.add(id(body[0].value))
    return found


def _fence_literals(tree: ast.Module) -> dict[int, ast.Constant]:
    """Code-level (non-docstring) string literals that spell a fence marker."""
    docstrings = _docstring_nodes(tree)
    return {
        id(node): node
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
        and ("```" in node.value or "~~~" in node.value)
    }


def _detection_uses(tree: ast.Module, fences: dict[int, ast.Constant]) -> Iterator[ast.Constant]:
    """The fence literals that are used as a predicate rather than as content."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if name in DETECTION_CALLS:
                arguments = [*node.args, *[keyword.value for keyword in node.keywords]]
                for argument in arguments:
                    for inner in ast.walk(argument):
                        if id(inner) in fences:
                            yield fences[id(inner)]
        elif isinstance(node, ast.Compare):
            for operator in node.ops:
                if isinstance(operator, (ast.In, ast.NotIn)):
                    for inner in ast.walk(node.left):
                        if id(inner) in fences:
                            yield fences[id(inner)]


def validate_single_fence_grammar(root: Path) -> None:
    """Reject hand-written fence grammar outside the canonical module."""
    directory = root / "openspec" / "governance"
    for path in _module_files(directory):
        if path.name in EXEMPT_MODULES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        fences = _fence_literals(tree)
        if not fences:
            continue
        for literal in _detection_uses(tree, fences):
            relative = path.relative_to(root).as_posix()
            raise ContractViolation(
                "markdown.grammar_duplicated",
                f"{relative}:{literal.lineno} hand-rolls the fence grammar; "
                f"use openspec/governance/{CANONICAL_MODULE}",
            )
