#!/usr/bin/env python3
"""Release-face guard (RLF-001): the minimal release contract, checked loudly.

The release face is exactly ``deep_research_harness/`` plus the pinned ``deerflow/``
gitlink. This checker validates the current tree against that contract and exits
non-zero, naming the violated fact, whenever the face is broken:

1. gitlink present, and its checked-out HEAD equals the commit pinned by the
   structural manifest (``openspec/governance/project-structure.toml``);
2. sibling layout: the gitlink sits beside the harness, and every dependency source
   declared in ``deep_research_harness/pyproject.toml`` ``[tool.uv.sources]``
   resolves inside the release face;
3. no harness runtime/CLI source file references development-face material
   (``openspec`` or ``_backlog``);
4. every playbook routing target named by ``COMMANDS.md`` exists under
   ``deep_research_harness/docs/playbook/``.

Usage: ``python3 openspec/governance/check_release_face.py [repo-root]``.
The slow full cold-start lane (fresh two-piece checkout through ``uv sync``,
``make verify``, and a fixture run) is documented in
``deep_research_harness/docs/playbook/run-research.md`` as the on-demand release proof.

@impl RLF-001
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

HARNESS = "deep_research_harness"
GITLINK = "deerflow"
MANIFEST_REL = "openspec/governance/project-structure.toml"
# Coupling shapes only: import statements and path references to development-face
# material. Prose mentions inside docstrings (e.g. a register entry describing what
# the harness never links) are not coupling and must stay green.
SCAN_PATTERNS = (
    re.compile(r"^\s*(from|import)\s+(openspec|_backlog)\b", re.MULTILINE),
    re.compile(r"[\"'`](openspec|_backlog)/"),
)
ROUTING_RE = re.compile(r"docs/playbook/[\w.-]+\.md")


def _repo_root(argv: list[str]) -> Path:
    if len(argv) > 1:
        return Path(argv[1]).resolve()
    return Path(__file__).resolve().parents[2]


def _gitlink_head(gitlink_dir: Path) -> str | None:
    """The checked-out HEAD sha of the gitlink working tree, or None."""
    try:
        result = subprocess.run(
            ["git", "-C", str(gitlink_dir), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha if re.fullmatch(r"[0-9a-f]{40}", sha) else None


def _check_gitlink(root: Path, manifest: dict) -> list[str]:
    problems: list[str] = []
    gitlink_dir = root / GITLINK
    if not gitlink_dir.is_dir():
        return [f"release face incomplete: {GITLINK}/ is missing "
                f"(recover with: git submodule update --init)"]
    pinned = manifest.get("upstream_gitlink", {}).get("commit")
    head = _gitlink_head(gitlink_dir)
    if head is None:
        return [f"gitlink unreadable: cannot resolve {GITLINK}/ HEAD"]
    if head != pinned:
        problems.append(
            f"gitlink pin drift: {GITLINK}/ HEAD {head} != pinned {pinned} "
            f"({MANIFEST_REL})"
        )
    return problems


def _check_dependency_sources(root: Path) -> list[str]:
    """Every [tool.uv.sources] path must resolve inside the release face."""
    problems: list[str] = []
    pyproject = root / HARNESS / "pyproject.toml"
    if not pyproject.is_file():
        return [f"release face incomplete: {HARNESS}/pyproject.toml is missing"]
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    for name, entry in sorted(sources.items()):
        rel = entry.get("path") if isinstance(entry, dict) else None
        if not rel:
            continue
        resolved = (pyproject.parent / rel).resolve()
        inside = (
            resolved == (root / HARNESS).resolve()
            or (root / HARNESS).resolve() in resolved.parents
            or resolved == (root / GITLINK).resolve()
            or (root / GITLINK).resolve() in resolved.parents
        )
        if not inside:
            problems.append(
                f"dependency source escapes the release face: {name} -> {rel} "
                f"(pyproject.toml [tool.uv.sources])"
            )
    return problems


def _check_dev_face_references(root: Path) -> list[str]:
    problems: list[str] = []
    scan_targets = sorted((root / HARNESS / "src").rglob("*.py")) + [
        root / HARNESS / "cli.py"
    ]
    for path in scan_targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in SCAN_PATTERNS):
            problems.append(
                f"development-face reference in shipped source: {path.relative_to(root)} "
                f"(harness code must not import or path-reference openspec/_backlog)"
            )
    return problems


def _check_menu_routing(root: Path) -> list[str]:
    problems: list[str] = []
    commands = root / HARNESS / "COMMANDS.md"
    if not commands.is_file():
        return [f"entry face missing: {HARNESS}/COMMANDS.md"]
    playbook_dir = commands.parent / "docs" / "playbook"
    for match in ROUTING_RE.findall(commands.read_text(encoding="utf-8")):
        if not (commands.parent / match).is_file():
            problems.append(
                f"dangling menu routing target: {match} "
                f"(expected under {HARNESS}/docs/playbook/)"
            )
    if playbook_dir.is_dir():
        return problems
    joined = "\n".join(problems)
    if "dangling" in joined:
        return problems
    return problems


def main(argv: list[str]) -> int:
    root = _repo_root(argv)
    manifest_path = root / MANIFEST_REL
    if not manifest_path.is_file():
        print(f"release-face guard: {MANIFEST_REL} is missing", file=sys.stdout)
        return 1
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))

    problems: list[str] = []
    problems += _check_gitlink(root, manifest)
    problems += _check_dependency_sources(root)
    problems += _check_dev_face_references(root)
    problems += _check_menu_routing(root)

    if problems:
        print("release-face guard: violations found")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("release-face guard passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
