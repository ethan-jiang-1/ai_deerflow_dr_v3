"""Skill-declaration guard: the binding's skill surface is declared, not implicit.

Locks the deerflow-wiring delta (landed by the active structural change): the
bound client's ``available_skills`` surface must be sourced from the owning
ladder's declaration through the assembly resolver — never hard-coded at the
binding site, never silently coerced. The default posture is exactly ``None``
(absent declaration = unwired binding, never an empty list, which would be a
conscious declaration). Activation semantics — what the framework loads and
with what quality — are outside this guard's scope.

@impl SKL-001
@impl SKL-002"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[2]
SRC = HARNESS_ROOT / "src" / "deerflow_deep_research"

from deerflow_deep_research.runtime.assembly import resolve_skills


def _parse(rel_path: str) -> ast.Module:
    path = SRC / rel_path
    if not path.is_file():
        raise AssertionError(f"declaration-seam module missing: {rel_path}")
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _call_node(tree: ast.Module, func_name: str) -> ast.Call:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute) and func.attr == func_name) or (
                isinstance(func, ast.Name) and func.id == func_name
            ):
                return node
    raise AssertionError(f"no call to {func_name!r} found")


def _keyword_value(call: ast.Call, name: str) -> ast.expr | None:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


class DefaultPostureTest(unittest.TestCase):
    """The declared-none posture: absent declaration resolves to exactly None."""

    def test_absent_declaration_resolves_to_none(self) -> None:
        self.assertIsNone(resolve_skills({"models": []}))

    def test_explicit_null_resolves_to_none(self) -> None:
        self.assertIsNone(resolve_skills({"skills": None}))

    def test_empty_list_is_a_conscious_declaration_not_the_default(self) -> None:
        declared = resolve_skills({"skills": []})
        self.assertIsNotNone(declared)
        self.assertEqual(declared, [])

    def test_declared_names_pass_through_verbatim(self) -> None:
        self.assertEqual(resolve_skills({"skills": ["deep-research"]}), ["deep-research"])

    def test_malformed_declaration_fails_loudly_naming_the_field(self) -> None:
        for bad in ("deep-research", {"name": "deep-research"}, [""], [42], [None]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    resolve_skills({"skills": bad})
                self.assertIn("skills", str(ctx.exception))


class DeclarationSeamTest(unittest.TestCase):
    """The binding sources the skill surface from the declaration, not a literal."""

    def test_binding_does_not_hard_code_the_skill_surface(self) -> None:
        tree = _parse("runtime/adapters/client.py")
        constructor_call = _call_node(tree, "DeerFlowClient")
        value = _keyword_value(constructor_call, "available_skills")
        if value is None:
            self.fail(
                "skill-declaration seam broken: build_client no longer passes "
                "available_skills to the bound client"
            )
        self.assertFalse(
            isinstance(value, ast.Constant) and value.value is None,
            "skill-declaration seam broken: build_client hard-codes the skill "
            "surface (available_skills=None literal) instead of sourcing it "
            "from the declaration",
        )

    def test_assembly_passes_the_declaration_into_the_binding(self) -> None:
        tree = _parse("runtime/assembly.py")
        build_call = _call_node(tree, "build_client")
        value = _keyword_value(build_call, "available_skills")
        self.assertIsNotNone(
            value,
            "skill-declaration seam broken: run_foreground no longer passes "
            "available_skills (resolved from the ladder declaration) into build_client",
        )
        self.assertTrue(
            "resolve_skills" in ast.dump(value),
            "skill-declaration seam broken: run_foreground's available_skills "
            "argument is not sourced from resolve_skills (the declaration resolver)",
        )

    def test_declaration_resolver_lives_in_the_assembly(self) -> None:
        tree = _parse("runtime/assembly.py")
        resolvers = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "resolve_skills"
        ]
        self.assertEqual(
            resolvers,
            ["resolve_skills"],
            "skill-declaration seam broken: the assembly no longer owns the "
            "declaration resolver",
        )


if __name__ == "__main__":
    unittest.main()
