"""The wiring smoke: embedded client + sync saver + run engine, zero credentials.

Framework-dependent (skips loudly when the deerflow environment is absent). This is
the pinned experiment that closes the wiring plan's remaining uncertainty.

@impl DEW-001"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

try:
    from deerflow.client import DeerFlowClient  # noqa: F401

    _FRAMEWORK_AVAILABLE = True
except ImportError:  # pragma: no cover — environments without the framework
    _FRAMEWORK_AVAILABLE = False

from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from deerflow_deep_research.runtime.adapters import client as client_binding
from deerflow_deep_research.runtime.bundle import journal as journal_mod
from deerflow_deep_research.runtime import pump


def journal_entries(handle):
    return journal_mod.read_entries(handle)

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
_CONFIG_ROOT = Path(__file__).resolve().parents[2] / "config"

_SCRIPT_CONTINUATION = json.dumps(
    [
        {"content": "", "tool_calls": [{"id": "c1", "name": "ask_clarification", "args": {"question": "范围选哪国市场？"}}]},
        {"content": "已按假设完成：聚焦 A 国市场，认证壁垒分析见报告。"},
    ]
)

_SCRIPT_RAISE = json.dumps([{"raise": "deliberate fixture failure"}])


@unittest.skipUnless(_FRAMEWORK_AVAILABLE, "deerflow environment required: run `uv sync` in deep_research_harness/")
class WiringSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"
        self.state = bundle_actions.start(
            self.runs, problem_text="研究 A 国无人机供应链的认证壁垒", composition="fixture",
            deerflow_pin=_PIN, now=_FIXED_NOW,
        )
        self.handle = bundle_state.BundleHandle.open(self.runs / "d_20261003" / self.state.thread_id)

    def test_multi_turn_run_completes_with_readable_checkpoint(self) -> None:
        os.environ["DEERFLOW_FAKE_SCRIPT"] = _SCRIPT_CONTINUATION
        self.addCleanup(os.environ.pop, "DEERFLOW_FAKE_SCRIPT", None)
        with client_binding.bundle_checkpointer(self.handle) as saver:
            client = client_binding.build_client(
                _CONFIG_ROOT,
                "fixture",
                checkpointer=saver,
                model_name="fixture-scripted",
                snapshot_dir=self.handle.root / "diagnostics",
                pin=_PIN,
            )
            self.assertIsInstance(client, DeerFlowClient)
            result = pump.run_research(
                self.handle, stream_fn=lambda message: client.stream(message, thread_id=self.state.thread_id)
            )
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.auto_proceed_count, 1)  # one bounded continuation turn

        checkpoint = self.handle.root / "checkpoint.sqlite"
        self.assertTrue(checkpoint.is_file(), "the sync saver must land checkpoint.sqlite in the bundle")
        connection = sqlite3.connect(str(checkpoint))
        try:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            connection.close()
        self.assertIn("checkpoints", tables)

        snapshot = self.handle.root / "diagnostics" / "assembly-snapshot.json"
        self.assertTrue(snapshot.is_file(), "the assembly snapshot must be captured once per run")
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual(payload["model_name"], "fixture-scripted")
        self.assertIn("system_prompt", payload)

    def test_raising_model_fails_loud_via_the_framework_fallback(self) -> None:
        # The full chain: scripted model raises → the framework's error-handling
        # middleware renders the deerflow_error_fallback message → the run engine's
        # guard lands the run in failed-resume instead of a silent completion.
        os.environ["DEERFLOW_FAKE_SCRIPT"] = _SCRIPT_RAISE
        self.addCleanup(os.environ.pop, "DEERFLOW_FAKE_SCRIPT", None)
        with client_binding.bundle_checkpointer(self.handle) as saver:
            client = client_binding.build_client(_CONFIG_ROOT, "fixture", checkpointer=saver)
            result = pump.run_research(
                self.handle, stream_fn=lambda message: client.stream(message, thread_id=self.state.thread_id)
            )
        self.assertEqual(result.status, "failed-resume")
        entries = journal_entries(self.handle)
        terminal = [e for e in entries if e.category == "terminal" and e.event == "llm_error_fallback"]
        self.assertEqual(len(terminal), 1)
        self.assertEqual(terminal[0].detail.get("error_type"), "RuntimeError")

    def test_contract_mirror_matches_the_real_surface(self) -> None:
        import inspect

        from deerflow.client import DeerFlowClient

        signature = inspect.signature(DeerFlowClient.__init__)
        mirrored_names = [name for name, _ in client_binding.client_surface.CONSTRUCTOR_PARAMS]
        real_names = [name for name in signature.parameters if name != "self"]
        self.assertEqual(mirrored_names, real_names)
        from deerflow.client import StreamEventType  # noqa: F401 — the mirror pins this Literal

        self.assertEqual(
            list(client_binding.client_surface.STREAM_EVENT_FAMILIES),
            ["values", "messages-tuple", "custom", "end"],
        )


if __name__ == "__main__":
    unittest.main()
