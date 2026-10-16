"""Import-matrix validation over the harness source, fixture and upstream trees.

@impl PRS-001"""

from __future__ import annotations

import ast
import os
import sys
import tomllib
from pathlib import Path, PurePosixPath

from .contract import (
    INTERNAL_LAYERS,
    PACKAGE_NAME,
    ContractViolation,
    StructureManifest,
)

def _python_files(base: Path) -> list[Path]:
    if not base.is_dir():
        return []
    excluded_names = {".git", ".venv", "venv", "node_modules", ".next", "__pycache__"}
    files: list[Path] = []
    for current, directories, names in os.walk(base):
        directories[:] = sorted(directory for directory in directories if directory not in excluded_names)
        files.extend(Path(current) / name for name in sorted(names) if name.endswith(".py"))
    return files


def _module_parts(source_root: Path, path: Path) -> tuple[str, ...]:
    parts = list(path.relative_to(source_root).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return tuple(parts)


def _resolved_imports(
    tree: ast.AST,
    module_parts: tuple[str, ...],
    is_package: bool,
    *,
    package_name: str = PACKAGE_NAME,
) -> list[str]:
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level:
            package_parts = module_parts if is_package else module_parts[:-1]
            ascend = node.level - 1
            if ascend > len(package_parts):
                imports.append("")
                continue
            base_parts = package_parts[: len(package_parts) - ascend]
            module_suffix = tuple(node.module.split(".")) if node.module else ()
            resolved_parts = (package_name, *base_parts, *module_suffix)
        else:
            resolved_parts = tuple(node.module.split(".")) if node.module else ()
        if not resolved_parts:
            imports.append("")
            continue
        for alias in node.names:
            suffix = () if alias.name == "*" else tuple(alias.name.split("."))
            imports.append(".".join((*resolved_parts, *suffix)))
    return imports


def _source_owner(relative: PurePosixPath) -> tuple[str, str | None]:
    parts = relative.parts
    if not parts:
        return "package", None
    if parts[0] in {"domain", "engine", "agents", "runtime"}:
        return parts[0], None
    if len(parts) == 1 and parts[0] == "tool.py":
        return "tool", None
    return "package", None


def _target_owner(module_name: str) -> tuple[str | None, str | None]:
    parts = module_name.split(".")
    if not parts or parts[0] != PACKAGE_NAME:
        return None, None
    if len(parts) == 1:
        return "package", None
    if parts[1] in {"domain", "engine", "agents", "runtime"}:
        return parts[1], None
    return "package", None


def _external_allowed(
    layer: str,
    module_root: str,
    manifest: StructureManifest,
    relative: PurePosixPath,
) -> bool:
    if module_root in sys.stdlib_module_names or module_root == "__future__":
        return True
    if module_root == "openai":
        return layer == "runtime" and relative == PurePosixPath("runtime/node_agent_bridge.py")
    if module_root == "httpx":
        return layer == "runtime" and relative in {
            PurePosixPath("runtime/node_agent_bridge.py"),
            PurePosixPath("runtime/gateway_observer.py"),
        }
    if module_root == "httpx_sse":
        return layer == "runtime" and relative == PurePosixPath("runtime/gateway_observer.py")
    allowed = set(manifest.imports.get(layer, ())) - INTERNAL_LAYERS - {"stdlib"}
    if layer == "tool":
        allowed = {"langchain", "pydantic"}
    if layer == "package":
        allowed = set()
    return any(module_root == prefix or module_root.startswith(f"{prefix}_") for prefix in allowed)


def _validate_module_imports(
    root: Path,
    source_root: Path,
    path: Path,
    manifest: StructureManifest,
) -> None:
    relative = PurePosixPath(path.relative_to(source_root).as_posix())
    if path.stem in manifest.forbidden_shared_modules:
        raise ContractViolation("module.generic", f"generic shared module is forbidden: {path.relative_to(root)}")
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise ContractViolation("import.syntax", f"cannot parse {path.relative_to(root)}: {exc}") from exc

    layer, _ = _source_owner(relative)
    module_parts = _module_parts(source_root, path)
    for imported in _resolved_imports(tree, module_parts, path.name == "__init__.py"):
        if not imported:
            raise ContractViolation("import.boundary", f"invalid relative import in {path.relative_to(root)}")
        module_root = imported.split(".", 1)[0]
        if manifest.fixture_package is not None and module_root == manifest.fixture_package:
            raise ContractViolation(
                "import.fixture_reverse",
                f"production source imports fixture package: {path.relative_to(root)}",
            )
        if module_root == "app":
            raise ContractViolation("import.app", f"production downstream code imports app.*: {path.relative_to(root)}")

        target_layer, _ = _target_owner(imported)
        if target_layer is None:
            if not _external_allowed(layer, module_root, manifest, relative):
                raise ContractViolation(
                    "import.external",
                    f"{path.relative_to(root)} imports undeclared external namespace {module_root}",
                )
            continue

        if target_layer == layer or (layer == "package" and target_layer == "package"):
            continue
        if layer == "tool":
            allowed_internal = {"runtime"}
        elif layer == "package":
            allowed_internal = set()
        else:
            allowed_internal = set(manifest.imports[layer]) & INTERNAL_LAYERS
        if target_layer not in allowed_internal:
            raise ContractViolation(
                "import.boundary",
                f"{layer} module {path.relative_to(root)} imports forbidden {target_layer} module {imported}",
            )


def _validate_upstream_does_not_import_downstream(root: Path, manifest: StructureManifest) -> None:
    for upstream_root in manifest.forbidden_source_roots:
        for path in _python_files(root / upstream_root):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, UnicodeError, SyntaxError) as exc:
                raise ContractViolation("import.syntax", f"cannot parse {path.relative_to(root)}: {exc}") from exc
            for node in ast.walk(tree):
                if isinstance(node, ast.Import) and any(
                    alias.name.split(".", 1)[0] == PACKAGE_NAME for alias in node.names
                ):
                    raise ContractViolation(
                        "source.upstream_import",
                        f"upstream module imports downstream package: {path.relative_to(root)}",
                    )
                if isinstance(node, ast.ImportFrom) and (node.module or "").split(".", 1)[0] == PACKAGE_NAME:
                    raise ContractViolation(
                        "source.upstream_import",
                        f"upstream module imports downstream package: {path.relative_to(root)}",
                    )


