"""The release-face guard fails loudly on every violation class and stays green on a
compliant tree.

The release face (RLF-001) is exactly ``deep_research_harness/`` plus the pinned
``deerflow/`` gitlink. ``check_release_face.py`` validates the current tree against
that contract. Each violation class below is exercised against a purpose-built
fixture tree, and every assertion is an exit code read directly from a subprocess.
"""

from __future__ import annotations

import subprocess
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "openspec/governance/check_release_face.py"

VALID_SHA = "a" * 40
DRIFT_SHA = "b" * 40

HARNESS = "deep_research_harness"
PYPROJECT = """\
[project]
name = "fixture-harness"

[tool.uv.sources]
deerflow-harness = { path = "../deerflow/backend/packages/harness", editable = true }
"""

COMMANDS = """\
# COMMANDS

- `python3 cli.py create "..."` — details: playbook/run-research.md
"""


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _make_gitlink_repo(dir_path: Path) -> str:
    """A standalone repo standing in for the gitlink checkout; returns HEAD sha."""
    dir_path.mkdir(parents=True)
    (dir_path / "backend/packages/harness").mkdir(parents=True)
    (dir_path / "backend/packages/harness/pyproject.toml").write_text("", encoding="utf-8")
    _git(dir_path, "init", "-q")
    _git(dir_path, "config", "user.email", "fixture@example.invalid")
    _git(dir_path, "config", "user.name", "fixture")
    _git(dir_path, "add", "-A")
    _git(dir_path, "commit", "-q", "--allow-empty", "-m", "fixture")
    return _git(dir_path, "rev-parse", "HEAD")


def _build_compliant_tree(root: Path, head_sha: str) -> None:
    (root / "openspec/governance").mkdir(parents=True)
    (root / "openspec/governance/project-structure.toml").write_text(
        f'[upstream_gitlink]\npath = "deerflow"\ncommit = "{head_sha}"\n',
        encoding="utf-8",
    )
    harness = root / HARNESS
    (harness / "src/pkg").mkdir(parents=True)
    (harness / "playbook").mkdir()
    (harness / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    (harness / "src/pkg/mod.py").write_text("VALUE = 1\n", encoding="utf-8")
    (harness / "cli.py").write_text("print('hi')\n", encoding="utf-8")
    (harness / "COMMANDS.md").write_text(COMMANDS, encoding="utf-8")
    (harness / "playbook/run-research.md").write_text("# run-research\n", encoding="utf-8")


def _fixture_tree() -> Path:
    import tempfile

    root = Path(tempfile.mkdtemp(prefix="release-face-fixture-"))
    _make_gitlink_repo(root / "deerflow")
    head_sha = _git(root / "deerflow", "rev-parse", "HEAD")
    _build_compliant_tree(root, head_sha)
    return root


def _run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(CHECKER), str(root)], capture_output=True, text=True, check=False
    )


class CompliantTreeTest(unittest.TestCase):
    def test_compliant_tree_exits_zero(self) -> None:
        root = _fixture_tree()
        result = _run_checker(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ViolationClassTest(unittest.TestCase):
    """Each fixture turns exactly one contract fact red; the guard must name it."""

    def test_missing_gitlink_directory_is_red(self) -> None:
        import shutil

        root = _fixture_tree()
        shutil.rmtree(root / "deerflow")
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("deerflow", result.stdout)

    def test_gitlink_pin_drift_is_red(self) -> None:
        root = _fixture_tree()
        manifest = root / "openspec/governance/project-structure.toml"
        manifest.write_text(
            f'[upstream_gitlink]\npath = "deerflow"\ncommit = "{DRIFT_SHA}"\n',
            encoding="utf-8",
        )
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pin drift", result.stdout)

    def test_dependency_source_outside_the_face_is_red(self) -> None:
        root = _fixture_tree()
        pyproject = root / HARNESS / "pyproject.toml"
        pyproject.write_text(
            PYPROJECT.replace("../deerflow/", "../elsewhere/"), encoding="utf-8"
        )
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pyproject.toml", result.stdout)

    def test_dev_face_reference_in_harness_source_is_red(self) -> None:
        root = _fixture_tree()
        module = root / HARNESS / "src/pkg/mod.py"
        module.write_text("import openspec\n", encoding="utf-8")
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mod.py", result.stdout)

    def test_dangling_menu_routing_target_is_red(self) -> None:
        root = _fixture_tree()
        commands = root / HARNESS / "COMMANDS.md"
        commands.write_text(
            COMMANDS.replace("run-research.md", "missing-file.md"), encoding="utf-8"
        )
        result = _run_checker(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing-file.md", result.stdout)


class RealTreeTest(unittest.TestCase):
    def test_real_repository_tree_exits_zero(self) -> None:
        result = subprocess.run(
            ["python3", str(CHECKER)], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_manifest_pin_is_a_full_sha(self) -> None:
        manifest = tomllib.loads(
            (REPO_ROOT / "openspec/governance/project-structure.toml").read_text(
                encoding="utf-8"
            )
        )
        self.assertRegex(manifest["upstream_gitlink"]["commit"], r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
