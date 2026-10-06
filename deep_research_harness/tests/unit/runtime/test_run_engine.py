"""Run-engine rule tests (framework-free: scripted events at the domain boundary).

@impl DEW-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from deerflow_deep_research.domain import bundle, journal_policy, state_machine
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from deerflow_deep_research.runtime import run_engine

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
_FIXED_BUCKET = "d_20261003"


def _event(event_type: str, **data) -> SimpleNamespace:
    return SimpleNamespace(type=event_type, data=data)


def _chunk_event(chunk: dict) -> SimpleNamespace:
    """A real-shaped messages-tuple event: the data IS the message chunk (flat)."""
    return SimpleNamespace(type="messages-tuple", data=chunk)


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
        self.runs = Path(self._tmp.name) / "runs"
        self.state = bundle_actions.start(
            self.runs, problem_text="研究 A 国无人机供应链的认证壁垒", composition="all_real",
            deerflow_pin=_PIN, now=_FIXED_NOW,
        )
        self.handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / self.state.thread_id)

    def test_clean_stream_completes(self) -> None:
        def stream_fn(message: str):
            yield _event("values", title="t")
            yield _chunk_event(_ai("最终报告内容"))
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")

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

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
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

        result = run_engine.run_research(
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

        result = run_engine.run_research(
            self.handle, stream_fn=stream_fn, on_clarification=lambda q: "   ",
        )
        self.assertEqual(result.status, "completed")
        # A declined round consumes the auto bound exactly like a headless continuation.
        self.assertEqual(result.auto_proceed_count, 1)
        self.assertIn("[非交互模式·系统自动应答]", turns[1])
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("clarification_declined", events)

    _PLAN_TEXT = "研究计划：\n1. 广度探索认证壁垒的全景\n2. 深挖 A 国消费级法规"

    def test_plan_hook_gates_first_turn_and_injects_confirmed_plan(self) -> None:
        turns: list[str] = []
        plans: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            if len(turns) == 1:
                yield _chunk_event(_ai(self._PLAN_TEXT))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告：按计划完成"))
                yield _event("end")

        def on_plan(plan: str) -> str:
            plans.append(plan)
            return plan  # confirm as-is

        result = run_engine.run_research(self.handle, stream_fn=stream_fn, on_plan=on_plan)
        self.assertEqual(result.status, "completed")
        # The hook received the proposed plan; the plan turn was NOT the report.
        self.assertEqual(plans, [self._PLAN_TEXT])
        # The first message carries the problem plus a plan-request framing.
        self.assertIn("研究 A 国无人机供应链的认证壁垒", turns[0])
        self.assertNotIn(self._PLAN_TEXT, turns[0])
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
                yield _chunk_event(_ai(self._PLAN_TEXT))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        result = run_engine.run_research(
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
                yield _chunk_event(_ai(self._PLAN_TEXT))
                yield _event("end")
            else:
                yield _chunk_event(_ai("最终报告"))
                yield _event("end")

        result = run_engine.run_research(
            self.handle, stream_fn=stream_fn, on_plan=lambda p: None,
        )
        self.assertEqual(result.status, "completed")
        self.assertIn("跳过计划注入", turns[1])
        self.assertNotIn(self._PLAN_TEXT, turns[1])
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("plan_skipped", events)

    def test_researching_first_turn_degrades_the_plan_gate_honestly(self) -> None:
        turns: list[str] = []

        def stream_fn(message: str):
            turns.append(message)
            yield _chunk_event(_ai(tool_calls=[
                {"id": "t1", "name": "web_search", "args": {"query": "认证壁垒"}}
            ]))
            yield _chunk_event(_tool_result("t1"))
            yield _chunk_event(_ai("一回合跑完的报告"))
            yield _event("end")

        result = run_engine.run_research(
            self.handle, stream_fn=stream_fn, on_plan=lambda p: self.fail("gate must not fire"),
        )
        # Nothing force-blocked: the run completed under today's rules in one turn.
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(turns), 1)
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())
        events = [e.event for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]
        self.assertIn("plan_gate_degraded", events)

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
                yield _chunk_event(_ai(self._PLAN_TEXT))
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

        result = run_engine.run_research(
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

    def test_plan_hook_is_ignored_for_refine_generations(self) -> None:
        def first_run(message: str):
            yield _chunk_event(_ai("第一代报告"))
            yield _event("end")

        run_engine.run_research(self.handle, stream_fn=first_run)
        refined_state, _record = None, None
        from deerflow_deep_research.runtime.bundle import bundle_actions
        refined_state, _record = bundle_actions.refine(self.handle, "深挖竞品对比")
        self.handle = bundle_state.BundleHandle.open(
            self.runs / _FIXED_BUCKET / refined_state.thread_id
        )

        turns: list[str] = []

        def second_run(message: str):
            turns.append(message)
            yield _chunk_event(_ai("第二代报告"))
            yield _event("end")

        result = run_engine.run_research(
            self.handle, stream_fn=second_run, on_plan=lambda p: self.fail("refine must not gate"),
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(turns), 1)
        self.assertFalse((self.handle.root / "request" / "plan-gen1.md").exists())

    def test_exhausted_bound_fails_loud_with_question_file(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event(_ai(tool_calls=[_ask_call("c1")]))
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
            yield _chunk_event(_ai(tool_calls=[
                {"id": "t1", "name": "web_search", "args": {"query": "认证壁垒"}}
            ]))
            yield _chunk_event(_tool_result("t1"))
            yield _event("custom", event="subagent_started", detail="x")
            yield _chunk_event(_ai("结论"))
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        entries = journal_mod_entries(self.handle)
        tool_turns = [e for e in entries if e.category == "model_tool" and e.event == "model_tool_call"]
        self.assertEqual(len(tool_turns), 1)  # ONE aggregated entry per turn, not per token
        self.assertEqual(tool_turns[0].detail.get("calls"), ["web_search"])
        self.assertTrue(any(e.category == "subagent" for e in entries))

    def test_stop_reason_transfers_to_failed_resume(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event(_ai("部分内容"))
            yield _event("end", stop_reason="token_capped")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "stop_reason" for e in entries))

    def test_observed_cancellation_wins(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event(_ai("内容"))
            yield _event("end")

        # The cancel action records the request externally while the run streams.
        bundle_actions.cancel(self.handle)
        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "cancelled")

    def test_error_fallback_transfers_to_failed_resume(self) -> None:
        fallback_ai = {
            "type": "ai",
            "content": "LLM request failed: No generations found in stream.",
            "additional_kwargs": {"deerflow_error_fallback": True, "error_type": "ValueError"},
        }

        def stream_fn(message: str):
            yield _event("values", messages=[{"type": "human", "content": "q"}, fallback_ai])
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        entries = journal_mod_entries(self.handle)
        terminal = [e for e in entries if e.category == "terminal"]
        self.assertEqual(len(terminal), 1)
        self.assertEqual(terminal[0].event, "llm_error_fallback")
        self.assertEqual(terminal[0].detail.get("error_type"), "ValueError")

    def test_error_fallback_beats_a_clean_completion(self) -> None:
        # The fallback message is an error report: the run must not complete even
        # though the stream reaches end with no stop reason and no clarification.
        # Shape mirrors a real run (values snapshot + messages-tuple, per the wiring
        # smoke diagnostic).
        fallback_ai = {
            "type": "ai",
            "content": "LLM request failed: boom",
            "additional_kwargs": {"deerflow_error_fallback": True, "error_type": "RuntimeError"},
        }

        def stream_fn(message: str):
            yield _event("values", messages=[{"type": "human", "content": "q"}, fallback_ai])
            yield _event("messages-tuple", message=fallback_ai)
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")

    def test_clean_run_has_no_fallback_behavior(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event({"type": "ai", "content": "正常回答", "additional_kwargs": {}})
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        entries = journal_mod_entries(self.handle)
        self.assertFalse(any(e.event == "llm_error_fallback" for e in entries))


    def test_token_chunks_aggregate_into_one_turn_entry(self) -> None:
        def stream_fn(message: str):
            for token in ["无人", "机进口", "认证"]:
                yield _chunk_event({"type": "ai", "content": token})
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        entries = journal_mod_entries(self.handle)
        text_turns = [e for e in entries if e.category == "model_tool"]
        self.assertEqual(len(text_turns), 1)
        self.assertIn("answer_excerpt", text_turns[0].detail)
        self.assertIn("认证", text_turns[0].detail["answer_excerpt"])


    def test_framework_exception_transfers_to_failed_resume(self) -> None:
        def stream_fn(message: str):
            yield _event("values", messages=[])
            raise RuntimeError("GraphRecursionError: limit reached")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "framework_error" for e in entries))

    def test_clean_completion_lands_final_report_through_hold_point(self) -> None:
        def stream_fn(message: str):
            yield _event("values", messages=[
                {"type": "human", "content": "q"},
                {"type": "ai", "content": "最终简报全文内容"},
            ])
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        report = self.handle.root / "final" / f"report-gen{result.generation}.md"
        self.assertTrue(report.is_file(), report)
        self.assertIn("最终简报全文内容", report.read_text(encoding="utf-8"))
        from deerflow_deep_research.runtime.bundle.ledger import read_ledger
        entries = read_ledger(self.handle)
        self.assertTrue(any(e.disposition == "admit" and e.kind == "final_report" for e in entries))

    def test_fallback_completion_never_submits(self) -> None:
        fallback_ai = {"type": "ai", "content": "LLM request failed", "additional_kwargs": {"deerflow_error_fallback": True, "error_type": "RuntimeError"}}

        def stream_fn(message: str):
            yield _event("values", messages=[{"type": "human", "content": "q"}, fallback_ai])
            yield _event("end")

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        self.assertEqual(list((self.handle.root / "final").iterdir()), [], "no report file on a failed run")

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

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.generation, 2)
        self.assertTrue(first_messages, "the stream must have been called")
        self.assertIn("深挖成本侧证据", first_messages[0])
        self.assertNotIn("认证壁垒", first_messages[0], "generation 2 must not resend the original problem")

    def _drive_to_completion(self, answer: str) -> "state_machine.BundleState":
        def stream_fn(message: str):
            yield _event("values", title="t", messages=[_ai(answer)])
            yield _chunk_event(_ai(answer))
            yield _event("end")

        return run_engine.run_research(self.handle, stream_fn=stream_fn)

    def test_clean_completion_records_admitted_delivery(self) -> None:
        self._drive_to_completion("第一代报告内容")
        final = bundle_state.read_state(self.handle)
        self.assertEqual(final.status, "completed")
        self.assertEqual(final.delivery, "admitted")
        self.assertEqual(final.delivery_artifact, "final/report-gen1.md")

    def test_empty_answer_records_no_answer_delivery(self) -> None:
        self._drive_to_completion("   ")
        final = bundle_state.read_state(self.handle)
        self.assertEqual(final.status, "completed")
        self.assertEqual(final.delivery, "no-answer")
        self.assertIsNone(final.delivery_artifact)

    def test_duplicate_refine_answer_records_rejected_delivery_and_stays_refinable(self) -> None:
        from dataclasses import replace as _replace

        first = self._drive_to_completion("完全相同的报告内容")
        self.assertEqual(first.delivery, "admitted")
        refined, _record = bundle_actions.refine(self.handle, "深挖成本侧")
        second = self._drive_to_completion("完全相同的报告内容")  # duplicate hash vs gen 1
        final = bundle_state.read_state(self.handle)
        self.assertEqual(final.status, "completed")
        self.assertEqual(final.delivery, "rejected")
        self.assertIsNone(final.delivery_artifact)
        # refine-after-rejected stays legal: the orthogonal model's point
        refined_again, _r2 = bundle_actions.refine(self.handle, "换个角度")
        self.assertEqual(refined_again.status, "active")


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

        result = run_engine.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        path = self.handle.root / "diagnostics" / "searches" / "gen1-001-web_search.json"
        self.assertTrue(path.is_file(), "the search turn must be materialized")
        payload = _json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["arguments"], {"query": "无人机 认证壁垒"})


def journal_mod_entries(handle):
    from deerflow_deep_research.runtime.bundle import journal as journal_mod

    return journal_mod.read_entries(handle)



if __name__ == "__main__":
    unittest.main()
