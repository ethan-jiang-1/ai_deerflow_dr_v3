"""Composition and CLI of the Change Guidance checker.

@impl CHA-001"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .guidance import (
    _validate_change_guidance_tree,
    _validate_claude_guide,
    _validate_focus_gate,
    _validate_information_map,
    _validate_product_context,
)
from .helpers import ContractViolation
from .proposals import _validate_active_changes, _validate_authoring_pointer

def validate(root: Path) -> list[str]:
    if not root.is_dir():
        raise ContractViolation("root.missing", f"project root is not a directory: {root}")
    _validate_change_guidance_tree(root)
    _validate_product_context(root)
    _validate_focus_gate(root)
    _validate_claude_guide(root)
    _validate_authoring_pointer(root)
    warnings = _validate_information_map(root)
    _validate_active_changes(root)
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".", help="repository root to validate")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    try:
        warnings = validate(root)
    except ContractViolation as exc:
        print(f"[{exc.code}] {exc.detail}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(warning, file=sys.stderr)
    print("Change Guidance governance passed.")
    return 0
