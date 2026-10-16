"""Direct tests for the one fence rule the governance tools share.

Until this module existed, two tools answered "what is a fenced code block?"
differently and neither answer had a direct test: the specs checker's local copy had
zero references under ``openspec/tests/``, and the closeout tool's copy arrived with
BUG-003. The older answer was the permissive one, and it blanked headings that
CommonMark calls real (BUG-004) — those two cases are pinned here as regressions.

@impl PRS-001"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

import markdown_fences  # noqa: E402 — the governance dir is put on sys.path above


class FenceFlagsTest(unittest.TestCase):
    def flags(self, text: str) -> list[bool]:
        return markdown_fences.fence_flags(text.split("\n"))

    def test_a_closed_fence_flags_delimiters_and_content(self) -> None:
        self.assertEqual(self.flags("a\n```\nb\n```\nc"), [False, True, True, True, False])

    def test_an_unclosed_fence_runs_to_the_end(self) -> None:
        self.assertEqual(self.flags("a\n```\nb\nc"), [False, True, True, True])

    def test_tilde_fences_are_fences(self) -> None:
        self.assertEqual(self.flags("~~~\nb\n~~~"), [True, True, True])

    def test_a_longer_closing_fence_closes(self) -> None:
        self.assertEqual(self.flags("````\nb\n`````\nc"), [True, True, True, False])

    def test_a_shorter_closing_fence_does_not_close(self) -> None:
        self.assertEqual(self.flags("````\nb\n```\nc"), [True, True, True, True])

    def test_a_closing_fence_with_trailing_text_does_not_close(self) -> None:
        self.assertEqual(self.flags("```\nb\n``` not a close\nc"), [True, True, True, True])

    def test_an_opening_fence_may_carry_an_info_string(self) -> None:
        self.assertEqual(self.flags("```python\nb\n```\nc"), [True, True, True, False])

    def test_up_to_three_spaces_of_indentation_is_still_a_fence(self) -> None:
        self.assertEqual(self.flags("   ```\nb\n   ```\nc"), [True, True, True, False])

    def test_four_spaces_of_indentation_is_an_indented_code_block(self) -> None:
        # CommonMark 4.4: the fence-looking line is the content of an indented code
        # block, so it neither opens nor closes a fence.
        self.assertEqual(self.flags("    ```\n## Requirement\n    ```"), [False, False, False])

    def test_a_backtick_info_string_may_not_contain_a_backtick(self) -> None:
        # CommonMark 4.5: the first line is not a fence opener at all, so the heading
        # below it is ordinary text. The trailing bare fence IS a valid opener (and is
        # unclosed, hence flagged) — that is what makes this case worth pinning.
        self.assertEqual(self.flags("``` foo`bar\n## Requirement\n```"), [False, False, True])

    def test_a_tilde_fence_info_string_may_contain_a_backtick(self) -> None:
        self.assertEqual(self.flags("~~~ foo`bar\nb\n~~~\nc"), [True, True, True, False])

    def test_a_mixed_character_closing_fence_does_not_close(self) -> None:
        self.assertEqual(self.flags("```\nb\n~~~\nc"), [True, True, True, True])


class IterOutsideFencesTest(unittest.TestCase):
    def test_only_unfenced_lines_are_yielded(self) -> None:
        lines = "keep\n```\ndrop\n```\nkeep too".split("\n")
        self.assertEqual(list(markdown_fences.iter_outside_fences(lines)), ["keep", "keep too"])

    def test_an_unclosed_fence_swallows_the_rest(self) -> None:
        lines = "keep\n```\ndrop\ndrop too".split("\n")
        self.assertEqual(list(markdown_fences.iter_outside_fences(lines)), ["keep"])


class StripFencedCodeBlocksTest(unittest.TestCase):
    def test_line_numbering_is_preserved(self) -> None:
        stripped = markdown_fences.strip_fenced_code_blocks("one\n```\ntwo\n```\nthree")
        self.assertEqual(stripped, "one\n\n\n\nthree")
        self.assertEqual(len(stripped.split("\n")), 5)

    def test_carriage_returns_are_normalised(self) -> None:
        self.assertEqual(
            markdown_fences.strip_fenced_code_blocks("a\r\n```\r\nb\r\n```"),
            "a\n\n\n",
        )

    def test_a_heading_after_a_four_space_indented_fence_is_not_hidden(self) -> None:
        # BUG-004 regression: this is an indented code block followed by a real
        # heading; the old permissive rule blanked the heading.
        stripped = markdown_fences.strip_fenced_code_blocks(
            "    ```\n## Requirement: real\n    ```\n"
        )
        self.assertIn("## Requirement: real", stripped)

    def test_a_heading_after_a_backtick_info_string_containing_backticks_is_not_hidden(self) -> None:
        # BUG-004 regression, second case.
        stripped = markdown_fences.strip_fenced_code_blocks(
            "``` foo`bar\n## Requirement: real\n```\n"
        )
        self.assertIn("## Requirement: real", stripped)

    def test_a_real_fence_still_hides_its_content(self) -> None:
        stripped = markdown_fences.strip_fenced_code_blocks(
            "```\n## Requirement: an example\n```\n## Requirement: real\n"
        )
        self.assertNotIn("an example", stripped)
        self.assertIn("## Requirement: real", stripped)


if __name__ == "__main__":
    unittest.main()
