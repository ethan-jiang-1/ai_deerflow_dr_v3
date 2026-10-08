"""Deterministic tests for the standing-tasks-sections rule (@impl CHA-001).

Run from the repository root:

    python3 -m unittest discover -s openspec/tests/governance

Fixtures build isolated temp roots and never mutate the repository. The
kernel grammar is exercised pure; the checker wiring is exercised through
_validate_change_tasks on a temp change root. Exit-code semantics: the
checker surfaces each kernel issue as a ContractViolation (exit 1 with a
[code] detail line) — the tests assert the issue codes and details directly.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

import change_guidance_kernel as kernel  # noqa: E402
from check_change_guidance import ContractViolation, _validate_change_tasks  # noqa: E402


GOOD_REGISTER = "## Deviation Register\n\n- none: planning-time deviation-free\n"
BAD_REGISTER = "## Deviation Register\n\n## Next\n"
BARE_NONE_REGISTER = "## Deviation Register\n\n- none:\n"
GOOD_RECORD = (
    "## Delivery Record\n\n"
    "- **外部行为**: filled at closeout\n"
    "- **影响面**: filled at closeout\n"
    "- **实际跑了什么**: filled at closeout\n"
    "- **未执行的检查**: filled at closeout\n"
)
MISSING_LABEL_RECORD = (
    "## Delivery Record\n\n"
    "- **外部行为**: filled\n"
    "- **影响面**: filled\n"
    "- **实际跑了什么**: filled\n"
)


def _tasks(*sections: str) -> str:
    return "# Tasks\n\n## 1. Work\n\n- [ ] 1.1 do it\n\n" + "\n".join(sections)


class DeviationRegisterGrammarTests(unittest.TestCase):
    def test_explicit_none_passes(self):
        self.assertEqual(kernel.deviation_register_issues(_tasks(GOOD_REGISTER)), ())

    def test_entry_bullets_pass(self):
        register = "## Deviation Register\n\n- renamed helper; ruled by spec §2; landed in tasks 2.1\n"
        self.assertEqual(kernel.deviation_register_issues(_tasks(register)), ())

    def test_missing_section_fails(self):
        issues = kernel.deviation_register_issues("# Tasks\n\n## 1. Work\n\n- [ ] 1.1 do it\n")
        self.assertEqual(issues[0].code, "tasks.deviation_register_missing")

    def test_empty_section_fails(self):
        issues = kernel.deviation_register_issues(_tasks("## Deviation Register\n\nsome prose, no bullets\n"))
        self.assertEqual(issues[0].code, "tasks.deviation_register_empty")

    def test_bare_none_fails(self):
        issues = kernel.deviation_register_issues(_tasks(BARE_NONE_REGISTER))
        self.assertEqual(issues[0].code, "tasks.deviation_register_none_rationale")

    def test_duplicate_section_fails(self):
        issues = kernel.deviation_register_issues(_tasks(GOOD_REGISTER, GOOD_REGISTER))
        self.assertEqual(issues[0].code, "tasks.deviation_register_duplicate")


class DeliveryRecordGrammarTests(unittest.TestCase):
    def test_all_labels_pass(self):
        self.assertEqual(kernel.delivery_record_issues(_tasks(GOOD_RECORD)), ())

    def test_missing_section_fails(self):
        issues = kernel.delivery_record_issues(_tasks(GOOD_REGISTER))
        self.assertEqual(issues[0].code, "tasks.delivery_record_missing")

    def test_missing_label_fails(self):
        issues = kernel.delivery_record_issues(_tasks(MISSING_LABEL_RECORD))
        self.assertEqual(issues[0].code, "tasks.delivery_record_field_missing")
        self.assertIn("未执行的检查", issues[0].detail)

    def test_duplicate_section_fails(self):
        issues = kernel.delivery_record_issues(_tasks(GOOD_RECORD, GOOD_RECORD))
        self.assertEqual(issues[0].code, "tasks.delivery_record_duplicate")


class CheckerWiringTests(unittest.TestCase):
    """_validate_change_tasks raises on grammar violations and skips a missing tasks.md."""

    def _change_root(self, tmp: str, tasks_text: str | None) -> Path:
        root = Path(tmp)
        change_root = root / "openspec" / "changes" / "demo-change"
        change_root.mkdir(parents=True)
        if tasks_text is not None:
            (change_root / "tasks.md").write_text(tasks_text, encoding="utf-8")
        return root

    def test_compliant_tasks_pass_silently(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, _tasks(GOOD_REGISTER, GOOD_RECORD))
            _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")

    def test_missing_tasks_md_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, None)
            _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")

    def test_violation_names_change_and_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, _tasks(MISSING_LABEL_RECORD, GOOD_REGISTER))
            with self.assertRaises(ContractViolation) as ctx:
                _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")
            self.assertEqual(ctx.exception.code, "tasks.delivery_record_field_missing")
            self.assertIn("demo-change/tasks.md", ctx.exception.detail)

    def test_register_violation_names_change_and_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._change_root(tmp, _tasks(GOOD_RECORD))
            with self.assertRaises(ContractViolation) as ctx:
                _validate_change_tasks(root, root / "openspec" / "changes" / "demo-change")
            self.assertEqual(ctx.exception.code, "tasks.deviation_register_missing")


if __name__ == "__main__":
    unittest.main()
