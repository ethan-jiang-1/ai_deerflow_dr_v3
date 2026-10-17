"""The change-guidance guard must not read structure out of a fenced example.

BUG-006: three of its parses were line-based, so a proposal that merely *quoted* a
heading or a table inside a code fence was rejected as malformed — and the rejection
was a false one (the field was there, the section had been truncated before reaching
it). Each case here pins one of the three, plus the shapes that must keep working.

@impl CHA-001"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from change_guidance_check import helpers, reviews  # noqa: E402

FENCED_HEADING = "```\n## Example Heading Inside A Fence\n```\n"


class SectionBoundaryTest(unittest.TestCase):
    def section(self, proposal: str) -> str:
        match = re.search(r"^## Change Focus\s*$", proposal, flags=re.MULTILINE)
        return helpers._section_after_heading(proposal, match, maximum_level=2)

    def test_a_fenced_heading_does_not_end_the_section(self) -> None:
        proposal = (
            "## Change Focus\n\n- **Primary module:** x\n\n"
            + FENCED_HEADING
            + "\n- **Evidence seam:** y\n"
        )
        section = self.section(proposal)
        self.assertIn("Evidence seam", section)
        self.assertIn("Primary module", section)

    def test_a_real_heading_still_ends_the_section(self) -> None:
        proposal = "## Change Focus\n\n- **Primary module:** x\n\n## Next Section\n\n- **Evidence seam:** y\n"
        section = self.section(proposal)
        self.assertIn("Primary module", section)
        self.assertNotIn("Evidence seam", section)


class ReviewTableTest(unittest.TestCase):
    def table_lines(self, section: str) -> list[str]:
        return [
            line
            for line in helpers._without_fences(section).splitlines()
            if reviews._table_cells(line) is not None
        ]

    def test_a_fenced_table_before_the_real_one_is_not_the_header(self) -> None:
        real = "| h1 | h2 | h3 | h4 | h5 | h6 |\n|---|---|---|---|---|---|\n| a | b | c | d | e | f |\n"
        fenced = "```\n| x1 | x2 | x3 | x4 | x5 | x6 |\n```\n"
        lines = self.table_lines(fenced + real)
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("| h1"))


class ProgramModeTest(unittest.TestCase):
    def program_count(self, proposal: str) -> int:
        return len(re.findall(r"^## Program Focus\s*$", helpers._without_fences(proposal),
                              flags=re.MULTILINE))

    def test_a_fenced_program_heading_does_not_switch_the_form(self) -> None:
        proposal = "# P\n\n## Change Focus\n\n```\n## Program Focus\n```\n"
        self.assertEqual(self.program_count(proposal), 0)

    def test_a_real_program_heading_is_still_counted(self) -> None:
        self.assertEqual(self.program_count("# P\n\n## Program Focus\n"), 1)


if __name__ == "__main__":
    unittest.main()
