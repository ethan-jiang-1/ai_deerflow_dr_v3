"""Doc rules: generated guide block, spec authority, declared paths, source root.

@impl PRS-001"""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

from .contract import (
    MAIN_SPEC_RELATIVE,
    SPEC_REFERENCE,
    ContractViolation,
    StructureManifest,
)

def _directory_display(path: PurePosixPath) -> str:
    return f"{path.as_posix()}/"


def render_guide_block(manifest: StructureManifest) -> str:
    lines = [
        manifest.begin_marker,
        "## Canonical Structure Locator",
        "",
        "Exact inventory: the structure registry declared by the owning "
        "`project-structure` spec.",
        "",
        f"- Source root: `{_directory_display(manifest.source_root)}`",
        *(
            [f"- Fixture source root: `{_directory_display(manifest.fixture_root)}`"]
            if manifest.fixture_root is not None
            else []
        ),
        f"- Test root: `{_directory_display(manifest.test_root)}`",
        "- Ownership layers: " + ", ".join(f"`{layer}`" for layer in manifest.ownership_layers),
        "- Validate: repository architecture governance (`check_project_architecture.py`)",
        manifest.end_marker,
    ]
    return "\n".join(lines)


def _validate_guide(root: Path, manifest: StructureManifest) -> None:
    path = root / manifest.guide_path
    if not path.is_file():
        raise ContractViolation("guide.marker_missing", f"module guide is missing: {manifest.guide_path}")
    text = path.read_text(encoding="utf-8")
    begin_count = text.count(manifest.begin_marker)
    end_count = text.count(manifest.end_marker)
    if begin_count == 0 or end_count == 0:
        raise ContractViolation("guide.marker_missing", "module guide lacks the generated structure markers")
    if begin_count != 1 or end_count != 1:
        raise ContractViolation(
            "guide.marker_duplicate",
            "module guide must contain exactly one generated structure block",
        )
    start = text.index(manifest.begin_marker)
    end = text.index(manifest.end_marker, start) + len(manifest.end_marker)
    actual = text[start:end]
    expected = render_guide_block(manifest).rstrip("\n")
    if actual != expected:
        raise ContractViolation("guide.drift", "generated module-guide block does not match the structure registry")


def _validate_spec_authority(root: Path, manifest: StructureManifest) -> None:
    main_spec = root / MAIN_SPEC_RELATIVE
    if main_spec.is_file():
        text = main_spec.read_text(encoding="utf-8")
        reference_count = text.count(SPEC_REFERENCE)
        if reference_count == 0:
            raise ContractViolation("spec.reference_missing", f"active main spec lacks {SPEC_REFERENCE!r}")
        if reference_count != 1:
            raise ContractViolation("spec.reference_ambiguous", "active main spec has duplicate structure references")
        return

    changes_dir = root / "openspec" / "changes"
    active_specs = sorted(changes_dir.glob("*/specs/project-structure/spec.md")) if changes_dir.is_dir() else []
    owning_specs: list[Path] = []
    referenced_specs: list[Path] = []
    for spec_path in active_specs:
        text = spec_path.read_text(encoding="utf-8")
        owning_specs.append(spec_path)
        if SPEC_REFERENCE in text:
            referenced_specs.append(spec_path)

    if len(referenced_specs) > 1 or len(owning_specs) > 1:
        raise ContractViolation("spec.reference_ambiguous", "more than one active delta claims structural authority")
    if len(referenced_specs) == 1 and len(owning_specs) == 1:
        return
    if owning_specs:
        raise ContractViolation("spec.reference_missing", f"pending owning delta lacks {SPEC_REFERENCE!r}")

    archived_specs = root.glob("openspec/changes/archive/*/specs/project-structure/spec.md")
    if any(SPEC_REFERENCE in path.read_text(encoding="utf-8") for path in archived_specs):
        raise ContractViolation("spec.archived_only", "an archived delta cannot be the active structural authority")
    raise ContractViolation("spec.reference_missing", "no lifecycle-appropriate project-structure spec was found")


