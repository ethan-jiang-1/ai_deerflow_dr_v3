"""No module-level import cycle inside a module directory.

Two cycles were found and repaired by hand before this rule existed: the doc-hygiene
entry against its control battery, and (inside the battery package) fixtures against
registry. Both were invisible to every other checker, and both are the kind of defect
that hides well — a module cycle works or fails depending on which side is imported
first, so a suite can stay green while the cycle is there.

Scope: the governance directory tree. The harness has its own layering matrix but no
cycle detection either; extending this rule there is a separate change, not a silent
widening of this one.

What counts as an edge
----------------------
Only imports that are *direct children of the module body*. An import inside a
function, a class, or an ``if`` (including ``if TYPE_CHECKING:``) is deferred and is
deliberately not an edge — deferred imports are this repository's established way of
breaking a cycle (``cli._self_test`` importing the battery, the pump's
``TYPE_CHECKING`` block). Counting them would flag the cure as the disease.

@impl PRS-001"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

from .contract import ContractViolation

GOVERNANCE_DIR = "openspec/governance"


def _module_files(directory: Path) -> list[Path]:
    """Every Python module under ``directory``, packages included."""
    return sorted(path for path in directory.rglob("*.py") if "__pycache__" not in path.parts)


def _key(path: Path, directory: Path) -> str:
    return path.relative_to(directory).as_posix()


def _candidates(name: str, package: Path, directory: Path) -> list[Path]:
    """The files a dotted name could mean, looked up inside the same directory tree."""
    base = package / name.replace(".", "/")
    return [base.with_suffix(".py"), base / "__init__.py"]


def _module_level_imports(tree: ast.Module) -> Iterator[ast.Import | ast.ImportFrom]:
    """Imports that execute when the module loads (so they are real edges)."""
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            yield node


def _edges(path: Path, directory: Path, present: set[str]) -> set[str]:
    """The module keys ``path`` imports at module level."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    package = path.parent
    found: set[str] = set()
    for node in _module_level_imports(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for candidate in _candidates(alias.name, directory, directory):
                    if candidate.is_file():
                        found.add(_key(candidate, directory))
        else:
            level = node.level or 0
            module = node.module or ""
            if level:
                base = package
                for _ in range(level - 1):
                    base = base.parent
                names = [module] if module else [alias.name for alias in node.names]
                for name in names:
                    for candidate in _candidates(name, base, directory):
                        if candidate.is_file():
                            found.add(_key(candidate, directory))
            else:
                for candidate in _candidates(module, directory, directory):
                    if candidate.is_file():
                        found.add(_key(candidate, directory))
                for alias in node.names:
                    for candidate in _candidates(f"{module}.{alias.name}", directory, directory):
                        if candidate.is_file():
                            found.add(_key(candidate, directory))
    return {key for key in found if key in present and key != _key(path, directory)}


def _components(graph: dict[str, set[str]]) -> list[list[str]]:
    """Tarjan's strongly connected components; only the cyclic ones are returned.

    Pairwise mutual-import checks miss a three-module ring (A -> B -> C -> A) where no
    pair points at each other, which is why this walks components instead.
    """
    index_of: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    counter = 0
    cyclic: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal counter
        index_of[node] = low[node] = counter
        counter += 1
        stack.append(node)
        on_stack.add(node)
        for neighbour in sorted(graph.get(node, ())):
            if neighbour not in index_of:
                strongconnect(neighbour)
                low[node] = min(low[node], low[neighbour])
            elif neighbour in on_stack:
                low[node] = min(low[node], index_of[neighbour])
        if low[node] == index_of[node]:
            component = []
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1:
                cyclic.append(sorted(component))

    for node in sorted(graph):
        if node not in index_of:
            strongconnect(node)
    return sorted(cyclic)


def validate_no_import_cycles(root: Path) -> None:
    """Reject any module-level import cycle inside the governance directory tree."""
    directory = root / GOVERNANCE_DIR
    files = _module_files(directory)
    present = {_key(path, directory) for path in files}
    graph = {_key(path, directory): _edges(path, directory, present) for path in files}
    for component in _components(graph):
        ring = " -> ".join([*component, component[0]])
        raise ContractViolation(
            "import.cycle",
            f"module-level import cycle in {GOVERNANCE_DIR}: {ring}",
        )
