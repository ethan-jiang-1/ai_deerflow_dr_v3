"""The agent invocation surface stays a thin menu over a real playbook.

@impl APB-001"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[2]
COMMANDS = HARNESS / "COMMANDS.md"
PLAYBOOK = HARNESS / "playbook"

SIX_VERBS = ("create", "status", "watch", "cancel", "refine", "inspect")


class MenuCoversTheClosedSurfaceTest(unittest.TestCase):
    def test_every_cli_verb_appears_in_the_menu(self) -> None:
        text = COMMANDS.read_text(encoding="utf-8")
        for verb in SIX_VERBS:
            self.assertIn(f"cli.py {verb}", text, f"menu omits cli verb: {verb}")

    def test_every_make_target_appears_in_the_menu(self) -> None:
        makefile = (HARNESS / "Makefile").read_text(encoding="utf-8")
        targets = re.findall(r"^([a-z-]+):", makefile, re.MULTILINE)
        self.assertTrue(targets)
        text = COMMANDS.read_text(encoding="utf-8")
        for target in targets:
            self.assertIn(target, text, f"menu omits make target: {target}")


class MenuRoutesWithoutEmbeddingProcedureTest(unittest.TestCase):
    def test_every_routing_target_exists_under_playbook(self) -> None:
        text = COMMANDS.read_text(encoding="utf-8")
        targets = re.findall(r"\((playbook/[\w.-]+\.md)\)", text)
        self.assertTrue(targets, "menu carries no routing lines")
        for target in targets:
            self.assertTrue(
                (HARNESS / target).is_file(), f"dangling routing target: {target}"
            )

    def test_menu_has_no_ordered_procedural_sequence(self) -> None:
        text = COMMANDS.read_text(encoding="utf-8")
        numbered_steps = re.findall(r"^\d+\.\s+\*\*", text, re.MULTILINE)
        self.assertEqual(
            numbered_steps, [], "menu must not embed ordered procedure steps"
        )


class PlaybookContentDisciplineTest(unittest.TestCase):
    def test_seed_playbook_carries_completion_criteria_and_receipts(self) -> None:
        text = (PLAYBOOK / "run-research.md").read_text(encoding="utf-8")
        self.assertIn("完成判据", text)
        self.assertIn("回执纪律", text)
        self.assertIn("坑", text)

    def test_playbook_commands_reference_the_menu_not_duplicates(self) -> None:
        text = (PLAYBOOK / "run-research.md").read_text(encoding="utf-8")
        self.assertIn("../COMMANDS.md", text)
        for verb in SIX_VERBS:
            self.assertIn(verb, text, f"playbook never exercises verb: {verb}")


if __name__ == "__main__":
    unittest.main()
