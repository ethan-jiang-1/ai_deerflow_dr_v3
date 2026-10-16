"""Manifest loading: parse the registry, validate the contract, build the value.

@impl PRS-001"""

from __future__ import annotations

import tomllib
from pathlib import Path, PurePosixPath

from .contract import (
    CANONICAL_HARNESS_ROOT,
    CANONICAL_OWNERSHIP_LAYERS,
    ContractViolation,
    FIXTURE_PACKAGE_NAME,
    GIT_COMMIT_RE,
    INVENTORY_RELATIVE,
    INTERNAL_LAYERS,
    MANIFEST_RELATIVE,
    PACKAGE_NAME,
    REQUIRED_INTERNAL_IMPORT_POLICY,
    RequiredPath,
    StructureManifest,
    TOP_LEVEL_NAMESPACE_WHITELIST,
    UPSTREAM_GITLINK_PATH,
    UpstreamGitlink,
    _expect_mapping,
    _expect_string,
    _expect_string_list,
    _relative_path,
)

def _parse_fixture_declaration(
    fixture_root_raw: Any,
    fixture_package_raw: Any,
    fixture_imports_raw: Any,
    source_root: PurePosixPath,
) -> tuple[PurePosixPath | None, str | None, tuple[str, ...], tuple[str, ...], str | None, tuple[str, ...]]:
    """Validate the fixture declaration and return its six derived values.

    Returns ``(fixture_root, fixture_package, production_contracts,
    external_namespaces, recipe_class, recipe_factories)``. A registry that
    declares no fixture returns all-empty values; a half-declared fixture fails
    loudly rather than silently disabling the fixture import boundary.
    """

    if fixture_root_raw is None and fixture_package_raw is None:
        fixture_root = None
        fixture_package = None
        if fixture_imports_raw is not None:
            raise ContractViolation("manifest.schema", "fixture_imports requires a registered fixture root")
        fixture_production_contracts: tuple[str, ...] = ()
        fixture_external_namespaces: tuple[str, ...] = ()
        fixture_recipe_class = None
        fixture_recipe_factories: tuple[str, ...] = ()
    elif fixture_root_raw is None or fixture_package_raw is None:
        raise ContractViolation("manifest.schema", "fixture_root and fixture_package must be declared together")
    else:
        fixture_root = _relative_path(fixture_root_raw, "package.fixture_root")
        fixture_package = _expect_string(fixture_package_raw, "package.fixture_package")
        if fixture_package != FIXTURE_PACKAGE_NAME or fixture_root.name != fixture_package:
            raise ContractViolation("manifest.schema", "fixture root must use the registered distinct package name")
        if fixture_root == source_root:
            raise ContractViolation("manifest.schema", "fixture root must differ from production source root")
        expected_fixture_root = source_root.parent.parent / "src_fixtures" / fixture_package
        if fixture_root != expected_fixture_root:
            raise ContractViolation("manifest.schema", "fixture root must use the registered src_fixtures location")

        fixture_imports = _expect_mapping(fixture_imports_raw, "fixture_imports")
        fixture_production_contracts = _expect_string_list(
            fixture_imports.get("production_contracts"),
            "fixture_imports.production_contracts",
        )
        if any(
            not contract.startswith(f"{PACKAGE_NAME}.") or len(contract.split(".")) < 3
            for contract in fixture_production_contracts
        ):
            raise ContractViolation(
                "manifest.schema",
                "fixture_imports.production_contracts must name production contract modules",
            )
        fixture_external_namespaces = _expect_string_list(
            fixture_imports.get("external_namespaces"),
            "fixture_imports.external_namespaces",
        )
        if any("." in namespace for namespace in fixture_external_namespaces):
            raise ContractViolation(
                "manifest.schema",
                "fixture_imports.external_namespaces must contain top-level namespaces",
            )
        fixture_recipe_class = _expect_string(fixture_imports.get("recipe_class"), "fixture_imports.recipe_class")
        expected_recipe_class = f"{PACKAGE_NAME}.runtime.research.ResearchGraphRecipe"
        if fixture_recipe_class != expected_recipe_class:
            raise ContractViolation(
                "manifest.schema",
                "fixture_imports.recipe_class must name the documented recipe composition class",
            )
        if fixture_recipe_class in fixture_production_contracts:
            raise ContractViolation(
                "manifest.schema",
                "fixture recipe class must not widen the production-contract import allowlist",
            )
        fixture_recipe_factories = _expect_string_list(
            fixture_imports.get("recipe_factories"),
            "fixture_imports.recipe_factories",
        )
        if fixture_recipe_factories != ("from_adapters",):
            raise ContractViolation(
                "manifest.schema",
                "fixture recipe composition may permit only ResearchGraphRecipe.from_adapters",
            )



    return (
        fixture_root,
        fixture_package,
        fixture_production_contracts,
        fixture_external_namespaces,
        fixture_recipe_class,
        fixture_recipe_factories,
    )


