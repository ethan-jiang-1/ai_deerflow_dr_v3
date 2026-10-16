"""The closeout tool is importable **by name** — the point of the 2026-10-16 rename.

Every other governance test loads its checker through
``importlib.util.spec_from_file_location`` (a path-based load), which works even for
a hyphenated file name. That is exactly why those tests could not have caught the
problem this file guards: until the rename, ``import selected_change_closeout`` was
impossible, so the tool's logic could only ever be exercised as a subprocess.

These tests therefore load it with a real ``import``. The first keeps the module
importable by name; the second pins the decision that the *recorded evidence schema*
did not follow the file name.

@impl DEW-001"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GOVERNANCE = REPO_ROOT / "openspec" / "governance"


def _import_tool():
    """Import the module by name, restoring sys.path afterwards."""
    sys.path.insert(0, str(GOVERNANCE))
    try:
        import selected_change_closeout as tool  # noqa: PLC0415 — the import IS the assertion
    finally:
        sys.path.remove(str(GOVERNANCE))
    return tool


class CloseoutToolImportTest(unittest.TestCase):
    def test_the_module_imports_by_name_and_exposes_its_entry_point(self) -> None:
        tool = _import_tool()
        self.assertEqual(
            Path(tool.__file__).name,
            "selected_change_closeout.py",
            "the tool must stay importable by name (a hyphenated file cannot be)",
        )
        self.assertTrue(
            callable(getattr(tool, "main", None)),
            "the tool must expose its CLI entry point as `main`",
        )

    def test_the_recorded_evidence_schema_did_not_follow_the_file_name(self) -> None:
        tool = _import_tool()
        self.assertEqual(
            tool.SCHEMA_VERSION,
            "selected-change-closeout/v1",
            "SCHEMA_VERSION identifies recorded evidence, not the path; renaming it "
            "would invalidate every existing record",
        )


if __name__ == "__main__":
    unittest.main()
