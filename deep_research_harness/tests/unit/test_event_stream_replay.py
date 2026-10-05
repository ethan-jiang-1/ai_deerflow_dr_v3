"""Replay the recorded real event stream through the run engine.

The fixture is a real run's verbatim event stream (type + data dicts). The replay
asserts terminal honesty and journal shape — the flat-chunk adapter bug's permanent
scar: fake-shaped events once passed green while the real stream differed.

@impl DEW-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from deerflow_deep_research.domain import bundle
from deerflow_deep_research.runtime import run_engine
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "replay" / "real-small-stream.json"
_PIN = "c" * 40


@unittest.skipUnless(FIXTURE.is_file(), "replay fixture not recorded yet: run `make record-stream PROBLEM=…`")
class EventStreamReplayTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.scopes = Path(self._tmp.name) / "scopes"
        recorded = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.events = recorded["events"]
        state = bundle_actions.start(
            self.scopes, problem_text=recorded["problem"], composition="all_real",
            deerflow_pin=_PIN, now=datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc),
        )
        self.handle = bundle_state.BundleHandle.open(self.scopes / "d_20261003" / state.thread_id)

    def _stream_fn(self):
        iterator = iter(self.events)

        def _stream(message: str):
            return (SimpleEvent(e["type"], e["data"]) for e in iterator)

        return _stream

    def test_replayed_real_stream_lands_the_recorded_shape(self) -> None:
        result = run_engine.run_research(self.handle, stream_fn=self._stream_fn())
        self.assertEqual(result.status, "completed")  # the recorded run was a clean completion
        entries = self._journal()
        model_turns = [e for e in entries if e.category == "model_tool" and e.event == "model_tool_call"]
        self.assertTrue(model_turns, "the real stream must produce aggregated model_tool turns")
        self.assertTrue(any(e.category == "terminal" and e.event == "run_completed" for e in entries))

    def test_tampered_tool_calls_go_red(self) -> None:
        # The flat-chunk bug's permanent scar: mutate a recorded tool_calls field and
        # the journal shape must change (the adapter must keep reading real chunks).
        tampered = [dict(e) for e in self.events]
        for e in tampered:
            if e["type"] == "messages-tuple" and isinstance(e["data"], dict) and e["data"].get("tool_calls"):
                e["data"] = {**e["data"], "tool_calls": [{**tc, "name": "tampered_tool"} for tc in e["data"]["tool_calls"]]}
        self.events = tampered
        run_engine.run_research(self.handle, stream_fn=self._stream_fn())
        entries = self._journal()
        calls = [call for e in entries if e.category == "model_tool" for call in e.detail.get("calls", [])]
        self.assertIn("tampered_tool", calls, "tampered tool_calls must surface in the journal")

    def _journal(self):
        from deerflow_deep_research.runtime.bundle import journal as journal_mod

        return journal_mod.read_entries(self.handle)


class SimpleEvent:
    def __init__(self, type: str, data: dict) -> None:  # noqa: A002 — mirrors StreamEvent
        self.type = type
        self.data = data


if __name__ == "__main__":
    unittest.main()
