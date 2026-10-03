"""Subagent posture guard: the configs declare no custom subagent types, and any
future declaration must satisfy the depth self-check (task excluded from
disallowed_tools).

Dependency-free (stdlib text scanning — the unit gate environment has no YAML parser).
The guard fails closed: a shape it cannot parse is a red, never a silent pass.

@impl DEW-001"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from deerflow_deep_research.domain.state_machine import RuleViolation
from deerflow_deep_research.runtime import subagent_posture

CONFIG_ROOT = Path(__file__).resolve().parents[2] / "config"

POSTURE_MARK = "no custom subagent types"


class PostureDeclaredTest(unittest.TestCase):
    def test_both_configs_declare_the_posture(self) -> None:
        for name in ("base", "fixture"):
            text = (CONFIG_ROOT / f"{name}.yaml").read_text(encoding="utf-8")
            self.assertIn(POSTURE_MARK, text, f"{name}.yaml lacks the subagent posture block")


class DepthSelfCheckTest(unittest.TestCase):
    def test_configs_declare_no_custom_subagents(self) -> None:
        for name in ("base", "fixture"):
            text = (CONFIG_ROOT / f"{name}.yaml").read_text(encoding="utf-8")
            self.assertEqual(
                subagent_posture.check_custom_agents(text, source=f"config/{name}.yaml"), [], name
            )

    def test_guard_goes_red_on_a_violating_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            violating = Path(td) / "violating.yaml"
            violating.write_text(
                "subagents:\n"
                "  custom_agents:\n"
                "    - name: fetcher\n"
                "      disallowed_tools: []\n",
                encoding="utf-8",
            )
            with self.assertRaises(RuleViolation) as ctx:
                subagent_posture.check_custom_agents(
                    violating.read_text(encoding="utf-8"), source="violating.yaml"
                )
            message = str(ctx.exception)
            self.assertIn("violating.yaml", message)  # names the config file
            self.assertIn("fetcher", message)  # names the offender
            self.assertIn("task", message)  # names the remedy

    def test_guard_passes_on_a_compliant_declaration(self) -> None:
        compliant = (
            "subagents:\n"
            "  custom_agents:\n"
            "    - name: fetcher\n"
            "      disallowed_tools: [task]\n"
        )
        declared = subagent_posture.check_custom_agents(compliant, source="compliant.yaml")
        self.assertEqual(declared, [{"name": "fetcher", "disallowed_tools": ["task"]}])


if __name__ == "__main__":
    unittest.main()
