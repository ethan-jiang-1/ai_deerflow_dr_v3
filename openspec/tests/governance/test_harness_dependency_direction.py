"""The dependency-direction guard distinguishes evidence from coupling.

The guard rejects downstream harness dependencies on the development-governance face
while structurally recognizing runner verification receipts as exempt evidence: a
receipt is exempt only when it is named exactly ``verification-receipt.json`` and
parses as a JSON object carrying a top-level non-empty ``checks`` list of
command-record objects. ``check_harness_dependency_direction.py`` owns the rule
(``@impl DEP-001``).

Every fixture below runs against a purpose-built non-git temp tree, so the fixture
files are untracked by construction and the controls also evidence the untracked-file
scan. The checker is invoked as a subprocess with the fixture root passed as its
``project_root`` argument, and every assertion reads the exit code directly from the
subprocess result — never through a pipe.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "openspec/governance/check_harness_dependency_direction.py"
HARNESS = "deep_research_harness"

VALID_RECEIPT = {
    "revision": "0" * 40,
    "completed_at": "2026-10-05T00:00:00+00:00",
    "checks": [
        {
            "command": ["python3", "openspec/governance/check_doc_hygiene.py"],
            "exit_code": 0,
            "stdout": "doc-layer hygiene passed.\n",
            "stderr": "",
        },
        {
            "command": ["python3", "openspec/governance/check_project_architecture.py"],
            "exit_code": 0,
            "stdout": "Architecture governance passed.\n",
            "stderr": "",
        },
    ],
    "observations": ["fixture receipt for the dependency guard"],
    "unverified": [],
}


def _fixture_tree() -> Path:
    """A minimal harness tree whose only content is a valid receipt recording
    governance command argv (the historical false-positive shape)."""
    import tempfile

    root = Path(tempfile.mkdtemp(prefix="dependency-guard-fixture-"))
    skills = root / HARNESS / "docs/skills/deep-research"
    skills.mkdir(parents=True)
    (skills / "verification-receipt.json").write_text(
        json.dumps(VALID_RECEIPT, indent=2) + "\n", encoding="utf-8"
    )
    return root


def _run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(CHECKER), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


class ValidReceiptTest(unittest.TestCase):
    """A receipt recording governance commands is evidence, not a dependency."""

    def test_valid_receipt_with_governance_argv_exits_zero(self) -> None:
        root = _fixture_tree()
        result = _run_checker(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ViolationClassTest(unittest.TestCase):
    """Each fixture turns exactly one contract fact red; the guard must name it."""

    def test_governance_reference_in_harness_source_is_red(self) -> None:
        root = _fixture_tree()
        module = root / HARNESS / "src/pkg/mod.py"
        module.parent.mkdir(parents=True)
        module.write_text("PATH = 'openspec/governance'\n", encoding="utf-8")
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mod.py", result.stderr)
        self.assertIn("openspec/", result.stderr)

    def test_fake_receipt_without_receipt_shape_is_red(self) -> None:
        root = _fixture_tree()
        receipt = root / HARNESS / "docs/skills/deep-research/verification-receipt.json"
        receipt.write_text(
            "run python3 openspec/governance/check_doc_hygiene.py\n", encoding="utf-8"
        )
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verification-receipt.json", result.stderr)

    def test_empty_checks_with_hidden_token_is_red(self) -> None:
        root = _fixture_tree()
        receipt = root / HARNESS / "docs/skills/deep-research/verification-receipt.json"
        receipt.write_text(
            json.dumps({"checks": [], "notes": "openspec/ hidden here"}) + "\n",
            encoding="utf-8",
        )
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verification-receipt.json", result.stderr)

    def test_non_dict_command_records_are_red(self) -> None:
        root = _fixture_tree()
        receipt = root / HARNESS / "docs/skills/deep-research/verification-receipt.json"
        receipt.write_text(
            json.dumps({"checks": ["openspec/governance/check_doc_hygiene.py"]}) + "\n",
            encoding="utf-8",
        )
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("verification-receipt.json", result.stderr)


class RealTreeTest(unittest.TestCase):
    def test_real_repository_tree_exits_zero(self) -> None:
        result = _run_checker(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