def _parse_inventory(
    inventory_data: dict[str, Any],
    forbidden_source_roots: tuple[PurePosixPath, ...],
    ignored_path: PurePosixPath,
) -> list[RequiredPath]:
    """Validate and flatten an already-loaded inventory into required-path entries.

    Owns the inventory document's own schema (version, contract, group table) plus
    the cross-checks that the ignored-path policy and the inventory itself are
    registered as required files. Loading the file is the caller's business, which
    keeps this helper a pure function of the parsed document.
    """
    if inventory_data.get("schema_version") != 1:
        raise ContractViolation("inventory.schema", "inventory schema_version must be integer 1")
    if inventory_data.get("contract") != "project-structure-inventory":
        raise ContractViolation(
            "inventory.schema",
            "inventory contract must be 'project-structure-inventory'",
        )
    raw_path_sections = inventory_data.get("paths")
    if not isinstance(raw_path_sections, dict) or not raw_path_sections:
        raise ContractViolation(
            "inventory.schema",
            "inventory must declare a non-empty [paths.<group>] section table",
        )
    required_paths: list[RequiredPath] = []
    seen_paths: set[PurePosixPath] = set()
    for section_owner in sorted(raw_path_sections):
        section = _expect_mapping(raw_path_sections[section_owner], f"paths.{section_owner}")
        for kind, key in (("file", "files"), ("directory", "directories")):
            raw_values = section.get(key)
            if raw_values is None:
                continue
            for item_path_raw in _expect_string_list(raw_values, f"paths.{section_owner}.{key}"):
                item_path = _relative_path(item_path_raw, f"paths.{section_owner}.{key}")
                if item_path in seen_paths:
                    raise ContractViolation("path.duplicate", f"required path appears more than once: {item_path}")
                seen_paths.add(item_path)
                if any(item_path == root_path or root_path in item_path.parents for root_path in forbidden_source_roots):
                    raise ContractViolation(
                        "path.forbidden_owner",
                        f"required path is under an upstream root: {item_path}",
                    )
                required_paths.append(RequiredPath(item_path, kind, section_owner))
    if not required_paths:
        raise ContractViolation("manifest.schema", "required_paths must be a non-empty set of inventory entries")
    if not any(item.path == ignored_path and item.kind == "file" for item in required_paths):
        raise ContractViolation(
            "manifest.schema",
            "ignored_paths.path must be registered as a required file",
        )
    if not any(item.path == INVENTORY_RELATIVE and item.kind == "file" for item in required_paths):
        raise ContractViolation(
            "inventory.unregistered",
            "the required-path inventory must be registered as a required file",
        )



    return required_paths


