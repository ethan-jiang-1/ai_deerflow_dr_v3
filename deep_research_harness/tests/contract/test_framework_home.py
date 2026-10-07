"""Framework-home pin contract: runtime state never lands in the app subtree.

@impl HOME-001"""

from __future__ import annotations

import ast
import os
import unittest
from pathlib import Path

from deerflow_deep_research.runtime import assembly

HARNESS_ROOT = Path(__file__).resolve().parents[2]
SRC = HARNESS_ROOT / "src" / "deerflow_deep_research"


class FrameworkHomePinTest(unittest.TestCase):
    def test_pin_sets_env_to_the_repo_root_home(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            home = assembly.pin_framework_home()
            self.assertEqual(home, assembly.REPO_ROOT / ".deer-flow")
            self.assertEqual(os.environ.get("DEER_FLOW_HOME"), str(home))

    def test_pinned_home_is_outside_the_application_subtree(self) -> None:
        home = assembly.FRAMEWORK_HOME
        self.assertFalse(
            home == HARNESS_ROOT or HARNESS_ROOT in home.parents,
            f"framework home {home} must not live inside the application subtree",
        )

    def test_run_foreground_pins_before_client_construction(self) -> None:
        tree = ast.parse((SRC / "runtime" / "assembly.py").read_text(encoding="utf-8"))
        run_fg = next(
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "run_foreground"
        )
        calls = []
        for sub in ast.walk(run_fg):
            if isinstance(sub, ast.Call):
                func = sub.func
                name = func.attr if isinstance(func, ast.Attribute) else (
                    func.id if isinstance(func, ast.Name) else ""
                )
                calls.append(name)
        self.assertIn("pin_framework_home", calls, "run_foreground must pin the framework home")
        self.assertLess(
            calls.index("pin_framework_home"), calls.index("build_client"),
            "the home pin must happen before client construction (framework import)",
        )


from unittest.mock import patch  # noqa: E402

if __name__ == "__main__":
    unittest.main()
