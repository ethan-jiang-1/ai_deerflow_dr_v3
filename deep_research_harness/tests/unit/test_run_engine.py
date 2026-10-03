"""Run-engine rule tests (framework-free: scripted events at the domain boundary).

@impl DEW-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from deerflow_deep_research.domain import bundle, journal_policy
from deerflow_deep_research.runtime import bundle_actions, bundle_state
from deerflow_deep_research.runtime import run_engine

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
_FIXED_BUCKET = "d_20261003"


def _event(event_type: str, **data) -> SimpleNamespace:
    return SimpleNamespace(type=event_type, data=data)


def _ai(content: str = "", tool_calls: list | None = None) -> dict:
    message = {"type": "ai", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return message


def _tool_result(call_id: str) -> dict:
    return {"type": "tool", "tool_call_id": call_id, "content": "ok"}


def _ask_call(call_id: str = "c1") -> dict:
    return {"id": call_id, "name": "ask_clarification", "args": {"question": "范围选哪国市场？"}}


class RunEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.scopes = Path(self._tmp.name) / "scopes"
        self.state = bundle_actions.start(
            self.scopes, problem_text="研究 A 国无人机供应链的认证壁垒", composition="all_real",
            deerflow_pin=_PIN, now=_FIXED_NOW,
        )
        self.handle = bundle_state.BundleHandle.open(self.scopes / _FIXED_BUCKET / self.state.thread_id)

    def test_clean_stream_completes(self) -> None:
        def stream_fn(message: str):
            yield _event("values", title="t")
            yield _event("messages-tuple", message=_ai("最终报告内容"))
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")

    def test_unanswered_clarification_triggers_provenance_marked_continuation(self) -> None:
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _event("messages-tuple", message=_ai(tool_calls=[_ask_call("c1")]))
                yield _event("end")
            else:
                yield _event("messages-tuple", message=_ai("已按假设继续：A 国"))
                yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.auto_proceed_count, 1)
        self.assertEqual(len(turns), 2)
        self.assertIn("[非交互模式·系统自动应答]", turns[1])
        self.assertIn("范围选哪国市场", turns[1])

    def test_exhausted_bound_fails_loud_with_question_file(self) -> None:
        def stream_fn(message: str):
            yield _event("messages-tuple", message=_ai(tool_calls=[_ask_call("c1")]))
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        self.assertEqual(result.auto_proceed_count, 2)
        questions = json.loads(
            (self.handle.root / bundle.UNANSWERED_QUESTIONS_RELATIVE).read_text(encoding="utf-8")
        )
        self.assertEqual(questions["questions"], ["范围选哪国市场？"])
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "exhaustion" for e in entries))

    def test_tool_events_are_journaled(self) -> None:
        def stream_fn(message: str):
            yield _event("messages-tuple", message=_ai(tool_calls=[
                {"id": "t1", "name": "web_search", "args": {"query": "认证壁垒"}}
            ]))
            yield _event("messages-tuple", message=_tool_result("t1"))
            yield _event("custom", event="subagent_started", detail="x")
            yield _event("messages-tuple", message=_ai("结论"))
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "model_tool" and e.event == "model_tool_call" for e in entries))
        self.assertTrue(any(e.category == "model_tool" and e.event == "tool_result" for e in entries))
        self.assertTrue(any(e.category == "subagent" for e in entries))

    def test_stop_reason_transfers_to_failed_resume(self) -> None:
        def stream_fn(message: str):
            yield _event("messages-tuple", message=_ai("部分内容"))
            yield _event("end", stop_reason="token_capped")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "stop_reason" for e in entries))

    def test_observed_cancellation_wins(self) -> None:
        def stream_fn(message: str):
            yield _event("messages-tuple", message=_ai("内容"))
            yield _event("end")

        # The cancel action records the request externally while the run streams.
        bundle_actions.cancel(self.handle)
        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "cancelled")


def journal_mod_entries(handle):
    from deerflow_deep_research.runtime import journal as journal_mod

    return journal_mod.read_entries(handle)


if __name__ == "__main__":
    unittest.main()
