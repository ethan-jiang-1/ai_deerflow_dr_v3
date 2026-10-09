"""Ladder level-4 behavior assertions: journal-derived profile and expectations.

The fixture is extracted verbatim from the real recorded run
``runs/d_20261005/5bb2c343-5353-4b5a-8e6f-9c83b587a707`` (34 events, 2026-10-05)
— the richest journal on disk at extraction time. Local run storage never
enters the repository; the fixture is the pinned bridge. This observes, never
admits (test-evidence spec).

@impl TES-002"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from deerflow_deep_research.engine.behavior_profile import (
    check_expectations,
    profile_journal,
)

_FIXTURE = (
    Path(__file__).resolve().parents[2] / "fixtures" / "replay" / "real-research-journal.jsonl"
)


def _load_fixture() -> list[dict]:
    lines = _FIXTURE.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


class FixtureProfileTest(unittest.TestCase):
    """The pinned values below are the recorded run's actual profile."""

    def test_real_run_profile_is_pinned(self) -> None:
        profile = profile_journal(_load_fixture())
        self.assertEqual(
            dict(profile.tool_calls),
            {"web_fetch": 3, "web_search": 9, "task": 1},
        )
        self.assertEqual(profile.unknown_tools, ())
        self.assertEqual(
            dict(profile.event_counts),
            {
                "subagent_event": 31,
                "model_tool_call": 1,
                "run_completed": 1,
                "disposition_recorded": 1,
            },
        )
        self.assertEqual(profile.event_total, 34)
        self.assertAlmostEqual(profile.span_seconds, 892.453737, places=6)

    def test_declared_expectations_hold_on_real_run(self) -> None:
        profile = profile_journal(_load_fixture())
        self.assertEqual(
            check_expectations(
                profile,
                tool_calls={"web_search": 9, "web_fetch": 3, "task": 1},
                event_counts={"subagent_event": 31},
                event_total=34,
                span_seconds=892.453737,
                min_search_calls=1,
            ),
            (),
        )


class TamperedExpectationTest(unittest.TestCase):
    def test_wrong_tool_count_is_named(self) -> None:
        profile = profile_journal(_load_fixture())
        violations = check_expectations(profile, tool_calls={"web_search": 8})
        self.assertTrue(
            any("tool_calls.web_search" in v for v in violations),
            f"expected a named web_search violation, got {violations}",
        )

    def test_wrong_event_total_is_named(self) -> None:
        profile = profile_journal(_load_fixture())
        violations = check_expectations(profile, event_total=33)
        self.assertTrue(
            any("event_total" in v for v in violations),
            f"expected a named event_total violation, got {violations}",
        )


class DegenerateResearchTest(unittest.TestCase):
    def test_zero_search_calls_is_named_degenerate(self) -> None:
        events = [
            {
                "ts": "2026-10-07T05:30:43.610179+00:00",
                "category": "lifecycle",
                "event": "clarification_asked",
                "detail": {"question": "范围选哪国市场？"},
            },
            {
                "ts": "2026-10-07T05:30:43.626259+00:00",
                "category": "terminal",
                "event": "run_completed",
                "detail": {"generation": 1},
            },
        ]
        profile = profile_journal(events)
        violations = check_expectations(profile, min_search_calls=1)
        self.assertTrue(
            any("degenerate research" in v for v in violations),
            f"expected the degenerate face to be named, got {violations}",
        )


class UnknownToolTest(unittest.TestCase):
    def test_unknown_tool_surfaces_instead_of_bucketing(self) -> None:
        events = [
            {
                "ts": "2026-10-07T05:30:43.609934+00:00",
                "category": "model_tool",
                "event": "model_tool_call",
                "detail": {"calls": ["web_search", "mystery_tool"]},
            }
        ]
        profile = profile_journal(events)
        self.assertEqual(profile.unknown_tools, ("mystery_tool",))
        self.assertEqual(dict(profile.tool_calls), {"web_search": 1, "mystery_tool": 1})


class SpanTest(unittest.TestCase):
    def test_journal_without_timestamps_has_no_span(self) -> None:
        events = [{"event": "run_completed", "detail": {"generation": 1}}]
        profile = profile_journal(events)
        self.assertIsNone(profile.span_seconds)
        violations = check_expectations(profile, span_seconds=1.0)
        self.assertTrue(
            any("span_seconds" in v for v in violations),
            f"expected a span violation naming the missing timestamps, got {violations}",
        )


if __name__ == "__main__":
    unittest.main()
