"""A graduated bug card must land with the work it records.

Four flips were done by hand in one session and every one compiled with this rule — which
is the situation worth guarding: a habit that has never failed is a habit nobody notices
when it stops. The rule reads history rather than structure, so these cases build tiny
repositories (and, just as importantly, cases where there is no history to read at all).

@impl PRS-001"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parents[2] / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from project_architecture_check.contract import ContractViolation  # noqa: E402
from project_architecture_check.graduation import (  # noqa: E402
    validate_graduation_lands_with_implementation,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = "_backlog/_archived/_fixed_bugs"


class GraduationCase(unittest.TestCase):
    def repository(self, *, git: bool = True) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / ARCHIVE).mkdir(parents=True)
        if git:
            for command in (
                ["git", "init", "-q"],
                ["git", "config", "user.email", "t@example.invalid"],
                ["git", "config", "user.name", "test"],
                ["git", "config", "commit.gpgsign", "false"],
            ):
                subprocess.run(command, cwd=root, check=True, capture_output=True)
        return root

    def commit(self, root: Path, message: str) -> None:
        subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", message], cwd=root, check=True, capture_output=True)

    def card(self, root: Path, name: str = "BUG-900-demo.md") -> Path:
        path = root / ARCHIVE / name
        path.write_text("# BUG-900: demo\n", encoding="utf-8")
        return path


class GraduationFlipTest(GraduationCase):
    def test_a_card_committed_alone_is_reported(self) -> None:
        root = self.repository()
        self.card(root)
        self.commit(root, "ledger only")
        with self.assertRaises(ContractViolation) as caught:
            validate_graduation_lands_with_implementation(root)
        self.assertEqual(caught.exception.code, "ledger.graduation_without_implementation")
        self.assertIn("BUG-900-demo.md", caught.exception.detail)

    def test_a_card_landing_with_an_implementation_is_accepted(self) -> None:
        root = self.repository()
        self.card(root)
        implementation = root / "openspec" / "governance" / "thing.py"
        implementation.parent.mkdir(parents=True)
        implementation.write_text("value = 1\n", encoding="utf-8")
        self.commit(root, "card + implementation")
        validate_graduation_lands_with_implementation(root)


class SilentWhenHistoryCannotAnswerTest(GraduationCase):
    def test_an_untracked_card_is_skipped(self) -> None:
        root = self.repository()
        self.card(root)  # never committed
        validate_graduation_lands_with_implementation(root)

    def test_a_tree_without_git_is_skipped(self) -> None:
        root = self.repository(git=False)
        self.card(root)
        validate_graduation_lands_with_implementation(root)


class RealHistoryTest(unittest.TestCase):
    def test_every_graduated_card_landed_with_its_implementation(self) -> None:
        validate_graduation_lands_with_implementation(REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
