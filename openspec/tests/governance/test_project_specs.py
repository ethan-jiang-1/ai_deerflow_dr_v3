"""Red-first fixtures for the requirement-ID tracking removal (remove-requirement-id-tracking).

New shapes under test — all must validate CLEAN once the tracking rules are removed:
  1. a delta spec without any `> req:` header line,
  2. a main spec without a `> req:` header line,
  3. a requirement title that embeds a requirement ID.

Run from the repository root:
    python3 -m unittest discover -s openspec/tests/governance -q
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from check_project_specs import (  # noqa: E402
    _validate_main_specs,
    validate_selected_change_delta_specs,
)


def _write_change_delta(root: Path, body: str) -> None:
    delta = root / "openspec" / "changes" / "demo-change" / "specs" / "demo" / "spec.md"
    delta.parent.mkdir(parents=True)
    delta.write_text(body, encoding="utf-8")


class HeaderLessDeltaValidatesClean(unittest.TestCase):
    def test_delta_without_req_header_has_no_violations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_change_delta(
                root,
                "# Spec Delta\n\n## ADDED Requirements\n\n### Requirement: Does the thing\n\n"
                "The system SHALL do the thing.\n\n"
                "#### Scenario: It does the thing\n\n- **WHEN** invoked\n- **THEN** it does\n",
            )
            violations, code = validate_selected_change_delta_specs(root, "demo-change")
            self.assertEqual([], [v for v in violations if v["check"] == "missingDeltaReqHeader"])
            self.assertEqual(0, code)


class HeaderLessMainSpecValidatesClean(unittest.TestCase):
    def test_main_spec_without_req_header_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "openspec" / "specs" / "demo" / "spec.md"
            spec.parent.mkdir(parents=True)
            spec.write_text(
                "# demo Specification\n\n## Purpose\n\nOwns the demo behavior.\n\n"
                "## Requirements\n\n### Requirement: Does the thing\n\n"
                "The system SHALL do the thing.\n\n"
                "#### Scenario: It does the thing\n\n- **WHEN** invoked\n- **THEN** it does\n",
                encoding="utf-8",
            )
            self.assertEqual(0, _validate_main_specs(root))


class TitleMayCarryIdText(unittest.TestCase):
    def test_main_spec_title_with_id_text_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "openspec" / "specs" / "demo" / "spec.md"
            spec.parent.mkdir(parents=True)
            spec.write_text(
                "# demo Specification\n\n## Purpose\n\nOwns the demo behavior.\n\n"
                "## Requirements\n\n### Requirement: PRS-001 style title\n\n"
                "The system SHALL do the thing.\n\n"
                "#### Scenario: It does the thing\n\n- **WHEN** invoked\n- **THEN** it does\n",
                encoding="utf-8",
            )
            self.assertEqual(0, _validate_main_specs(root))


if __name__ == "__main__":
    unittest.main()
