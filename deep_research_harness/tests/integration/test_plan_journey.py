"""The plan-gate journeys: the agent proposes, the operator confirms or amends.

Framework-dependent (skips loudly without the deerflow environment); drives the real
cli.py as a subprocess with DEEP_RESEARCH_INTERACTIVE=1 and piped stdin, so the
plan prompt is exercised end-to-end without a TTY.

@impl ENS-001"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

try:
    from deerflow.client import DeerFlowClient  # noqa: F401

    _FRAMEWORK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FRAMEWORK_AVAILABLE = False

HARNESS_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = HARNESS_ROOT.parent / "runs"

_PLAN = "研究计划：1) 广度探索无人机认证壁垒全景 2) 深挖 A 国消费级法规"
_MARKED_PLAN = "<research-plan>\n" + _PLAN + "\n</research-plan>"
_FINAL = "Fixture report produced under the confirmed plan."
_FINAL_UNMARKED = "One-turn research report without any plan markers (the 58b5440e regression shape)."


@unittest.skipUnless(_FRAMEWORK_AVAILABLE, "deerflow environment required: run `uv sync` in deep_research_harness/")
class PlanGateJourneyTest(unittest.TestCase):
    def _create(self, piped_input: str) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.update({
            "DEERFLOW_FAKE_SCRIPT": json.dumps([
                {"content": _MARKED_PLAN},
                {"content": _FINAL},
            ]),
            "DEEP_RESEARCH_INTERACTIVE": "1",
        })
        return subprocess.run(
            [sys.executable, "cli.py", "create", "研究无人机供应链的认证壁垒", "--config", "fixture"],
            cwd=HARNESS_ROOT, capture_output=True, text=True, timeout=120,
            env=env, input=piped_input,
        )

    def _bundle_dir(self, stdout: str) -> Path:
        match = re.search(r"bundle ([0-9a-f-]{36}) started", stdout)
        self.assertIsNotNone(match, stdout)
        return next(RUNS_ROOT.glob(f"d_*/{match.group(1)}"))

    def test_confirmed_plan_gates_injects_and_materializes(self) -> None:
        result = self._create("\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        # The plan reached the operator through the shared rendering.
        self.assertIn("agent 的研究计划", result.stdout)
        self.assertIn(_PLAN, result.stdout)
        self.assertIn("run completed", result.stdout)

        bundle_dir = self._bundle_dir(result.stdout)
        state = json.loads((bundle_dir / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "completed")
        # The plan turn was gated, not admitted; the final report is the second turn.
        self.assertEqual((bundle_dir / "final" / "report-gen1.md").read_text(encoding="utf-8").strip(), _FINAL)
        # The confirmed plan is materialized as a request artifact.
        plan_file = bundle_dir / "request" / "plan-gen1.md"
        self.assertTrue(plan_file.is_file())
        self.assertIn("广度探索", plan_file.read_text(encoding="utf-8"))
        journal = (bundle_dir / "diagnostics" / "journal.jsonl").read_text(encoding="utf-8")
        self.assertIn("plan_proposed", journal)
        self.assertIn("plan_confirmed", journal)

    def test_amended_plan_carries_the_revision_note(self) -> None:
        result = self._create("补一个竞品对比角度\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("agent 的研究计划", result.stdout)

        bundle_dir = self._bundle_dir(result.stdout)
        plan_file = bundle_dir / "request" / "plan-gen1.md"
        content = plan_file.read_text(encoding="utf-8")
        self.assertIn(_PLAN, content)
        self.assertIn("用户修订意见：补一个竞品对比角度", content)
        journal = (bundle_dir / "diagnostics" / "journal.jsonl").read_text(encoding="utf-8")
        self.assertIn("plan_amended", journal)
        state = json.loads((bundle_dir / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "completed")


    def test_markerless_report_completes_without_gating(self) -> None:
        """The real-ladder regression, scripted: a research turn ending in a plain
        report must complete ungated — no plan prompt on the report, no second pass."""
        env = dict(os.environ)
        env.update({
            "DEERFLOW_FAKE_SCRIPT": json.dumps([
                {"content": _FINAL_UNMARKED},
            ]),
            "DEEP_RESEARCH_INTERACTIVE": "1",
        })
        result = subprocess.run(
            [sys.executable, "cli.py", "create", "研究无人机供应链的认证壁垒", "--config", "fixture"],
            cwd=HARNESS_ROOT, capture_output=True, text=True, timeout=120,
            env=env, input="unused\n",  # must never be consumed
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("agent 的研究计划", result.stdout)
        self.assertIn("run completed", result.stdout)

        bundle_dir = self._bundle_dir(result.stdout)
        state = json.loads((bundle_dir / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "completed")
        self.assertEqual(
            (bundle_dir / "final" / "report-gen1.md").read_text(encoding="utf-8").strip(),
            _FINAL_UNMARKED,
        )
        self.assertFalse((bundle_dir / "request" / "plan-gen1.md").exists())
        journal = (bundle_dir / "diagnostics" / "journal.jsonl").read_text(encoding="utf-8")
        self.assertIn("plan_gate_degraded", journal)


if __name__ == "__main__":
    unittest.main()
