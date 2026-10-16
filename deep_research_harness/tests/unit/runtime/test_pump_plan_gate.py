"""The first-generation plan gate: confirm, amend, skip, degrade honestly.

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
from support import chunk_event as _chunk_event
from support import event as _event
from support import tool_result as _tool_result

from deerflow_deep_research.domain import bundle, state_machine
from deerflow_deep_research.runtime import pump
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from tests.fixture_reports import fixture_report

from .pump_case import _FIXED_BUCKET, PumpCase, journal_mod_entries


class RunEngineTest(PumpCase):
    def test_plan_hook_gates_first_turn_and_injects_confirmed_plan(self) -> None:
        turns: list[str] = []
        plans: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(self._MARKED_PLAN))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告：按计划完成"))
                yield _event("end")

        def on_plan(plan: str) -> str:
            plans.append(plan)
            return plan  # confirm as-is

        result = pump.run_research(self.handle, stream_fn=stream_fn, on_plan=on_plan)
        self.assertEqual(result.status, "completed")
        # The hook received the proposed plan; the plan turn was NOT the report.
        self.assertEqual(plans, [self._PLAN_TEXT])
        # The first message carries the problem plus a plan-request framing.
        self.assertIn("研究 A 国无人机供应链的认证壁垒", turns[0])
        self.assertNotIn(self._PLAN_TEXT, turns[0])
        # The framing binds the two channels (deerflow-wiring spec delta): question
        # turns carry only ask_clarification; plan confirmation only via the markers.
        self.assertIn("通道纪律", turns[0])
        self.assertIn("ask_clarification", turns[0])
        # The continuation injects the confirmed plan.
        self.assertIn(self._PLAN_TEXT, turns[1])
        # The confirmed plan is materialized as a request artifact.
        plan_file = self.handle.root / "request" / "plan-gen1.md"
        self.assertTrue(plan_file.is_file())
        self.assertIn("广度探索", plan_file.read_text(encoding="utf-8"))
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("plan_proposed", events)
        self.assertIn("plan_confirmed", events)

    def test_plan_amendment_injects_the_revised_plan(self) -> None:
        turns: list[str] = []
        amended = self._PLAN_TEXT + "\n\n用户修订意见：补一个竞品对比角度"

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(self._MARKED_PLAN))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn, on_plan=lambda p: amended,
        )
        self.assertEqual(result.status, "completed")
        self.assertIn("用户修订意见", turns[1])
        plan_file = self.handle.root / "request" / "plan-gen1.md"
        self.assertIn("用户修订意见", plan_file.read_text(encoding="utf-8"))
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("plan_amended", events)

    def test_plan_skip_injects_proceed_message_and_writes_no_file(self) -> None:
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(self._MARKED_PLAN))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn, on_plan=lambda p: None,
        )
        self.assertEqual(result.status, "completed")
        self.assertIn("跳过计划注入", turns[1])
        self.assertNotIn(self._PLAN_TEXT, turns[1])
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("plan_skipped", events)

    def test_markerless_report_turn_degrades_the_plan_gate_honestly(self) -> None:
        """The real-ladder regression (bundle 58b5440e): a research turn ending in a
        plain-text report has an empty terminal tool-call picture exactly like a plan
        turn — only content markers can distinguish them."""
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(tool_calls=[
                    {"id": "t1", "name": "web_search", "args": {"query": "认证壁垒"}}
                ]))
                yield _chunk_event(_tool_result("t1"))
                yield _chunk_event(_ai("一回合跑完的研究报告（无计划标记）"))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn, on_plan=lambda p: self.fail("gate must not fire"),
        )
        # Nothing force-blocked: the run completed under today's rules in ONE turn —
        # no spurious plan prompt on the report, no injected skip, no second pass.
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(turns), 1)
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("plan_gate_degraded", events)

    def test_markerless_plain_answer_also_degrades(self) -> None:
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai("这不是计划，只是闲聊式回答"))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn, on_plan=lambda p: self.fail("gate must not fire"),
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(turns), 1)
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("plan_gate_degraded", events)

    def test_markers_never_leak_into_hook_or_artifact(self) -> None:
        received: list[str] = []
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(self._MARKED_PLAN))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        def on_plan(plan: str) -> str:
            received.append(plan)
            return plan

        pump.run_research(self.handle, stream_fn=stream_fn, on_plan=on_plan)
        self.assertEqual(received, [self._PLAN_TEXT])  # inner text only, no markers
        plan_file = self.handle.root / "request" / "plan-gen1.md"
        self.assertNotIn("research-plan", plan_file.read_text(encoding="utf-8"))
        # The injected continuation carries the inner plan, not the markers.
        self.assertIn(self._PLAN_TEXT, turns[1])
        self.assertNotIn("<research-plan>", turns[1])

    def test_plan_hook_is_ignored_for_refine_generations(self) -> None:
        def first_run(message: str):
            yield _chunk_event(_ai("第一代报告"))
            yield _event("end")

        pump.run_research(self.handle, stream_fn=first_run)
        refined_state, _record = None, None
        refined_state, _record = bundle_actions.refine(self.handle, "深挖竞品对比")
        self.handle = bundle_state.BundleHandle.open(
            self.runs / _FIXED_BUCKET / refined_state.thread_id
        )

        turns: list[str] = []

        def second_run(message: str):
            turns.append(message)
            yield _chunk_event(_ai("第二代报告"))
            yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=second_run, on_plan=lambda p: self.fail("refine must not gate"),
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(turns), 1)
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())
