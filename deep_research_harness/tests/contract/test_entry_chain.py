"""Chain-lock contract: the entry chain's call composition, locked offline.

Locks the declared create/refine journey composition (spec owner: the
entry-surface chain-lock requirement, landed by the active structural
change): the launcher delegates to the interaction surface; the verbs route
through bundle actions and the foreground assembly; the assembly composes
checkpointer, bound client, stream callable, and the run pump; terminal
delivery passes the admission owner. Assertions are AST-level call
signatures over the chain's module sources: they fail naming the broken
link when a stage is replaced, bypassed, or its module is renamed without
cutover, and they pass under behavior-preserving refactors inside a stage
(no line numbers, no formatting, no product import).

@impl CHAIN-001"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[2]
SRC = HARNESS_ROOT / "src" / "deerflow_deep_research"

LAUNCHER = "cli.py"
INTERACTION_CLI = "runtime/interaction/cli.py"
ASSEMBLY = "runtime/assembly.py"
PUMP = "runtime/pump.py"


def _parse(rel_path: str, *, root: Path = SRC) -> ast.Module:
    path = root / rel_path
    if not path.is_file():
        raise AssertionError(
            f"entry-chain module missing: {rel_path} "
            "(renamed or moved without cutting over the chain lock)"
        )
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _function(tree: ast.Module, name: str, owner: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"entry-chain stage function missing: {name} in {owner}")


def _call_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Attribute):
                names.add(func.attr)
            elif isinstance(func, ast.Name):
                names.add(func.id)
    return names


def _from_imports(tree: ast.Module) -> list[tuple[str, list[str]]]:
    return [
        (node.module or "", [alias.name for alias in node.names])
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    ]


class LauncherDelegationTest(unittest.TestCase):
    """Link 1: the stable launcher only delegates to the interaction surface."""

    def test_launcher_imports_only_the_interaction_surface(self) -> None:
        tree = _parse(LAUNCHER, root=HARNESS_ROOT)
        product_imports = [
            (module, names)
            for module, names in _from_imports(tree)
            if module.startswith("deerflow_deep_research")
        ]
        self.assertEqual(
            product_imports,
            [("deerflow_deep_research.runtime.interaction.cli", ["main"])],
            "entry-chain link 1 broken: cli.py must delegate solely to the "
            "interaction surface (deerflow_deep_research.runtime.interaction.cli.main)",
        )


class VerbRoutingTest(unittest.TestCase):
    """Link 2: create/refine route through bundle actions + foreground assembly."""

    def test_create_routes_through_actions_and_assembly(self) -> None:
        tree = _parse(INTERACTION_CLI)
        calls = _call_names(_function(tree, "cmd_create", INTERACTION_CLI))
        for required in ("start", "resolve_bundle", "run_foreground"):
            self.assertIn(
                required,
                calls,
                f"entry-chain link 2 broken: cmd_create no longer calls {required!r} "
                f"(bundle actions / foreground assembly bypassed); observed calls: {sorted(calls)}",
            )

    def test_refine_routes_through_actions_and_assembly(self) -> None:
        tree = _parse(INTERACTION_CLI)
        calls = _call_names(_function(tree, "cmd_refine", INTERACTION_CLI))
        for required in ("refine", "resolve_bundle", "run_foreground"):
            self.assertIn(
                required,
                calls,
                f"entry-chain link 2 broken: cmd_refine no longer calls {required!r} "
                f"(bundle actions / foreground assembly bypassed); observed calls: {sorted(calls)}",
            )

    def test_verbs_never_drive_the_stream_themselves(self) -> None:
        tree = _parse(INTERACTION_CLI)
        stream_leaks = sorted(
            name
            for name in ("make_stream_fn", "build_client", "bundle_checkpointer", "run_research")
            if name in _call_names(tree)
        )
        self.assertEqual(
            stream_leaks,
            [],
            f"entry-chain link 2 broken: the interaction surface reaches into binding/pump "
            f"directly ({stream_leaks}) — verbs must own presentation only",
        )


class AssemblyCompositionTest(unittest.TestCase):
    """Link 3: the foreground assembly composes checkpointer, binding, stream, pump."""

    def test_run_foreground_composes_the_full_run(self) -> None:
        tree = _parse(ASSEMBLY)
        calls = _call_names(_function(tree, "run_foreground", ASSEMBLY))
        for required in ("bundle_checkpointer", "build_client", "make_stream_fn", "run_research"):
            self.assertIn(
                required,
                calls,
                f"entry-chain link 3 broken: run_foreground no longer calls {required!r} "
                f"(checkpointer / binding / stream seam / pump bypassed); "
                f"observed calls: {sorted(calls)}",
            )


class TerminalDeliveryTest(unittest.TestCase):
    """Link 4: terminal honesty comes from domain rules; delivery passes admission."""

    def test_delivery_submits_through_admission(self) -> None:
        tree = _parse(PUMP)
        delivery = _call_names(_function(tree, "_record_delivery", PUMP))
        self.assertIn(
            "_submit_final_report",
            delivery,
            "entry-chain link 4 broken: _record_delivery no longer routes the final "
            "report through _submit_final_report; observed calls: "
            f"{sorted(delivery)}",
        )
        submission = _call_names(_function(tree, "_submit_final_report", PUMP))
        self.assertIn(
            "submit_artifact",
            submission,
            "entry-chain link 4 broken: _submit_final_report no longer calls "
            "submit_artifact (admission hold point bypassed); observed calls: "
            f"{sorted(submission)}",
        )


if __name__ == "__main__":
    unittest.main()
