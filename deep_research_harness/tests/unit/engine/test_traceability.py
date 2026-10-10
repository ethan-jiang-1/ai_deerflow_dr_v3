"""Source-traceability machine: report URLs versus the run's search corpus.

The fixture pin drives the real pump over the recorded stream and asserts the
recorded report's URLs are fully supported by the materialized corpus; the
negative cases prove the verdict cannot pass on empty or tampered input.

@impl RUA-002"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from deerflow_deep_research.engine import traceability
from deerflow_deep_research.runtime import pump
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "replay" / "real-small-stream.json"


def _replay_report_and_corpus(tmp: str) -> tuple[str, str]:
    """Drive the recorded stream through the real pump; return (report, corpus)."""
    recorded = json.loads(FIXTURE.read_text(encoding="utf-8"))
    runs = Path(tmp) / "runs"
    state = bundle_actions.start(
        runs, problem_text=recorded["problem"], composition="all_real",
        deerflow_pin="c" * 40, now=datetime(2026, 10, 3, 12, 0, tzinfo=UTC),
    )
    handle = bundle_state.BundleHandle.open(runs / "d_20261003" / state.thread_id)
    events = iter(recorded["events"])

    class SimpleEvent:
        def __init__(self, type: str, data: dict) -> None:  # noqa: A002
            self.type = type
            self.data = data

    pump.run_research(handle, stream_fn=lambda message: (SimpleEvent(e["type"], e["data"]) for e in events))
    report = (handle.root / "final" / "report-gen1.md").read_text(encoding="utf-8")
    records = [
        (r["content"], r["arguments"])
        for r in (
            json.loads(f.read_text(encoding="utf-8"))
            for f in (handle.root / "diagnostics" / "searches").glob("*.json")
        )
    ]
    return report, traceability.search_corpus_text(records)


@unittest.skipUnless(FIXTURE.is_file(), "replay fixture not recorded yet: run `make record-stream PROBLEM=…`")
class SourceTraceabilityTest(unittest.TestCase):
    def test_recorded_report_is_fully_traceable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report, corpus = _replay_report_and_corpus(tmp)
            verdict = traceability.trace_source_urls(report, corpus)
            self.assertTrue(verdict.urls, "the recorded report must contain URLs to trace")
            self.assertEqual(verdict.untraceable, (), "every recorded URL must be supported")

    def test_unknown_url_is_named(self) -> None:
        verdict = traceability.trace_source_urls(
            "结论见 https://easa.europa.eu/rules\n另有 https://example.invalid/never-searched",
            "search output mentioning https://easa.europa.eu/rules only",
        )
        self.assertEqual(verdict.traceable, ("https://easa.europa.eu/rules",))
        self.assertEqual(verdict.untraceable, ("https://example.invalid/never-searched",))

    def test_empty_corpus_cannot_pass(self) -> None:
        verdict = traceability.trace_source_urls("see https://a.example/x and https://b.example/y", "")
        self.assertEqual(verdict.traceable, ())
        self.assertEqual(len(verdict.untraceable), 2)

    def test_removing_a_record_drops_its_support(self) -> None:
        report = "backed by https://backed.example/source and https://lonely.example/src"
        corpus_backed = "raw output containing https://backed.example/source"
        corpus_lonely = "raw output containing https://lonely.example/src"
        full = traceability.trace_source_urls(report, corpus_backed + "\n" + corpus_lonely)
        self.assertEqual(full.untraceable, ())
        without_lonely = traceability.trace_source_urls(report, corpus_backed)
        self.assertEqual(without_lonely.untraceable, ("https://lonely.example/src",))


if __name__ == "__main__":
    unittest.main()
