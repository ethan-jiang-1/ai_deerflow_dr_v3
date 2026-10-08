"""The interactive clarification journey: the agent asks, the operator answers.

Framework-dependent (skips loudly without the deerflow environment); drives the real
cli.py as a subprocess with DEEP_RESEARCH_INTERACTIVE=1 and the answer piped on
stdin, so the prompt is exercised end-to-end without a TTY.

@impl ENS-001"""

from __future__ import annotations

import json
from tests.fixture_reports import fixture_report
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


@unittest.skipUnless(_FRAMEWORK_AVAILABLE, "deerflow environment required: run `uv sync` in deep_research_harness/")
class InteractiveClarificationJourneyTest(unittest.TestCase):
    def test_asked_question_is_answered_and_the_run_completes(self) -> None:
        env = dict(os.environ)
        env.update({
            "DEERFLOW_FAKE_SCRIPT": json.dumps([
                {"content": "", "tool_calls": [{
                    "id": "call-q1", "name": "ask_clarification",
                    "args": {"question": "范围选哪国市场？"},
                }]},
                {"content": fixture_report("已对齐范围：A 国消费级无人机。Fixture answer with cited sources.")},
            ]),
            "DEEP_RESEARCH_INTERACTIVE": "1",
        })
        result = subprocess.run(
            [sys.executable, "cli.py", "create", "研究无人机供应链的认证壁垒", "--config", "fixture"],
            cwd=HARNESS_ROOT, capture_output=True, text=True, timeout=120,
            env=env, input="A 国，聚焦消费级\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        # The question reached the operator through the shared rendering.
        self.assertIn("agent 想问你：范围选哪国市场？", result.stdout)
        self.assertIn("run completed", result.stdout)

        match = re.search(r"bundle ([0-9a-f-]{36}) started", result.stdout)
        self.assertIsNotNone(match, result.stdout)
        bundle_dir = next(RUNS_ROOT.glob(f"d_*/{match.group(1)}"))
        state = json.loads((bundle_dir / "state.json").read_text(encoding="utf-8"))
        # The answered round did not consume the auto bound, and the run completed.
        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["auto_proceed_count"], 0)
        journal = (bundle_dir / "diagnostics" / "journal.jsonl").read_text(encoding="utf-8")
        self.assertIn("clarification_asked", journal)
        self.assertIn("clarification_answered", journal)

    def test_declined_question_falls_back_to_the_bounded_auto_reply(self) -> None:
        env = dict(os.environ)
        env.update({
            "DEERFLOW_FAKE_SCRIPT": json.dumps([
                {"content": "", "tool_calls": [{
                    "id": "call-q1", "name": "ask_clarification",
                    "args": {"question": "范围选哪国市场？"},
                }]},
                {"content": fixture_report("按假设继续：A 国。Fixture answer.")},
            ]),
            "DEEP_RESEARCH_INTERACTIVE": "1",
        })
        result = subprocess.run(
            [sys.executable, "cli.py", "create", "研究无人机供应链的认证壁垒", "--config", "fixture"],
            cwd=HARNESS_ROOT, capture_output=True, text=True, timeout=120,
            env=env, input="\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("agent 想问你：范围选哪国市场？", result.stdout)
        self.assertIn("run completed", result.stdout)

        match = re.search(r"bundle ([0-9a-f-]{36}) started", result.stdout)
        self.assertIsNotNone(match, result.stdout)
        bundle_dir = next(RUNS_ROOT.glob(f"d_*/{match.group(1)}"))
        state = json.loads((bundle_dir / "state.json").read_text(encoding="utf-8"))
        # The declined round consumed the auto bound exactly like a headless continuation.
        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["auto_proceed_count"], 1)
        journal = (bundle_dir / "diagnostics" / "journal.jsonl").read_text(encoding="utf-8")
        self.assertIn("clarification_declined", journal)
        self.assertIn("auto_continuation", journal)


if __name__ == "__main__":
    unittest.main()