def _validate_required_paths(root: Path, manifest: StructureManifest) -> None:
    for item in manifest.required_paths:
        path = root / item.path
        if not path.exists():
            raise ContractViolation("path.missing", f"required {item.kind} is missing: {item.path}")
        if item.kind == "file" and not path.is_file():
            raise ContractViolation("path.kind", f"required file is not a file: {item.path}")
        if item.kind == "directory" and not path.is_dir():
            raise ContractViolation("path.kind", f"required directory is not a directory: {item.path}")


def _validate_ignored_paths(root: Path, manifest: StructureManifest) -> None:
    path = root / manifest.ignored_path
    try:
        actual_entries = tuple(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeError) as exc:
        raise ContractViolation("ignore.unreadable", f"cannot read ignored-path policy: {manifest.ignored_path}") from exc
    if actual_entries != manifest.ignored_entries:
        raise ContractViolation(
            "ignore.entries",
            f"ignore entries must exactly match the registered policy: {manifest.ignored_path}",
        )


def _validate_single_source_root(root: Path, manifest: StructureManifest) -> None:
    legacy_root = root / "agent"
    if legacy_root.exists() or legacy_root.is_symlink():
        raise ContractViolation(
            "source.compatibility_root",
            "legacy compatibility root is forbidden: agent",
        )

    source_parents = {manifest.source_root.parent: manifest.source_root.name}
    if manifest.fixture_root is not None:
        source_parents[manifest.fixture_root.parent] = manifest.fixture_root.name
    source_container = manifest.source_root.parent.parent
    registered_source_roots = set(source_parents)
    container_path = root / source_container
    if container_path.is_dir():
        for child in container_path.iterdir():
            candidate = PurePosixPath(child.relative_to(root).as_posix())
            if child.is_dir() and child.name.startswith("src") and candidate not in registered_source_roots:
                raise ContractViolation(
                    "source.unregistered_root",
                    f"unregistered Deep Research source root found: {candidate}",
                )
    for source_parent, package_name in source_parents.items():
        parent_path = root / source_parent
        if not parent_path.is_dir():
            continue
        for child in parent_path.iterdir():
            if child.name == "__pycache__" or not child.is_dir() or child.name == package_name:
                continue
            if (child / "__init__.py").is_file():
                raise ContractViolation(
                    "source.unregistered_root",
                    f"unregistered package under source root {source_parent}: {child.name}",
                )

    excluded = {
        PurePosixPath(".git"),
        PurePosixPath(".venv"),
        PurePosixPath("_backlog"),
        manifest.upstream_gitlink.path,
        PurePosixPath("frontend/.next"),
        PurePosixPath("node_modules"),
        PurePosixPath("openspec/changes/archive"),
        manifest.test_root / "fixtures",
    }

    def is_excluded(path: PurePosixPath) -> bool:
        return any(path == prefix or prefix in path.parents for prefix in excluded)

    for current, directories, _files in os.walk(root):
        relative_current = Path(current).relative_to(root)
        current_posix = PurePosixPath(relative_current.as_posix()) if relative_current.parts else PurePosixPath(".")
        directories[:] = [
            directory
            for directory in directories
            if not is_excluded(
                (current_posix / directory) if current_posix != PurePosixPath(".") else PurePosixPath(directory)
            )
        ]
        for directory in directories:
            registered_names = {manifest.source_root.name}
            if manifest.fixture_root is not None:
                registered_names.add(manifest.fixture_root.name)
            if directory not in registered_names:
                continue
            candidate = current_posix / directory if current_posix != PurePosixPath(".") else PurePosixPath(directory)
            if candidate == manifest.source_root or candidate == manifest.fixture_root:
                continue
            raise ContractViolation("source.second_root", f"non-canonical package source root found: {candidate}")
