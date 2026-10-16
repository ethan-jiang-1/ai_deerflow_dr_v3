"""Contract types and the closed declaration sets of the structure registry.

@impl PRS-001"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

MANIFEST_RELATIVE = PurePosixPath("openspec/governance/project-structure.toml")
INVENTORY_RELATIVE = PurePosixPath("openspec/governance/required-paths.toml")
MAIN_SPEC_RELATIVE = PurePosixPath("openspec/specs/project-structure/spec.md")
UPSTREAM_GITLINK_PATH = PurePosixPath("deerflow")
SPEC_REFERENCE = "> structure: openspec/governance/project-structure.toml"
GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_NAME = "deerflow_deep_research"
FIXTURE_PACKAGE_NAME = "deerflow_deep_research_fixtures"
CANONICAL_HARNESS_ROOT = PurePosixPath("deep_research_harness")
# Import-boundary layers: the four keys of the `[imports]` table, which are also the
# four canonical ownership layers (`runtime`, `domain`, `engine`, `agents`). The
# removed node-package grammar (`graph`/`nodes` layers, `[node_packages]`) cannot be
# re-declared: see load_manifest.
INTERNAL_LAYERS = {"domain", "engine", "agents", "runtime"}
# Non-weakenable internal-layer import directions, owned by PRS-001. The `[imports]`
# table cannot add an internal layer to a layer that these rules exclude. runtime is
# the declared composition home: its allowance reaches engine (composition deepens
# domain <- engine <- runtime; no cycle).
REQUIRED_INTERNAL_IMPORT_POLICY = {
    "domain": set(),
    "engine": {"domain"},
    "agents": {"domain"},
    "runtime": {"domain", "engine", "agents"},
}
CANONICAL_OWNERSHIP_LAYERS = frozenset(REQUIRED_INTERNAL_IMPORT_POLICY)
# Closed set of legal external top-level namespaces. External namespaces are
# TOML-authorized per layer; this whitelist only answers "is this external namespace
# real at all". Internal layers are validated separately above.
TOP_LEVEL_NAMESPACE_WHITELIST = {
    "stdlib",
    "pydantic",
    "deerflow",
    "langchain",
    "langgraph",
    "httpx",
    "httpx_sse",
    "openai",
    "yaml",  # Existing CLI configuration reader, now inside runtime entry assembly.
}


class ContractViolation(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class RequiredPath:
    path: PurePosixPath
    kind: str
    owner: str


@dataclass(frozen=True)
class UpstreamGitlink:
    path: PurePosixPath
    commit: str


@dataclass(frozen=True)
class StructureManifest:
    guide_path: PurePosixPath
    begin_marker: str
    end_marker: str
    upstream_gitlink: UpstreamGitlink
    source_root: PurePosixPath
    fixture_root: PurePosixPath | None
    fixture_package: str | None
    fixture_production_contracts: tuple[str, ...]
    fixture_external_namespaces: tuple[str, ...]
    fixture_recipe_class: str | None
    fixture_recipe_factories: tuple[str, ...]
    test_root: PurePosixPath
    ownership_layers: tuple[str, ...]
    forbidden_source_roots: tuple[PurePosixPath, ...]
    forbidden_shared_modules: tuple[str, ...]
    ignored_path: PurePosixPath
    ignored_entries: tuple[str, ...]
    required_paths: tuple[RequiredPath, ...]
    imports: dict[str, tuple[str, ...]]


def _expect_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractViolation("manifest.schema", f"{label} must be a TOML table")
    return value


def _expect_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractViolation("manifest.schema", f"{label} must be a non-empty string")
    return value


def _expect_string_list(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise ContractViolation("manifest.schema", f"{label} must be a non-empty string array")
    if len(set(value)) != len(value):
        raise ContractViolation("manifest.schema", f"{label} contains duplicates")
    return tuple(value)


def _relative_path(value: Any, label: str) -> PurePosixPath:
    raw = _expect_string(value, label)
    if raw.startswith("/") or PurePosixPath(raw).is_absolute():
        raise ContractViolation("path.absolute", f"{label} must be repository-relative: {raw}")
    if "\\" in raw:
        raise ContractViolation("path.normalization", f"{label} must use POSIX separators: {raw}")
    path = PurePosixPath(raw)
    if ".." in path.parts:
        raise ContractViolation("path.traversal", f"{label} contains parent traversal: {raw}")
    if raw in {"", "."} or path.as_posix() != raw:
        raise ContractViolation("path.normalization", f"{label} is not normalized: {raw}")
    return path
