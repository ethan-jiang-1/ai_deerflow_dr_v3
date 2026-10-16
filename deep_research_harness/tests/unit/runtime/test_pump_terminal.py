"""Terminal dispositions and the delivery fact each one carries.

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

from deerflow_deep_research.domain import bundle, state_machine
from deerflow_deep_research.runtime import pump
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from tests.fixture_reports import fixture_report

from .pump_case import PumpCase, journal_mod_entries


class RunEngineTest(PumpCase):
    def test_stop_reason_transfers_to_failed_resume(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event(_ai("部分内容"))
            yield _event("end", stop_reason="token_capped")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "stop_reason" for e in entries))

    def test_observed_cancellation_wins(self) -> None:
        def stream_fn(message: str):
            yield _chunk_event(_ai("内容"))
            yield _event("end")

        # The cancel action records the request externally while the run streams.
        bundle_actions.cancel(self.handle)
        result = pump.run_research(self.handle, stream_fn=stream_fn)
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

        result = pump.run_research(self.handle, stream_fn=stream_fn)
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

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")

    def test_framework_exception_transfers_to_failed_resume(self) -> None:
        def stream_fn(message: str):
            yield _event("values", messages=[])
            raise RuntimeError("GraphRecursionError: limit reached")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        entries = journal_mod_entries(self.handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "framework_error" for e in entries))

    def test_clean_completion_lands_final_report_through_hold_point(self) -> None:
        def stream_fn(message: str):
            yield _event("values", messages=[
                {"type": "human", "content": "q"},
                {"type": "ai", "content": fixture_report("最终简报全文内容")},
            ])
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "completed")
        report = self.handle.root / "final" / f"report-gen{result.generation}.md"
        self.assertTrue(report.is_file(), report)
        self.assertIn("最终简报全文内容", report.read_text(encoding="utf-8"))
        from deerflow_deep_research.runtime.bundle.ledger import read_ledger
        entries = read_ledger(self.handle)
        self.assertTrue(any(e.disposition == "admit" and e.kind == "final_report" for e in entries))

    def test_fallback_completion_never_submits(self) -> None:
        fallback_ai = {
            "type": "ai",
            "content": "LLM request failed",
            "additional_kwargs": {"deerflow_error_fallback": True, "error_type": "RuntimeError"},
        }

        def stream_fn(message: str):
            yield _event("values", messages=[{"type": "human", "content": "q"}, fallback_ai])
            yield _event("end")

        result = pump.run_research(self.handle, stream_fn=stream_fn)
        self.assertEqual(result.status, "failed-resume")
        self.assertEqual(list((self.handle.root / "final").iterdir()), [], "no report file on a failed run")

    def test_clean_completion_records_admitted_delivery(self) -> None:
        self._drive_to_completion(fixture_report("第一代报告内容"))
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

        first = self._drive_to_completion(fixture_report("完全相同的报告内容"))
        self.assertEqual(first.delivery, "admitted")
        refined, _record = bundle_actions.refine(self.handle, "深挖成本侧")
        # duplicate hash vs gen 1 — the call drives the run; its return value is intentionally unused
        self._drive_to_completion(fixture_report("完全相同的报告内容"))
        final = bundle_state.read_state(self.handle)
        self.assertEqual(final.status, "completed")
        self.assertEqual(final.delivery, "rejected")
        self.assertIsNone(final.delivery_artifact)
        # refine-after-rejected stays legal: the orthogonal model's point
        refined_again, _r2 = bundle_actions.refine(self.handle, "换个角度")
        self.assertEqual(refined_again.status, "active")
