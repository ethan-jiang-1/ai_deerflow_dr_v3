"""Diagnosis classifier contract: seven terminal classes, mutually exclusive.

@impl DIAG-001"""

from __future__ import annotations

import unittest

from deerflow_deep_research.domain.diagnosis import (
    DiagnosticsPresence,
    classify,
)
from deerflow_deep_research.domain.journal_policy import JournalEntry
from deerflow_deep_research.domain.state_machine import BundleState


def make_state(*, status: str = "active", delivery: str | None = None, pid: int = 4242) -> BundleState:
    return BundleState(
        schema_version=1, revision=1, status=status, thread_id="t-1", owner_pid=pid,
        deerflow_pin="pin", generation=1, composition="fixture",
        cancel_requested=False, auto_proceed_count=0, auto_proceed_bound=2,
        delivery=delivery,
    )


def entry(category: str, event: str, detail: dict | None = None) -> JournalEntry:
    return JournalEntry(
        timestamp="2026-10-07T00:00:00+00:00", category=category, event=event,
        detail=detail or {},
    ).validate()


NO_PRESENCE = DiagnosticsPresence()


class ClassifierTest(unittest.TestCase):
    def test_model_call_failure_names_the_error_type_and_binding_stage(self) -> None:
        d = classify(
            make_state(status="failed-resume"),
            [entry("terminal", "llm_error_fallback", {"reason": "llm_error_fallback", "error_type": "rate_limit"})],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "model_call_failed")
        self.assertIn("binding", d.stage)
        self.assertIn("rate_limit", d.detail)

    def test_framework_crash_carries_the_exception_name(self) -> None:
        d = classify(
            make_state(status="failed-resume"),
            [entry("terminal", "framework_error", {"reason": "framework_error", "error": "RuntimeError"})],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "framework_crash")
        self.assertIn("RuntimeError", d.detail)

    def test_framework_stop_reason_is_its_own_class(self) -> None:
        d = classify(
            make_state(status="failed-resume"),
            [entry("terminal", "stop_reason", {"reason": "max_turns"})],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "framework_stopped")
        self.assertIn("max_turns", d.detail)

    def test_clarification_exhaustion_points_at_the_artifact(self) -> None:
        d = classify(
            make_state(status="failed-resume"),
            [
                entry("exhaustion", "clarification_bound_exhausted", {"bound": 2}),
                entry("terminal", "run_failed_resume", {"reason": "clarification bound exhausted"}),
            ],
            owner_alive=False,
            diagnostics=DiagnosticsPresence(unanswered_clarifications=True),
        )
        self.assertEqual(d.klass, "clarification_exhausted")
        self.assertTrue(any("unanswered-clarifications.json" in e for e in d.evidence))

    def test_cancellation_is_its_own_class(self) -> None:
        d = classify(
            make_state(status="cancelled"),
            [entry("terminal", "run_cancelled", {"generation": 1})],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "cancelled")

    def test_owner_death_is_detected_without_a_terminal_event(self) -> None:
        d = classify(
            make_state(status="active", pid=999999),
            [], owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "owner_died")
        self.assertTrue(any("state.json" in e for e in d.evidence))

    def test_owner_death_via_status_crash_transfer_is_the_same_class(self) -> None:
        d = classify(
            make_state(status="failed-resume", pid=999999),
            [entry("terminal", "crash_detected", {"reason": "owner process no longer alive"})],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "owner_died")

    def test_active_run_with_live_owner_is_running_not_classified(self) -> None:
        d = classify(
            make_state(status="active"), [], owner_alive=True, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "running")

    def test_completed_and_admitted_is_delivered(self) -> None:
        d = classify(
            make_state(status="completed", delivery="admitted"),
            [entry("terminal", "run_completed", {"generation": 1})],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "delivered")

    def test_completed_without_delivery_is_undelivered(self) -> None:
        for delivery in (None, "rejected", "no-answer"):
            with self.subTest(delivery=delivery):
                d = classify(
                    make_state(status="completed", delivery=delivery),
                    [entry("terminal", "run_completed", {"generation": 1})],
                    owner_alive=False, diagnostics=NO_PRESENCE,
                )
                self.assertEqual(d.klass, "completed_undelivered")

    def test_terminal_event_wins_over_a_dead_owner(self) -> None:
        d = classify(
            make_state(status="failed-resume", pid=999999),
            [entry("terminal", "framework_error", {"reason": "framework_error", "error": "ValueError"})],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "framework_crash")

    def test_two_distinct_terminal_events_are_ambiguous_not_guessed(self) -> None:
        d = classify(
            make_state(status="completed"),
            [
                entry("terminal", "run_completed", {"generation": 1}),
                entry("terminal", "framework_error", {"reason": "framework_error", "error": "X"}),
            ],
            owner_alive=False, diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "ambiguous")

    def test_duplicate_identical_terminal_events_are_not_ambiguous(self) -> None:
        e = entry("terminal", "framework_error", {"reason": "framework_error", "error": "X"})
        d = classify(
            make_state(status="failed-resume"), [e, e], owner_alive=False,
            diagnostics=NO_PRESENCE,
        )
        self.assertEqual(d.klass, "framework_crash")

    def test_diagnosis_is_read_only_over_its_inputs(self) -> None:
        entries = [entry("terminal", "run_cancelled", {"generation": 1})]
        classify(make_state(status="cancelled"), entries, owner_alive=False,
                 diagnostics=NO_PRESENCE)
        self.assertEqual(entries[0].detail, {"generation": 1})


if __name__ == "__main__":
    unittest.main()
