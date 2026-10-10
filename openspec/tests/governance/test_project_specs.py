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


class DeltaSyncCompletenessTest(unittest.TestCase):
    """Archived ADDED requirements must be pinned into the main specs.

    The 2026-10-10 sweep found two archived ADDED requirements that never
    landed (the archive spec-update step was skipped); this matrix locks the
    rule that makes that drift fail loudly (enforce-delta-sync).
    """

    @staticmethod
    def _write_main(root: Path, capability: str, titles: list) -> None:
        spec = root / "openspec" / "specs" / capability / "spec.md"
        spec.parent.mkdir(parents=True, exist_ok=True)
        body = "# spec\n\n## Purpose\n\nP.\n\n## Requirements\n"
        for title in titles:
            body += f"\n### Requirement: {title}\n\nThe system SHALL.\n"
        spec.write_text(body, encoding="utf-8")

    @staticmethod
    def _write_delta(root: Path, change: str, capability: str, body: str) -> None:
        delta = root / "openspec" / "changes" / "archive" / change / "specs" / capability / "spec.md"
        delta.parent.mkdir(parents=True, exist_ok=True)
        delta.write_text(body, encoding="utf-8")

    @staticmethod
    def _validate_capturing(root: Path) -> tuple[int, str]:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            code = _validate_main_specs(root)
        return code, buffer.getvalue()

    def test_archived_added_missing_from_main_fails_loudly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_main(root, "demo", ["Present thing"])
            self._write_delta(
                root, "2026-01-01-one", "demo",
                "# D\n\n## ADDED Requirements\n\n### Requirement: Vanished thing\n\n"
                "The system SHALL.\n\n#### Scenario: It does\n\n- **WHEN** invoked\n- **THEN** it does\n",
            )
            code, err = self._validate_capturing(root)
            self.assertEqual(1, code)
            self.assertIn("2026-01-01-one", err)
            self.assertIn("Vanished thing", err)

    def test_archived_added_present_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_main(root, "demo", ["Present thing", "Also present"])
            self._write_delta(
                root, "2026-01-01-one", "demo",
                "# D\n\n## ADDED Requirements\n\n### Requirement: Also present\n\nThe system SHALL.\n",
            )
            self.assertEqual(0, self._validate_capturing(root)[0])

    def test_later_removed_exempts_the_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_main(root, "demo", ["Survivor"])
            self._write_delta(
                root, "2026-01-01-one", "demo",
                "# D\n\n## ADDED Requirements\n\n### Requirement: Retired thing\n\nThe system SHALL.\n",
            )
            self._write_delta(
                root, "2026-02-02-two", "demo",
                "# D\n\n## REMOVED Requirements\n\n### Requirement: Retired thing\n",
            )
            self.assertEqual(0, self._validate_capturing(root)[0])

    def test_allowlisted_out_of_band_rename_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_main(
                root,
                "entry-surface",
                ["The verb set mirrors the state machine and observation layers"],
            )
            self._write_delta(
                root, "2026-01-01-one", "entry-surface",
                "# D\n\n## ADDED Requirements\n\n"
                "### Requirement: Six verbs mirror the state machine and observation layers\n\n"
                "The system SHALL.\n",
            )
            self.assertEqual(0, self._validate_capturing(root)[0])

    def test_capability_without_main_spec_fails_loudly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_main(root, "demo", ["Present thing"])
            self._write_delta(
                root, "2026-01-01-one", "ghost-capability",
                "# D\n\n## ADDED Requirements\n\n### Requirement: Orphaned thing\n\nThe system SHALL.\n",
            )
            code, err = self._validate_capturing(root)
            self.assertEqual(1, code)
            self.assertIn("ghost-capability", err)


if __name__ == "__main__":
    unittest.main()
