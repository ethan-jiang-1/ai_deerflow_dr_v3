"""The CLI journey: create → watch → status → refine → inspect over the fixture ladder.

Framework-dependent (skips loudly without the deerflow environment); drives the REAL
cli.py as a subprocess so the human path is what is tested.

@impl ENS-001"""

from __future__ import annotations

import json
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


def _cli(*arguments: str, env: dict | None = None) -> subprocess.CompletedProcess:
    import os

    merged = dict(os.environ)
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, "cli.py", *arguments],
        cwd=HARNESS_ROOT, capture_output=True, text=True, timeout=120, env=merged,
    )


@unittest.skipUnless(_FRAMEWORK_AVAILABLE, "deerflow environment required: run `uv sync` in deep_research_harness/")
class CliJourneyTest(unittest.TestCase):
    def test_create_watch_status_refine_inspect(self) -> None:
        # Round-4 ruling: the create script walks a real web_search tool call
        # through the fake provider so the journey proves search materialization.
        created = _cli(
            "create", "研究 A 国无人机供应链的认证壁垒", "--config", "fixture",
            env={"DEERFLOW_FAKE_SCRIPT": json.dumps([
                {"content": "", "tool_calls": [{
                    "id": "call-s1", "name": "web_search",
                    "args": {"query": "无人机 认证壁垒"},
                }]},
                {"content": "Fixture answer with cited sources."},
            ])},
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        match = re.search(r"bundle ([0-9a-f-]{36}) started", created.stdout)
        self.assertIsNotNone(match, created.stdout)
        bundle_id = match.group(1)
        self.assertIn("run completed", created.stdout)

        # Observe the accepted product artifact as well as the printed terminal state.
        bundle_dirs = list((HARNESS_ROOT.parent / "runs").glob(f"d_*/{bundle_id}"))
        self.assertEqual(len(bundle_dirs), 1)
        report = bundle_dirs[0] / "final/report-gen1.md"
        self.assertTrue(report.is_file(), created.stdout)
        self.assertTrue(report.read_text(encoding="utf-8").strip())
        entries = [json.loads(line) for line in (bundle_dirs[0] / "evidence/submissions.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(e["kind"] == "final_report" and e["disposition"] == "admit" and e["artifact_path"] == "final/report-gen1.md" for e in entries))

        # Round-4 ruling: the search result is materialized readable.
        search_log = bundle_dirs[0] / "diagnostics" / "searches" / "gen1-001-web_search.json"
        self.assertTrue(search_log.is_file(), created.stdout)
        search_payload = json.loads(search_log.read_text(encoding="utf-8"))
        self.assertEqual(search_payload["arguments"], {"query": "无人机 认证壁垒"})
        self.assertIn("Canned search results", search_payload["content"])

        watched = _cli("watch", bundle_id)
        self.assertEqual(watched.returncode, 0, watched.stderr)
        self.assertIn("run completed", watched.stdout)  # already-terminal: history + exit

        status = _cli("status", bundle_id)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("state: completed", status.stdout)
        self.assertIn("delivery: admitted (final/report-gen1.md)", status.stdout)

        # Phase 5 round-2 ruling: refine drives the next generation to an honest
        # terminal in the foreground. A distinct scripted answer avoids the
        # admission validator's duplicate-hash rejection against generation 1.
        refined = _cli(
            "refine", bundle_id, "深挖成本侧证据",
            env={"DEERFLOW_FAKE_SCRIPT": json.dumps(
                [{"content": "Refined fixture answer: cost-side evidence summary."}]
            )},
        )
        self.assertEqual(refined.returncode, 0, refined.stderr)
        self.assertIn("generation 2", refined.stdout)
        self.assertIn("state: completed", refined.stdout)
        report2 = bundle_dirs[0] / "final/report-gen2.md"
        self.assertTrue(report2.is_file(), refined.stdout)
        self.assertIn("cost-side", report2.read_text(encoding="utf-8"))
        entries2 = [json.loads(line) for line in (bundle_dirs[0] / "evidence/submissions.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(e["kind"] == "final_report" and e["disposition"] == "admit" and e["artifact_path"] == "final/report-gen2.md" for e in entries2))

        status2 = _cli("status", bundle_id)
        self.assertEqual(status2.returncode, 0, status2.stderr)
        self.assertIn("delivery: admitted (final/report-gen2.md)", status2.stdout)

        inspected = _cli("inspect", bundle_id)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertIn("journal timeline", inspected.stdout)
        self.assertIn("admitted evidence", inspected.stdout)
        self.assertIn("assembly snapshot", inspected.stdout)

        # Negative control: the refined generation is terminal, so cancel must
        # fail loudly naming the active-only precondition (positive cancel wiring
        # is pinned in tests/unit/interaction/test_refine_foreground.py).
        cancelled = _cli("cancel", bundle_id)
        self.assertNotEqual(cancelled.returncode, 0)
        self.assertIn("active", cancelled.stderr)

    def test_diagnose_classifies_a_real_failed_run(self) -> None:
        # The scripted model raises; the framework's real error-fallback path
        # turns it into an honest failed-resume. Zero credentials (fixture ladder).

        # @impl DIAG-001
        failed = _cli(
            "create", "诊断旅程：真实模型调用失败", "--config", "fixture",
            env={"DEERFLOW_FAKE_SCRIPT": json.dumps([{"raise": "deliberate journey failure"}])},
        )
        self.assertEqual(failed.returncode, 0, failed.stderr)
        match = re.search(r"bundle ([0-9a-f-]{36}) started", failed.stdout)
        self.assertIsNotNone(match, failed.stdout + failed.stderr)
        bundle_id = match.group(1)
        self.assertIn("run failed-resume", failed.stdout)

        diagnosed = _cli("diagnose", bundle_id)
        self.assertEqual(diagnosed.returncode, 0, diagnosed.stderr)
        self.assertIn("diagnosis: model_call_failed", diagnosed.stdout)
        self.assertIn("evidence: diagnostics/journal.jsonl", diagnosed.stdout)

    def test_unknown_verb_and_missing_bundle_fail_loudly(self) -> None:
        unknown = _cli("teleport", "x")
        self.assertNotEqual(unknown.returncode, 0)
        self.assertTrue(
            "invalid choice" in (unknown.stderr + unknown.stdout)
            or "teleport" in (unknown.stderr + unknown.stdout)
        )
        missing = _cli("status", "ffffffff-ffff-ffff-ffff-ffffffffffff")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("permanently unavailable", missing.stderr)


if __name__ == "__main__":
    unittest.main()
