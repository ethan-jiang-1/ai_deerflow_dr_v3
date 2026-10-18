"""Composition and CLI of the architecture checker.

@impl PRS-001"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .contract import ContractViolation
from .cycles import validate_no_import_cycles
from .markdown_grammar import validate_single_fence_grammar
from .gitlink import _validate_upstream_gitlink
from .imports import validate_imports
from .inspect_tree import (
    _validate_guide,
    _validate_ignored_paths,
    _validate_required_paths,
    _validate_single_source_root,
    _validate_spec_authority,
)
from .manifest import load_manifest


def validate_project(root: Path, manifest: StructureManifest) -> None:
    _validate_spec_authority(root, manifest)
    _validate_guide(root, manifest)
    _validate_required_paths(root, manifest)
    _validate_ignored_paths(root, manifest)
    _validate_single_source_root(root, manifest)
    validate_imports(root, manifest)
    validate_no_import_cycles(root)
    # A source-structure rule, not an import contract: it runs with the full project
    # validation and deliberately not under --imports-only.
    validate_single_fence_grammar(root)
    _validate_upstream_gitlink(root, manifest)


def check_project(root: Path, *, imports_only: bool = False) -> None:
    """Validate one repository through the same seam used by the CLI.

    """
    manifest = load_manifest(root)
    if imports_only:
        validate_imports(root, manifest)
        validate_no_import_cycles(root)
    else:
        validate_project(root, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument(
        "--imports-only",
        action="store_true",
        help="validate only manifest and Python import contracts",
    )
    parser.add_argument(
        "--render-guide",
        action="store_true",
        help="print the deterministic AGENTS.md structure-locator block",
    )
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    try:
        if args.render_guide:
            manifest = load_manifest(root)
            print(render_guide_block(manifest), end="")
            return 0
        check_project(root, imports_only=args.imports_only)
    except ContractViolation as violation:
        print(f"ERROR [{violation.code}] {violation.detail}", file=sys.stderr)
        return 1
    print(f"Architecture governance passed for {root}")
    return 0
