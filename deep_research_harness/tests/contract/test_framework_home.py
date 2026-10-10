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

    def test_secondary_direct_clients_pin_before_client_construction(self) -> None:
        """Direct build_client callers outside run_foreground must pin first.

        The framework resolves its home as $DEER_FLOW_HOME else cwd/.deer-flow;
        an unpinned direct client writes runtime state into the application
        subtree (2026-10-10 audit: deep_research_harness/.deer-flow accumulated
        live threads). Locked by source order, not line numbers.
        """
        targets = (
            HARNESS_ROOT / "tests" / "integration" / "test_wiring_smoke.py",
            HARNESS_ROOT / "tests" / "integration" / "test_complete_graph_replay.py",
            HARNESS_ROOT / "tools" / "record_stream.py",
        )

        def call_name(node: ast.AST) -> str:
            if isinstance(node, ast.Call):
                func = node.func
                return func.attr if isinstance(func, ast.Attribute) else (
                    func.id if isinstance(func, ast.Name) else ""
                )
            return ""

        for path in targets:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            offenders: list[str] = []
            found_client_call = False
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                pin_lines = [s.lineno for s in ast.walk(node) if call_name(s) == "pin_framework_home"]
                client_lines = [s.lineno for s in ast.walk(node) if call_name(s) == "build_client"]
                if client_lines:
                    found_client_call = True
                    if not pin_lines or min(pin_lines) > min(client_lines):
                        offenders.append(node.name)
            self.assertTrue(
                found_client_call,
                f"{path.name}: expected a build_client call site; update this "
                "contract when the call surface moves",
            )
            self.assertEqual(
                offenders, [],
                f"{path.name}: build_client without a preceding pin_framework_home in "
                f"{offenders} — the framework home would resolve to cwd and write "
                "runtime state inside the application subtree",
            )


from unittest.mock import patch  # noqa: E402

if __name__ == "__main__":
    unittest.main()
