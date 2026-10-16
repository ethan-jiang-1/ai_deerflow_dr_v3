"""The pump's public entry: one clean turn, tool plumbing, the refine direction.

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

from .pump_case import PumpCase, journal_mod_entries


class RunEngineTest(PumpCase):
    def test_clean_stream_completes(self) -> None:
        def stream_fn(message: str):
            yield _event("values", title="t")
            yield _chunk_event(_ai("最终报告内容"))
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")

    def test_tool_events_are_journaled(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event(_ai(tool_calls=[
                {"id": "t1", "name": "web_search", "args": {"query": "认证壁垒"}}
            ]))
            yield _chunk_event(_tool_result("t1"))
            yield _event("custom", event="subagent_started", detail="x")
            yield _chunk_event(_ai("结论"))
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        entries = journal_mod_entries(self.handle)
        tool_turns = [e for e in entries if e.category == "model_tool" and e.event == "model_tool_call"]
        self.assertEqual(len(tool_turns), 1)  # ONE aggregated entry per turn, not per token
        self.assertEqual(tool_turns[0].detail.get("calls"), ["web_search"])
        self.assertTrue(any(e.category == "subagent" for e in entries))

    def test_token_chunks_aggregate_into_one_turn_entry(self) -> None:
        def stream_fn(message: str):
            for token in ["无人", "机进口", "认证"]:
                yield _chunk_event({"type": "ai", "content": token})
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        entries = journal_mod_entries(self.handle)
        text_turns = [e for e in entries if e.category == "model_tool"]
        self.assertEqual(len(text_turns), 1)
        self.assertIn("answer_excerpt", text_turns[0].detail)
        self.assertIn("认证", text_turns[0].detail["answer_excerpt"])

    def test_clean_run_has_no_fallback_behavior(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event({"type": "ai", "content": "正常回答", "additional_kwargs": {}})
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        entries = journal_mod_entries(self.handle)
        self.assertFalse(any(e.event == "llm_error_fallback" for e in entries))

    def test_generation_two_message_is_the_refine_direction(self) -> None:
        done = state_machine.rule_run_terminal(self.state, "completed")
        bundle_state.write_state(self.handle, self.state, done)
        refined, _record = bundle_actions.refine(self.handle, "深挖成本侧证据")

        first_messages: list[str] = []

        def stream_fn(message: str):
            first_messages.append(message)
            yield _event("values", title="t")
            yield _chunk_event(_ai("第二代报告内容"))
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.generation, 2)
        self.assertTrue(first_messages, "the stream must have been called")
        self.assertIn("深挖成本侧证据", first_messages[0])
        self.assertNotIn("认证壁垒", first_messages[0], "generation 2 must not resend the original problem")

    def test_search_turn_materializes_readable_search_log(self) -> None:
        import json as _json

        def stream_fn(message: str):
            yield _chunk_event(_ai(tool_calls=[{
                "id": "call-s1", "name": "web_search",
                "args": {"query": "无人机 认证壁垒"},
            }]))
            yield _chunk_event(_tool_result("call-s1"))
            yield _event("values", title="t", messages=[_ai("带引用的最终报告")])
            yield _chunk_event(_ai("带引用的最终报告"))
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        path = self.handle.root / "diagnostics" / "searches" / "gen1-001-web_search.json"
        self.assertTrue(path.is_file(), "the search turn must be materialized")
        payload = _json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["arguments"], {"query": "无人机 认证壁垒"})
