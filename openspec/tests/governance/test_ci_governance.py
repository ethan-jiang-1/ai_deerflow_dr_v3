"""Focused stdlib tests for the ci-governance drift checker.

Canonical maintained command, from the repository root:

    python3 -m unittest discover -s openspec/tests/governance

Fixtures are built under temp directories and never mutate the repository.
The checker is loaded in-process via importlib for the check() cases and
invoked as a subprocess for the exit-code contract, exactly like real
callers do. Every negative case proves the guard can fail; only the valid
fixture passes clean.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "openspec" / "governance" / "check_ci_governance.py"

VALID_WORKFLOW = """name: Governance Gate

on:
  push:
    paths:
      - "openspec/**"
      - "deep_research_harness/**"
      - ".github/workflows/governance.yml"
      - ".githooks/**"
  pull_request:
    paths:
      - "openspec/**"
      - "deep_research_harness/**"
      - ".github/workflows/governance.yml"
      - ".githooks/**"

permissions:
  contents: read

jobs:
  governance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm install -g @fission-ai/openspec@1.13.1
      - run: python3 -m unittest discover -s openspec/tests/governance -q
      - run: python3 openspec/governance/check_project_gate.py --phase closeout
      - run: python3 openspec/governance/check_doc_hygiene.py
      - run: UV_OFFLINE=1 make verify
"""

VALID_HOOK = """#!/bin/sh
# Cheap checks only; suites belong to CI.
set -e
cd "$(git rev-parse --show-toplevel)"
git diff --cached --check
python3 openspec/governance/check_doc_hygiene.py
"""


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_ci_governance_under_test", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_tree(
    root: Path,
    workflow: str | None = VALID_WORKFLOW,
    hook: str | None = VALID_HOOK,
    executable: bool = True,
) -> None:
    if workflow is not None:
        path = root / ".github" / "workflows" / "governance.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(workflow, encoding="utf-8")
    if hook is not None:
        path = root / ".githooks" / "pre-commit"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(hook, encoding="utf-8")
        path.chmod(0o755 if executable else 0o644)


class CheckCiGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = _load_checker()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_valid_fixture_passes_clean(self) -> None:
        _build_tree(self.root)
        self.assertEqual(self.checker.check(self.root), [])

    def test_missing_workflow_fails(self) -> None:
        _build_tree(self.root, workflow=None)
        errors = self.checker.check(self.root)
        self.assertTrue(any("CI workflow is missing" in error for error in errors))

    def test_workflow_missing_one_canonical_command_fails(self) -> None:
        gutted = VALID_WORKFLOW.replace(
            "python3 openspec/governance/check_project_gate.py --phase closeout\n", ""
        )
        _build_tree(self.root, workflow=gutted)
        errors = self.checker.check(self.root)
        self.assertTrue(
            any("check_project_gate.py --phase closeout" in error for error in errors)
        )

    def test_multi_job_workflow_fails(self) -> None:
        two_jobs = VALID_WORKFLOW + "  second:\n    runs-on: ubuntu-latest\n"
        _build_tree(self.root, workflow=two_jobs)
        errors = self.checker.check(self.root)
        self.assertTrue(any("exactly one job" in error for error in errors))

    def test_missing_hook_fails(self) -> None:
        _build_tree(self.root, hook=None)
        errors = self.checker.check(self.root)
        self.assertTrue(any("pre-commit hook is missing" in error for error in errors))

    def test_non_executable_hook_fails(self) -> None:
        _build_tree(self.root, executable=False)
        errors = self.checker.check(self.root)
        self.assertTrue(any("not executable" in error for error in errors))

    def test_hook_with_forbidden_command_fails(self) -> None:
        forbidden = VALID_HOOK + "pytest -q\n"
        _build_tree(self.root, hook=forbidden)
        errors = self.checker.check(self.root)
        self.assertTrue(any("forbidden" in error for error in errors))

    def test_hook_with_undeclared_extra_command_fails(self) -> None:
        extra = VALID_HOOK + "echo hi\n"
        _build_tree(self.root, hook=extra)
        errors = self.checker.check(self.root)
        self.assertTrue(any("undeclared command line" in error for error in errors))

    def test_subprocess_exit_contract_on_missing_tree(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER), str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("CI workflow is missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
