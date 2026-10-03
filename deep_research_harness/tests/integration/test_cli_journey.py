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


def _cli(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "cli.py", *arguments],
        cwd=HARNESS_ROOT, capture_output=True, text=True, timeout=120,
    )


@unittest.skipUnless(_FRAMEWORK_AVAILABLE, "deerflow environment required: run `uv sync` in deep_research_harness/")
class CliJourneyTest(unittest.TestCase):
    def test_create_watch_status_refine_inspect(self) -> None:
        created = _cli("create", "研究 A 国无人机供应链的认证壁垒", "--config", "fixture")
        self.assertEqual(created.returncode, 0, created.stderr)
        match = re.search(r"bundle ([0-9a-f-]{36}) started", created.stdout)
        self.assertIsNotNone(match, created.stdout)
        bundle_id = match.group(1)
        self.assertIn("run completed", created.stdout)

        watched = _cli("watch", bundle_id)
        self.assertEqual(watched.returncode, 0, watched.stderr)
        self.assertIn("run completed", watched.stdout)  # already-terminal: history + exit

        status = _cli("status", bundle_id)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("state: completed", status.stdout)

        refined = _cli("refine", bundle_id, "深挖成本侧证据")
        self.assertEqual(refined.returncode, 0, refined.stderr)
        self.assertIn("generation 2", refined.stdout)
        self.assertIn("state: active", refined.stdout)

        inspected = _cli("inspect", bundle_id)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertIn("journal timeline", inspected.stdout)
        self.assertIn("admitted evidence", inspected.stdout)
        self.assertIn("assembly snapshot", inspected.stdout)

        cancelled = _cli("cancel", bundle_id)
        self.assertEqual(cancelled.returncode, 0, cancelled.stderr)
        self.assertIn("cancellation requested", cancelled.stdout)

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