def _static_all_exports(path: Path) -> list[str] | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise ContractViolation("import.syntax", f"cannot parse {path}: {exc}") from exc
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            continue
        value = node.value
        if not isinstance(value, (ast.List, ast.Tuple)):
            return None
        exports: list[str] = []
        for element in value.elts:
            if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                return None
            exports.append(element.value)
        return exports
    return None


def _fixture_production_import_is_allowed(imported: str, manifest: StructureManifest) -> bool:
    allowed = (*manifest.fixture_production_contracts, manifest.fixture_recipe_class)
    return any(
        candidate is not None and (imported == candidate or imported.startswith(f"{candidate}."))
        for candidate in allowed
    )


def _validate_fixture_recipe_references(
    root: Path,
    path: Path,
    tree: ast.AST,
    manifest: StructureManifest,
) -> None:
    if manifest.fixture_recipe_class is None:
        return
    recipe_module, recipe_class_name = manifest.fixture_recipe_class.rsplit(".", 1)
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.level or node.module != recipe_module:
            continue
        aliases.update(alias.asname or alias.name for alias in node.names if alias.name == recipe_class_name)
    if not aliases:
        return

    parents = {
        id(child): parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or node.id not in aliases:
            continue
        parent = parents.get(id(node))
        is_allowed_direct_call = (
            isinstance(node.ctx, ast.Load)
            and isinstance(parent, ast.Attribute)
            and parent.value is node
            and parent.attr in manifest.fixture_recipe_factories
            and isinstance(parents.get(id(parent)), ast.Call)
            and parents[id(parent)].func is parent
        )
        if is_allowed_direct_call:
            continue
        factories = ", ".join(manifest.fixture_recipe_factories)
        raise ContractViolation(
            "fixture.recipe_factory",
            f"fixture source may only call {manifest.fixture_recipe_class}.{factories}: {path.relative_to(root)}",
        )


def _validate_fixture_imports(root: Path, manifest: StructureManifest) -> None:
    if manifest.fixture_root is None or manifest.fixture_package is None:
        return
    fixture_root = root / manifest.fixture_root
    if not fixture_root.is_dir():
        raise ContractViolation("path.missing", f"fixture source root is missing: {manifest.fixture_root}")
    for path in _python_files(fixture_root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            raise ContractViolation("import.syntax", f"cannot parse {path.relative_to(root)}: {exc}") from exc
        module_parts = _module_parts(fixture_root, path)
        for imported in _resolved_imports(
            tree,
            module_parts,
            path.name == "__init__.py",
            package_name=manifest.fixture_package,
        ):
            if not imported:
                raise ContractViolation("import.boundary", f"invalid relative import in {path.relative_to(root)}")
            module_root = imported.split(".", 1)[0]
            if module_root == manifest.fixture_package:
                continue
            if module_root == PACKAGE_NAME:
                if _fixture_production_import_is_allowed(imported, manifest):
                    continue
                raise ContractViolation(
                    "import.fixture_production",
                    f"fixture source imports an unregistered production contract {imported}: {path.relative_to(root)}",
                )
            if (
                module_root in sys.stdlib_module_names
                or module_root == "__future__"
                or module_root in manifest.fixture_external_namespaces
            ):
                continue
            raise ContractViolation(
                "import.fixture_external",
                f"fixture source imports undeclared namespace {module_root}: {path.relative_to(root)}",
            )
        _validate_fixture_recipe_references(root, path, tree, manifest)


def _validate_production_wheel(root: Path, manifest: StructureManifest) -> None:
    if manifest.fixture_root is None:
        return
    pyproject = root / manifest.source_root.parent.parent / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        packages = data["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    except (KeyError, OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ContractViolation("package.wheel_config", "cannot inspect production wheel package configuration") from exc
    expected = ["src/deerflow_deep_research"]
    if packages != expected:
        raise ContractViolation("package.fixture_included", "production wheel must package only src/deerflow_deep_research")


def validate_imports(root: Path, manifest: StructureManifest) -> None:
    source_root = root / manifest.source_root
    if not source_root.is_dir():
        raise ContractViolation("path.missing", f"source root is missing: {manifest.source_root}")
    for path in _python_files(source_root):
        _validate_module_imports(root, source_root, path, manifest)
    _validate_fixture_imports(root, manifest)
    _validate_production_wheel(root, manifest)
    _validate_upstream_does_not_import_downstream(root, manifest)
