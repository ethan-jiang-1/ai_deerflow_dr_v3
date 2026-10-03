"""Entry-surface tests: renderer phrases, engine hook, watch tail, CLI surface.

@impl ENS-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from deerflow_deep_research.domain import bundle, journal_policy
from deerflow_deep_research.runtime import bundle_actions, bundle_state, render, run_engine

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
_FIXED_BUCKET = "d_20261003"
_GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "recorded" / "clarification-exhaustion.json"


def _event(event_type: str, **data) -> SimpleNamespace:
    return SimpleNamespace(type=event_type, data=data)


def _entry(category: str, event: str, detail: dict) -> journal_policy.JournalEntry:
    return journal_policy.JournalEntry(
        timestamp="2026-10-03T12:00:00Z", category=category, event=event, detail=detail
    ).validate()


class RendererTest(unittest.TestCase):
    def test_tool_call_phrase_is_stable(self) -> None:
        event = _event("messages-tuple", type="ai", tool_calls=[
            {"id": "t1", "name": "web_search", "args": {"query": "认证"}}
        ])
        self.assertEqual(render.event_line(event), "model calls web_search")

    def test_stream_chunk_text_returns_inline_text_only_for_ai_content(self) -> None:
        self.assertEqual(render.stream_chunk_text(_event("messages-tuple", type="ai", content="无人")), "无人")
        self.assertIsNone(render.stream_chunk_text(_event("messages-tuple", type="ai", content="")))
        self.assertIsNone(render.stream_chunk_text(_event("messages-tuple", type="ai", tool_calls=[{"id": "t1", "name": "web_search", "args": {}}])))
        self.assertIsNone(render.stream_chunk_text(_event("messages-tuple", type="tool", tool_call_id="t1", content="ok")))
        self.assertIsNone(render.stream_chunk_text(_event("end")))

    def test_journal_projection_uses_the_same_phrase(self) -> None:
        entry = _entry("model_tool", "model_tool_call", {"calls": ["web_search"]})
        self.assertEqual(render.journal_line(entry), "model calls web_search")

    def test_terminal_phrases(self) -> None:
        self.assertEqual(
            render.journal_line(_entry("terminal", "run_completed", {"generation": 2})),
            "run completed (generation 2)",
        )
        self.assertEqual(
            render.journal_line(_entry("terminal", "stop_reason", {"reason": "token_capped"})),
            "run failed-resume (stop reason: token_capped)",
        )
        self.assertEqual(
            render.journal_line(_entry("exhaustion", "clarification_bound_exhausted", {"bound": 2})),
            "clarification bound exhausted (2)",
        )


class EngineHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.scopes = Path(self._tmp.name) / "scopes"
        self.state = bundle_actions.start(
            self.scopes, problem_text="研究认证壁垒", composition="all_real",
            deerflow_pin=_PIN, now=_FIXED_NOW,
        )
        self.handle = bundle_state.BundleHandle.open(self.scopes / _FIXED_BUCKET / self.state.thread_id)

    def test_on_event_receives_events_without_changing_rules(self) -> None:
        seen: list[str] = []

        def stream_fn(message: str):
            yield _event("messages-tuple", message={"type": "ai", "tool_calls": [
                {"id": "t1", "name": "web_search", "args": {}}
            ]})
            yield _event("end")

        result = run_engine.run_research(
            self.handle, stream_fn=stream_fn, on_event=lambda event: seen.append(event.type)
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(seen, ["messages-tuple", "end"])

    def test_terminal_entry_journaled_on_completion(self) -> None:
        def stream_fn(message: str):
            yield _event("messages-tuple", message={"type": "ai", "content": "结论"})
            yield _event("end")

        run_engine.run_research(self.handle, stream_fn=stream_fn)
        from deerflow_deep_research.runtime import journal as journal_mod

        entries = journal_mod.read_entries(self.handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "run_completed" for e in entries))


class WatchTailTest(unittest.TestCase):
    def test_bounded_tail_exits_on_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            journal_path = Path(td) / "journal.jsonl"
            lines = [
                json.dumps({"ts": "t", "category": "lifecycle", "event": "started", "detail": {}}),
                json.dumps({"ts": "t", "category": "terminal", "event": "run_completed", "detail": {"generation": 1}}),
            ]
            journal_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            rendered, reached_terminal, _position = run_engine.tail_journal(journal_path, position=0)
            self.assertTrue(reached_terminal)
            self.assertEqual(len(rendered), 2)
            # Already-terminal: renders history and exits, never waits.
            rendered2, reached2, _pos2 = run_engine.tail_journal(journal_path, position=0)
            self.assertTrue(reached2)
            self.assertEqual(len(rendered2), 2)

    def test_open_tail_without_terminal_keeps_position(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            journal_path = Path(td) / "journal.jsonl"
            journal_path.write_text(
                json.dumps({"ts": "t", "category": "lifecycle", "event": "started", "detail": {}}) + "\n",
                encoding="utf-8",
            )
            rendered, reached_terminal, _position = run_engine.tail_journal(journal_path, position=0)
            self.assertFalse(reached_terminal)
            self.assertEqual(len(rendered), 1)


class GoldenReplayTest(unittest.TestCase):
    def test_recorded_exhaustion_scenario_renders_the_pinned_shape(self) -> None:
        recorded = json.loads(_GOLDEN.read_text(encoding="utf-8"))
        rendered = [render.journal_line(_entry(e["category"], e["event"], e["detail"])) for e in recorded["entries"]]
        self.assertEqual(rendered, recorded["expected_lines"])


if __name__ == "__main__":
    unittest.main()
