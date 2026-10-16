"""Implementation of the project-structure architecture checker.

The executable entry point stays at `../check_project_architecture.py`: CI, the
aggregate closeout gate and the copied-script test fixture all address that path.
This package holds the rules; the entry point holds the CLI and re-exports the
names the tests use.

@impl PRS-001
"""

from __future__ import annotations

import sys
from pathlib import Path

# The entry point may live in a copied tree (the governance fixtures copy the
# checker scripts into a temporary repository). Putting *this* file's directory
# first makes a copied entry point resolve its own sibling package instead of
# reaching back into the original checkout.
_GOVERNANCE_DIR = str(Path(__file__).resolve().parent)
if _GOVERNANCE_DIR not in sys.path:
    sys.path.insert(0, _GOVERNANCE_DIR)

from .contract import (  # noqa: E402
    CANONICAL_HARNESS_ROOT,
    CANONICAL_OWNERSHIP_LAYERS,
    ContractViolation,
    FIXTURE_PACKAGE_NAME,
    GIT_COMMIT_RE,
    INTERNAL_LAYERS,
    INVENTORY_RELATIVE,
    MAIN_SPEC_RELATIVE,
    MANIFEST_RELATIVE,
    PACKAGE_NAME,
    REQUIRED_INTERNAL_IMPORT_POLICY,
    SPEC_REFERENCE,
    TOP_LEVEL_NAMESPACE_WHITELIST,
    UPSTREAM_GITLINK_PATH,
    RequiredPath,
    StructureManifest,
    UpstreamGitlink,
)
from .facade import check_project, main, validate_project  # noqa: E402
from .gitlink import _run_git_metadata, _validate_upstream_gitlink  # noqa: E402
from .imports import (  # noqa: E402
    _external_allowed,
    _fixture_production_import_is_allowed,
    _module_parts,
    _python_files,
    _resolved_imports,
    _source_owner,
    _static_all_exports,
    _target_owner,
    _validate_fixture_imports,
    _validate_fixture_recipe_references,
    _validate_module_imports,
    _validate_production_wheel,
    _validate_upstream_does_not_import_downstream,
    validate_imports,
)
from .inspect_tree import (  # noqa: E402
    _directory_display,
    _validate_guide,
    _validate_ignored_paths,
    _validate_required_paths,
    _validate_single_source_root,
    _validate_spec_authority,
    render_guide_block,
)
from .manifest import load_manifest  # noqa: E402

__all__ = [
    "CANONICAL_HARNESS_ROOT",
    "CANONICAL_OWNERSHIP_LAYERS",
    "ContractViolation",
    "FIXTURE_PACKAGE_NAME",
    "GIT_COMMIT_RE",
    "INTERNAL_LAYERS",
    "INVENTORY_RELATIVE",
    "MAIN_SPEC_RELATIVE",
    "MANIFEST_RELATIVE",
    "PACKAGE_NAME",
    "REQUIRED_INTERNAL_IMPORT_POLICY",
    "SPEC_REFERENCE",
    "TOP_LEVEL_NAMESPACE_WHITELIST",
    "UPSTREAM_GITLINK_PATH",
    "RequiredPath",
    "StructureManifest",
    "UpstreamGitlink",
    "check_project",
    "load_manifest",
    "render_guide_block",
    "validate_imports",
    "validate_project",
]
