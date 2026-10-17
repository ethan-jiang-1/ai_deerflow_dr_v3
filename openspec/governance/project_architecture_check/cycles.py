"""No module-level import cycle inside a module directory.

Two cycles were found and repaired by hand before this rule existed: the doc-hygiene
entry against its control battery, and (inside the battery package) fixtures against
registry. Both were invisible to every other checker, and both are the kind of defect
that hides well — a module cycle works or fails depending on which side is imported
first, so a suite can stay green while the cycle is there. The harness has its own
layering matrix, but layering answers "who may depend on whom", not "is there a ring".

What counts as an edge
----------------------
Only imports that are *direct children of the module body*. An import inside a
function, a class, or an ``if`` (including ``if TYPE_CHECKING:``) is deferred and is
deliberately not an edge — deferred imports are this repository's established way of
breaking a cycle (``cli._self_test`` importing the battery, the pump's
``TYPE_CHECKING`` block). Counting them would flag the cure as the disease.

How a name resolves
-------------------
A scope is a pair, because "where the modules are" and "where absolute names start"
are only accidentally the same place:

* ``openspec/governance`` — the directory is on ``sys.path``, so an absolute name is
  a sibling module (``from gitio import run_git``). Both fields are that directory.
* ``deep_research_harness/src/deerflow_deep_research`` — absolute names start at the
  package root (``from deerflow_deep_research.domain import bundle``), so the second
  field is ``deep_research_harness/src``. Getting this pair wrong does not fail loudly:
  every absolute import would resolve to nothing and the rule would quietly check only
  relative imports.

A dotted name resolves to the module *and* to its named submodules, since
``from pkg import mod`` imports ``pkg/mod.py`` as part of resolving — and, for a dotted
absolute name, to each package ``__init__.py`` on the way, which Python also imports.
Only targets inside ``module_root`` become graph nodes; anything else (the standard
library, third-party packages, sibling packages under ``src/``) is ignored.

@impl PRS-001"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from .contract import ContractViolation


@dataclass(frozen=True)
class Scope:
    """One directory tree to check.

    ``module_root`` is where the modules live; ``absolute_base`` is where an absolute
    dotted name starts. They are equal when the directory itself is on ``sys.path``.
    """

    module_root: str
    absolute_base: str


SCOPES: tuple[Scope, ...] = (
    Scope("openspec/governance", "openspec/governance"),
    Scope("deep_research_harness/src/deerflow_deep_research", "deep_research_harness/src"),
)


def _module_files(directory: Path) -> list[Path]:
    """Every Python module under ``directory``, packages included."""
    return sorted(path for path in directory.rglob("*.py") if "__pycache__" not in path.parts)


def _key(path: Path, module_root: Path) -> str:
    return path.relative_to(module_root).as_posix()


def _module_level_imports(tree: ast.Module) -> Iterator[ast.Import | ast.ImportFrom]:
    """Imports that execute when the module loads (so they are real edges)."""
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            yield node


def _resolve(name: str, base: Path, module_root: Path, present: set[str]) -> str | None:
    """The graph key for a dotted name, or None when it is outside this scope."""
    candidate = base.joinpath(*name.split(".")) if name else base
    for path in (candidate.with_suffix(".py"), candidate / "__init__.py"):
        if path.is_file():
            try:
                key = _key(path, module_root)
            except ValueError:
                return None  # resolves outside the scope: not a node here
            return key if key in present else None
    return None


def _absolute_targets(node: ast.ImportFrom | ast.Import, base: Path, module_root: Path,
                      present: set[str]) -> set[str]:
    """Targets of an absolute import, including the parents Python imports on the way."""
    found: set[str] = set()
    if isinstance(node, ast.Import):
        modules = [alias.name for alias in node.names]
    else:
        module = node.module or ""
        names = [alias.name for alias in node.names]
        modules = [module, *[f"{module}.{name}" for name in names]] if module else names
    for dotted in modules:
        if not dotted:
            continue
        # every package on the way is imported too: a.b.c pulls in a and a.b
        parts = dotted.split(".")
        for depth in range(1, len(parts) + 1):
            key = _resolve(".".join(parts[:depth]), base, module_root, present)
            if key:
                found.add(key)
    return found


def _relative_targets(node: ast.ImportFrom, package: Path, module_root: Path,
                      present: set[str]) -> set[str]:
    base = package
    for _ in range((node.level or 1) - 1):
        base = base.parent
    found: set[str] = set()
    module = node.module or ""
    names = [alias.name for alias in node.names]
    for dotted in ([module] if module else []) + ([f"{module}.{name}" for name in names] if module else names):
        key = _resolve(dotted, base, module_root, present)
        if key:
            found.add(key)
    return found


def _edges(path: Path, scope: Scope, root: Path, present: set[str]) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    module_root = root / scope.module_root
    absolute_base = root / scope.absolute_base
    here = _key(path, module_root)
    found: set[str] = set()
    for node in _module_level_imports(tree):
        if isinstance(node, ast.Import):
            found |= _absolute_targets(node, absolute_base, module_root, present)
        elif node.level:
            found |= _relative_targets(node, path.parent, module_root, present)
        else:
            found |= _absolute_targets(node, absolute_base, module_root, present)
    return {key for key in found if key in present and key != here}


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
    """Reject any module-level import cycle inside a checked scope."""
    for scope in SCOPES:
        module_root = root / scope.module_root
        files = _module_files(module_root)
        present = {_key(path, module_root) for path in files}
        graph = {_key(path, module_root): _edges(path, scope, root, present) for path in files}
        for component in _components(graph):
            ring = " -> ".join([*component, component[0]])
            raise ContractViolation(
                "import.cycle",
                f"module-level import cycle in {scope.module_root}: {ring}",
            )
