"""Command-surface guard: COMMANDS.md, Makefile targets, and cli.py subcommands stay
mutually consistent (docs-as-contract — the documented commands ARE the deliverable).

@impl ENS-001"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[2]
COMMANDS = (HARNESS / "COMMANDS.md").read_text(encoding="utf-8")
MAKEFILE = (HARNESS / "Makefile").read_text(encoding="utf-8")
CLI = (HARNESS / "src/deerflow_deep_research/runtime/interaction/cli.py").read_text(encoding="utf-8")
REGISTER = (HARNESS / "docs" / "quality-register.md").read_text(encoding="utf-8")


def makefile_targets() -> set[str]:
    return set(re.findall(r"^([a-z][a-z-]*):", MAKEFILE, re.MULTILINE))


def cli_declared_commands() -> set[str]:
    """The subcommand verbs cli.py itself declares (the COMMANDS tuple + the
    add_parser call sites)."""

    tuple_match = re.search(r"^COMMANDS = \(([^)]*)\)", CLI, re.MULTILINE)
    declared = set(re.findall(r'"([a-z]+)"', tuple_match.group(1))) if tuple_match else set()
    declared |= set(re.findall(r'sub\.add_parser\("([a-z]+)"', CLI))
    return declared


class CommandSurfaceTest(unittest.TestCase):
    def test_documented_make_targets_exist(self) -> None:
        documented = set(re.findall(r"make ([a-z][a-z-]*)", COMMANDS))
        self.assertTrue(documented, "COMMANDS.md must document at least one make target")
        missing = documented - makefile_targets()
        self.assertEqual(missing, set(), f"COMMANDS.md documents nonexistent targets: {missing}")

    def test_cli_subcommands_are_documented(self) -> None:
        self.assertEqual(
            cli_declared_commands(), {"create", "status", "watch", "cancel", "refine", "inspect"}
        )
        for verb in cli_declared_commands():
            self.assertIn(verb, COMMANDS, f"subcommand {verb!r} undocumented in COMMANDS.md")

    def test_command_surface_guard_is_registered(self) -> None:
        self.assertIn("command-surface-guard", REGISTER)


if __name__ == "__main__":
    unittest.main()
