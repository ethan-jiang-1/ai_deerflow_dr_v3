#!/usr/bin/env python3
"""Reject downstream Harness dependencies on the upstream OpenSpec framework.

Scans every file under ``deep_research_harness/`` — tracked or not, outside the
ignored parts — for forbidden tokens referencing the governance face. A violation
fails loudly, naming the file and the token.

Verification receipts are exempt evidence, not dependencies: a file named exactly
``verification-receipt.json`` that parses as a JSON object carrying a top-level
non-empty ``checks`` list of command-record objects (the runner-receipt convention)
records governance commands that were run about the harness; it cannot make the
application depend on the governance face. Recognition is structural, not nominal —
a file that carries the name but not the shape stays scanned. The exemption is
locked by red-capable negative controls in
``openspec/tests/governance/test_harness_dependency_direction.py``.

@impl DEP-001
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORBIDDEN = ("openspec/", "../openspec", "openspec.governance")
IGNORED_PARTS = frozenset({".venv", ".pytest_cache", "__pycache__", ".reports"})
RECEIPT_NAME = "verification-receipt.json"


def _is_verification_receipt(path: Path) -> bool:
    """True iff the file structurally matches the runner-receipt convention.

    Fail-safe: any miss — wrong name, unparseable JSON, non-object root, missing,
    empty, or malformed ``checks`` — means the file is NOT recognized and stays
    subject to the token scan.
    """
    if path.name != RECEIPT_NAME:
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    checks = data.get("checks") if isinstance(data, dict) else None
    if not isinstance(checks, list) or not checks:
        return False
    return all(
        isinstance(item, dict) and "command" in item for item in checks
    )


def violations(root: Path) -> list[str]:
    harness = root / "deep_research_harness"
    found: list[str] = []
    for path in sorted(harness.rglob("*")):
        if not path.is_file() or IGNORED_PARTS.intersection(path.parts):
            continue
        if _is_verification_receipt(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for token in FORBIDDEN:
            if token in text:
                found.append(f"{path.relative_to(root)}: forbidden downstream dependency {token!r}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path("."))
    args = parser.parse_args()
    found = violations(args.project_root.resolve())
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    print("Harness dependency direction passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