def load_manifest(root: Path) -> StructureManifest:
    path = root / MANIFEST_RELATIVE
    if not path.is_file():
        raise ContractViolation("manifest.missing", f"structure registry is missing: {MANIFEST_RELATIVE}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ContractViolation("manifest.parse", f"cannot parse {MANIFEST_RELATIVE}: {exc}") from exc

    if data.get("schema_version") != 1:
        raise ContractViolation("manifest.schema", "schema_version must be integer 1")
    if data.get("contract") != "project-structure":
        raise ContractViolation("manifest.schema", "contract must be 'project-structure'")

    upstream_gitlink_raw = data.get("upstream_gitlink")
    if not isinstance(upstream_gitlink_raw, dict):
        raise ContractViolation("gitlink.schema", "upstream_gitlink must be a TOML table")
    upstream_gitlink_data = _expect_mapping(upstream_gitlink_raw, "upstream_gitlink")
    if set(upstream_gitlink_data) != {"path", "commit"}:
        raise ContractViolation("gitlink.schema", "upstream_gitlink must contain exactly path and commit")
    upstream_gitlink_path = _relative_path(upstream_gitlink_data.get("path"), "upstream_gitlink.path")
    if upstream_gitlink_path != UPSTREAM_GITLINK_PATH:
        raise ContractViolation("gitlink.path", f"upstream_gitlink.path must be {UPSTREAM_GITLINK_PATH}")
    upstream_gitlink_commit = _expect_string(upstream_gitlink_data.get("commit"), "upstream_gitlink.commit")
    if not GIT_COMMIT_RE.fullmatch(upstream_gitlink_commit):
        raise ContractViolation("gitlink.commit", "upstream_gitlink.commit must be a lower-case 40-hex identifier")
    upstream_gitlink = UpstreamGitlink(path=upstream_gitlink_path, commit=upstream_gitlink_commit)

    package = _expect_mapping(data.get("package"), "package")
    source_root = _relative_path(package.get("source_root"), "package.source_root")
    expected_source_root = CANONICAL_HARNESS_ROOT / "src" / PACKAGE_NAME
    if source_root != expected_source_root:
        raise ContractViolation(
            "source.canonical_root",
            f"package.source_root must be {expected_source_root}",
        )
    fixture_root_raw = package.get("fixture_root")
    fixture_package_raw = package.get("fixture_package")
    fixture_imports_raw = data.get("fixture_imports")
    (
        fixture_root,
        fixture_package,
        fixture_production_contracts,
        fixture_external_namespaces,
        fixture_recipe_class,
        fixture_recipe_factories,
    ) = _parse_fixture_declaration(
        fixture_root_raw, fixture_package_raw, fixture_imports_raw, source_root
    )
    test_root = _relative_path(package.get("test_root"), "package.test_root")
    expected_test_root = CANONICAL_HARNESS_ROOT / "tests"
    if test_root != expected_test_root:
        raise ContractViolation(
            "test.canonical_root",
            f"package.test_root must be {expected_test_root}",
        )
    ownership_layers = _expect_string_list(package.get("ownership_layers"), "package.ownership_layers")
    if set(ownership_layers) != CANONICAL_OWNERSHIP_LAYERS:
        raise ContractViolation(
            "manifest.schema",
            "ownership_layers must declare exactly the canonical layers runtime, domain, "
            "engine, and agents; the removed node-package grammar (graph/nodes) cannot "
            "be re-declared",
        )
    forbidden_source_roots = tuple(
        _relative_path(item, "package.forbidden_source_roots")
        for item in _expect_string_list(package.get("forbidden_source_roots"), "package.forbidden_source_roots")
    )
    forbidden_shared_modules = _expect_string_list(
        package.get("forbidden_shared_modules"), "package.forbidden_shared_modules"
    )

    ignored_paths = _expect_mapping(data.get("ignored_paths"), "ignored_paths")
    ignored_path = _relative_path(ignored_paths.get("path"), "ignored_paths.path")
    expected_ignored_path = CANONICAL_HARNESS_ROOT / ".gitignore"
    if ignored_path != expected_ignored_path:
        raise ContractViolation(
            "ignore.canonical_root",
            f"ignored_paths.path must be {expected_ignored_path}",
        )
    ignored_entries = _expect_string_list(ignored_paths.get("entries"), "ignored_paths.entries")
    if any(
        not entry.endswith("/")
        or entry.startswith("/")
        or "\\" in entry
        or ".." in PurePosixPath(entry[:-1]).parts
        for entry in ignored_entries
    ):
        raise ContractViolation(
            "manifest.schema",
            "ignored_paths.entries must contain normalized repository-local directory entries",
        )

    inventory_raw = data.get("inventory")
    if not isinstance(inventory_raw, dict):
        raise ContractViolation("inventory.schema", "inventory must be a TOML table")
    inventory_path = _relative_path(inventory_raw.get("path"), "inventory.path")
    inventory_path = _relative_path(inventory_raw.get("path"), "inventory.path")
    if inventory_path != INVENTORY_RELATIVE:
        raise ContractViolation(
            "inventory.path",
            f"inventory.path must be {INVENTORY_RELATIVE.as_posix()}",
        )
    inventory_file = root / INVENTORY_RELATIVE
    if not inventory_file.is_file():
        raise ContractViolation("inventory.missing", f"required-path inventory is missing: {INVENTORY_RELATIVE}")
    try:
        inventory_data = tomllib.loads(inventory_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ContractViolation("inventory.parse", f"cannot parse {INVENTORY_RELATIVE}: {exc}") from exc
    required_paths = _parse_inventory(inventory_data, forbidden_source_roots, ignored_path)
    raw_imports = _expect_mapping(data.get("imports"), "imports")
    imports = {name: _expect_string_list(values, f"imports.{name}") for name, values in raw_imports.items()}
    if set(imports) != CANONICAL_OWNERSHIP_LAYERS:
        raise ContractViolation(
            "manifest.schema",
            "imports must define exactly domain, engine, agents, and runtime; the "
            "removed node-package grammar (graph/nodes) cannot be re-declared",
        )
    for layer, required_internal in REQUIRED_INTERNAL_IMPORT_POLICY.items():
        internal = set(imports[layer]) & INTERNAL_LAYERS
        if internal != required_internal:
            raise ContractViolation(
                "imports.policy",
                f"imports.{layer} must keep its internal-layer import directions: {sorted(required_internal)}",
            )
        unknown = (set(imports[layer]) - INTERNAL_LAYERS) - TOP_LEVEL_NAMESPACE_WHITELIST
        if unknown:
            raise ContractViolation(
                "imports.namespace",
                f"imports.{layer} names an unknown external namespace: {sorted(unknown)}",
            )

    if data.get("node_packages") is not None:
        raise ContractViolation(
            "node.grammar_removed",
            "the node-package grammar was removed from the structure contract; "
            "reintroduction requires a project-structure spec change",
        )

    guide = _expect_mapping(data.get("guide"), "guide")
    guide_path = _relative_path(guide.get("path"), "guide.path")
    begin_marker = _expect_string(guide.get("begin_marker"), "guide.begin_marker")
    end_marker = _expect_string(guide.get("end_marker"), "guide.end_marker")
    if begin_marker == end_marker:
        raise ContractViolation("manifest.schema", "guide.begin_marker and guide.end_marker must differ")
    expected_guide_path = CANONICAL_HARNESS_ROOT / "AGENTS.md"
    if guide_path != expected_guide_path:
        raise ContractViolation("manifest.schema", f"guide.path must be {expected_guide_path.as_posix()}")

    return StructureManifest(
        guide_path=guide_path,
        begin_marker=begin_marker,
        end_marker=end_marker,
        upstream_gitlink=upstream_gitlink,
        source_root=source_root,
        fixture_root=fixture_root,
        fixture_package=fixture_package,
        fixture_production_contracts=fixture_production_contracts,
        fixture_external_namespaces=fixture_external_namespaces,
        fixture_recipe_class=fixture_recipe_class,
        fixture_recipe_factories=fixture_recipe_factories,
        test_root=test_root,
        ownership_layers=ownership_layers,
        forbidden_source_roots=forbidden_source_roots,
        forbidden_shared_modules=forbidden_shared_modules,
        ignored_path=ignored_path,
        ignored_entries=ignored_entries,
        required_paths=tuple(required_paths),
        imports=imports,
    )
