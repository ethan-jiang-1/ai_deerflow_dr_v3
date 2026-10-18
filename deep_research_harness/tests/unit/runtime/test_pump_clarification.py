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
from unittest import mock

from support import ai as _ai
from support import ask_call as _ask_call
from support import chunk_event as _chunk_event
from support import event as _event

from deerflow_deep_research.domain import bundle, state_machine
from deerflow_deep_research.runtime import pump
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from deerflow_deep_research.runtime.pump_parts import gates
from deerflow_deep_research.runtime.pump_parts.gates import clarification_step
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


class GateWriteConsistencyTest(PumpCase):
    """BUG-007: a gate write must CAS against the version it derived its payload from.

    `clarification_step` computed its new state from the caller's (older) view and then CASed
    against a value read *inside* the call expression, so the revision check could never fail
    while the payload was stale — a concurrent update was silently overwritten (the revision
    even looked continuous). These cases pin the property rather than the shape alone.
    """

    def _tool_calls(self) -> list[SimpleNamespace]:
        return [SimpleNamespace(arguments=json.dumps({"question": "范围选哪国市场？"}))]

    def test_a_concurrent_update_survives_the_step(self) -> None:
        caller_state = bundle_state.read_state(self.handle)
        concurrent = state_machine.rule_clarification_step(caller_state, detected=True)
        bundle_state.write_state(self.handle, caller_state, concurrent)

        clarification_step(self.handle, None, caller_state, self._tool_calls())

        persisted = bundle_state.read_state(self.handle)
        self.assertEqual(
            persisted.auto_proceed_count,
            2,
            "the step overwrote a concurrent update instead of building on it",
        )

    def test_a_conflict_is_raised_rather_than_swallowed(self) -> None:
        """The CAS refusing the write must surface — a conflict is not retried away.

        BUG-007 criterion 3: the failure channel is a raise (made readable at the CLI
        boundary), not a silent retry. A writer landing between the gate's own read and the
        read inside `write_state` must therefore produce `StateRevisionConflict`.
        """
        import dataclasses

        caller_state = bundle_state.read_state(self.handle)
        real_read = bundle_state.read_state
        calls = {"n": 0}

        def flaky_read(handle):
            calls["n"] += 1
            state = real_read(handle)
            if calls["n"] == 2:  # the read inside write_state, after the gate's own read
                return dataclasses.replace(state, revision=state.revision + 1)
            return state

        with mock.patch.object(bundle_state, "read_state", flaky_read):
            with self.assertRaises(bundle_state.StateRevisionConflict):
                clarification_step(self.handle, None, caller_state, self._tool_calls())

    def test_no_gate_write_reads_its_expected_value_inside_the_call(self) -> None:
        """The defect's signature: `write_state(..., read_state(...), ...)`."""
        import ast

        offenders: list[str] = []
        for source in sorted(Path(gates.__file__).parent.glob("*.py")):
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if name != "write_state":
                    continue
                arguments = [*node.args, *[keyword.value for keyword in node.keywords]]
                for argument in arguments:
                    for inner in ast.walk(argument):
                        if not isinstance(inner, ast.Call):
                            continue
                        inner_name = (
                            inner.func.attr
                            if isinstance(inner.func, ast.Attribute)
                            else getattr(inner.func, "id", "")
                        )
                        if inner_name == "read_state":
                            offenders.append(f"{source.name}:{node.lineno}")
        self.assertEqual(offenders, [], f"gate writes CAS against an inline read: {offenders}")
