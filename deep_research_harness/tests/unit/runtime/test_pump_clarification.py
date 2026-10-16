"""Clarification: asked, answered, declined, absorbed — and the bound.

The bodies moved verbatim from the old `test_run_engine.py`; the shared case
(`setUp` and the scripted-stream helpers) lives in `pump_case.py`.

@impl DEW-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from support import ai as _ai
from support import ask_call as _ask_call
from support import chunk_event as _chunk_event
from support import event as _event

from deerflow_deep_research.domain import bundle, state_machine
from deerflow_deep_research.runtime import pump
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from tests.fixture_reports import fixture_report

from .pump_case import PumpCase, journal_mod_entries


class RunEngineTest(PumpCase):
    def test_unanswered_clarification_triggers_provenance_marked_continuation(self) -> None:
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(tool_calls=[_ask_call("c1")]))
                yield _event("end")
            else:
                yield _chunk_event(_ai("已按假设继续：A 国"))
                yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.auto_proceed_count, 1)
        self.assertEqual(len(turns), 2)
        self.assertIn("[非交互模式·系统自动应答]", turns[1])
        self.assertIn("范围选哪国市场", turns[1])

    def test_interactive_answer_continues_without_consuming_bound(self) -> None:
        turns: list[str] = []
        asked: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(tool_calls=[_ask_call("c1")]))
                yield _event("end")
            else:
                yield _chunk_event(_ai("已对齐范围，继续研究"))
                yield _event("end")

        def on_clarification(question: str) -> str:
            asked.append(question)
            return "A 国，聚焦消费级无人机"

        result = pump.run_research(
            self.handle, stream_fn=stream_fn, on_clarification=on_clarification,
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(asked, ["范围选哪国市场？"])
        # The answer continues the run as the human's own words — no provenance prefix.
        self.assertEqual(turns[1], "A 国，聚焦消费级无人机")
        # An answered interactive round does not consume the auto bound.
        self.assertEqual(result.auto_proceed_count, 0)
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("clarification_asked", events)
        self.assertIn("clarification_answered", events)

    def test_declined_interactive_question_falls_back_to_auto_reply(self) -> None:
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(tool_calls=[_ask_call("c1")]))
                yield _event("end")
            else:
                yield _chunk_event(_ai("按假设继续"))
                yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn, on_clarification=lambda q: "   ",
        )
        self.assertEqual(result.status, "completed")
        # A declined round consumes the auto bound exactly like a headless continuation.
        self.assertEqual(result.auto_proceed_count, 1)
        self.assertIn("[非交互模式·系统自动应答]", turns[1])
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("clarification_declined", events)

    def test_absorbed_ask_is_journaled_headless_without_consuming_bound(self) -> None:
        def stream_fn(message: str):
            yield _event("values", messages=self._absorbed_turn_messages())
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        # The run takes today's completion path — the absorbed round changes nothing.
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.auto_proceed_count, 0)
        absorbed = [e for e in self._lifecycle() if e.event == "clarification_absorbed"]
        self.assertEqual(len(absorbed), 1)
        self.assertEqual(absorbed[0].detail.get("question"), "范围选哪国市场？")
        events = [e.event for e in self._lifecycle()]
        self.assertNotIn("auto_continuation", events)
        self.assertNotIn("clarification_asked", events)

    def test_absorbed_ask_never_fires_the_clarification_hook(self) -> None:
        def stream_fn(message: str):
            yield _event("values", messages=self._absorbed_turn_messages())
            yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn,
            on_clarification=lambda q: self.fail("an absorbed round must not reach the hook"),
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.auto_proceed_count, 0)
        absorbed = [e for e in self._lifecycle() if e.event == "clarification_absorbed"]
        self.assertEqual(len(absorbed), 1)

    def test_absorbed_ask_in_plan_phase_journals_before_the_gate_degrades(self) -> None:
        def stream_fn(message: str):
            yield _event("values", messages=self._absorbed_turn_messages())
            yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn,
            on_plan=lambda p: self.fail("a markerless absorbed turn must not reach the gate"),
        )
        self.assertEqual(result.status, "completed")
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())
        events = [e.event for e in self._lifecycle()]
        self.assertIn("clarification_absorbed", events)
        self.assertIn("plan_gate_degraded", events)
        # The absorbed round is recorded at classification time — before the gate branch.
        self.assertLess(events.index("clarification_absorbed"), events.index("plan_gate_degraded"))

    def test_clarification_inside_plan_phase_composes(self) -> None:
        turns: list[str] = []
        asked: list[str] = []
        plans: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(tool_calls=[_ask_call("c1")]))
                yield _event("end")
            if len(turns) == 2:
                yield _chunk_event(_ai(self._MARKED_PLAN))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        def on_clarification(question: str) -> str:
            asked.append(question)
            return "A 国，消费级"

        def on_plan(plan: str) -> str:
            plans.append(plan)
            return plan

        result = pump.run_research(
            self.handle, stream_fn=stream_fn,
            on_clarification=on_clarification, on_plan=on_plan,
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(asked, ["范围选哪国市场？"])
        # The clarification answer continued the thread; the plan arrived on turn 2.
        self.assertEqual(plans, [self._PLAN_TEXT])
        self.assertEqual(turns[1], "A 国，消费级")
        self.assertIn(self._PLAN_TEXT, turns[2])
        self.assertTrue((self.handle.root / "request" / "plan-gen1.md").is_file())

    def test_exhausted_bound_fails_loud_with_question_file(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event(_ai(tool_calls=[_ask_call("c1")]))
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        self.assertEqual(result.auto_proceed_count, 2)
        questions = json.loads(
            (self.handle.root / bundle.UNANSWERED_QUESTIONS_RELATIVE).read_text(encoding="utf-8")
        )
        self.assertEqual(questions["questions"], ["范围选哪国市场？"])
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "exhaustion" for e in entries))
