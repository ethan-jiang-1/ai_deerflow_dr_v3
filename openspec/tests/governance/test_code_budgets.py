#!/usr/bin/env python3
"""Tests for the governance code-budget gate (capability: code-budgets).

The gate's job is to notice a governance script growing past its declared ceiling.
These tests exercise the declared table against the real tree, each failure mode
against a planted temporary tree, and the checker's own negative-control self-test.

@impl DOB-001"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GOVERNANCE = Path(__file__).resolve().parents[2] / "governance"
REPO_ROOT = GOVERNANCE.parents[1]
CHECKER = GOVERNANCE / "check_code_budgets.py"

if str(GOVERNANCE) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE))

import check_code_budgets as budgets  # noqa: E402  (governance dir is importable above)


class DeclaredTableTests(unittest.TestCase):
    """The real tree satisfies every declared ceiling, and the table is not empty."""

    def test_real_tree_is_within_budget(self) -> None:
        self.assertEqual(budgets.violations(REPO_ROOT), [])

    def test_table_declares_the_largest_scripts(self) -> None:
        """A table that manages nothing would pass vacuously."""
        self.assertGreaterEqual(len(budgets.CODE_BUDGETS), 10, "the declaring table shrank")
        largest = {name for name, _ in sorted(
            ((p.relative_to(GOVERNANCE).as_posix(), len(p.read_text(encoding="utf-8").splitlines()))
             for p in GOVERNANCE.rglob("*.py") if "__pycache__" not in str(p)),
            key=lambda item: item[1], reverse=True)[:5]}
        self.assertTrue(largest.issubset(budgets.CODE_BUDGETS),
                        f"unmanaged top-five scripts: {sorted(largest - set(budgets.CODE_BUDGETS))}")

    def test_every_declared_ceiling_is_met_by_its_file(self) -> None:
        for relative, budget in budgets.CODE_BUDGETS.items():
            path = GOVERNANCE / relative
            with self.subTest(file=relative):
                self.assertTrue(path.is_file(), f"managed file missing: {relative}")
                lines = len(path.read_text(encoding="utf-8").splitlines())
                self.assertLessEqual(lines, budget.max_lines)
                self.assertLessEqual(len(budgets._long_functions(path)), budget.max_long_functions)


class FailureModeTests(unittest.TestCase):
    """Each failure mode fires on a planted tree and names what it found."""

    def _tree(self, files: dict[str, str]) -> tempfile.TemporaryDirectory:
        tmp = tempfile.TemporaryDirectory()
        base = Path(tmp.name) / "governance"
        base.mkdir(parents=True)
        for name, content in files.items():
            (base / name).write_text(content, encoding="utf-8")
        return tmp

    def test_over_line_budget_is_reported(self) -> None:
        with self._tree({"big.py": "x = 1\n" * 30}) as tmp:
            found = budgets.violations(Path(tmp), {"big.py": budgets.FileBudget(10, 0)},
                                       base_dir=Path("governance"))
        self.assertTrue(any("over line budget: big.py" in f and "30 > 10" in f for f in found), found)

    def test_over_long_function_budget_is_reported_with_the_function(self) -> None:
        body = "\n".join(f"    y{i} = {i}" for i in range(60))
        with self._tree({"long.py": f"def hefty():\n{body}\n"}) as tmp:
            found = budgets.violations(Path(tmp), {"long.py": budgets.FileBudget(500, 0)},
                                       base_dir=Path("governance"))
        self.assertTrue(any("over long-function budget: long.py" in f and "hefty" in f for f in found), found)

    def test_missing_managed_file_is_reported(self) -> None:
        with self._tree({"present.py": "x = 1\n"}) as tmp:
            found = budgets.violations(Path(tmp), {"absent.py": budgets.FileBudget(10, 0)},
                                       base_dir=Path("governance"))
        self.assertTrue(any("missing managed code path: governance/absent.py" in f for f in found), found)

    def test_within_budget_passes_clean(self) -> None:
        with self._tree({"fine.py": "def short():\n    return 1\n"}) as tmp:
            found = budgets.violations(Path(tmp), {"fine.py": budgets.FileBudget(10, 1)},
                                       base_dir=Path("governance"))
        self.assertEqual(found, [])

    def test_undeclared_files_are_not_enforced(self) -> None:
        with self._tree({"ignored.py": "x = 1\n" * 500}) as tmp:
            found = budgets.violations(Path(tmp), {}, base_dir=Path("governance"))
        self.assertEqual(found, [], "a file the table does not declare must not be enforced")


class CheckerInterfaceTests(unittest.TestCase):
    """The CLI contract: exit codes and the self-test's planted negatives."""

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(CHECKER), *args],
                              capture_output=True, text=True, check=False, cwd=str(REPO_ROOT))

    def test_plain_mode_exits_zero_on_the_real_tree(self) -> None:
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "governance code budgets passed.\n")

    def test_self_test_exits_zero(self) -> None:
        result = self._run("--self-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "code-budget self-test passed.\n")

    def test_self_test_reports_a_removed_planted_defect(self) -> None:
        """Mutation control: with the planted over-limit file gone, the self-test must fail.

        Patches the module's own self-test input in a subprocess so the repository
        file is never modified.
        """
        program = (
            "import sys; sys.path.insert(0, 'openspec/governance')\n"
            "import check_code_budgets as m\n"
            "original = m.violations\n"
            "m.violations = lambda *a, **k: []\n"     # nothing is ever reported
            "errs = m._self_test()\n"
            "m.violations = original\n"
            "print('RED' if errs else 'GREEN')\n"
        )
        result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True,
                                check=False, cwd=str(REPO_ROOT))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "RED",
                         "the self-test passed while every violation was suppressed")

    def test_checker_is_importable_without_side_effects(self) -> None:
        spec = importlib.util.spec_from_file_location("code_budget_probe", CHECKER)
        module = importlib.util.module_from_spec(spec)
        sys.modules["code_budget_probe"] = module
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))
        self.assertGreater(len(module.CODE_BUDGETS), 0)


if __name__ == "__main__":
    unittest.main()
