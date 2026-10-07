"""Entry-surface tests: renderer phrases, engine hook, watch tail, CLI surface.

@impl ENS-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from deerflow_deep_research.domain import bundle, journal_policy
from deerflow_deep_research.runtime import pump
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from deerflow_deep_research.runtime.interaction import render

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
_FIXED_BUCKET = "d_20261003"
_GOLDEN = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "recorded" / "clarification-exhaustion.json"


def _event(event_type: str, **data) -> SimpleNamespace:
    return SimpleNamespace(type=event_type, data=data)


def _entry(category: str, event: str, detail: dict) -> journal_policy.JournalEntry:
    return journal_policy.JournalEntry(
        timestamp="2026-10-03T12:00:00Z", category=category, event=event, detail=detail
    ).validate()


class RendererTest(unittest.TestCase):
    def test_tool_call_phrase_is_stable(self) -> None:
        event = _event("messages-tuple", type="ai", tool_calls=[
            {"id": "t1", "name": "web_search", "args": {"query": "认证"}}
        ])
        self.assertEqual(render.event_line(event), "model calls web_search")

    def test_stream_chunk_text_returns_inline_text_only_for_ai_content(self) -> None:
        self.assertEqual(render.stream_chunk_text(_event("messages-tuple", type="ai", content="无人")), "无人")
        self.assertIsNone(render.stream_chunk_text(_event("messages-tuple", type="ai", content="")))
        self.assertIsNone(render.stream_chunk_text(_event("messages-tuple", type="ai", tool_calls=[{"id": "t1", "name": "web_search", "args": {}}])))
        self.assertIsNone(render.stream_chunk_text(_event("messages-tuple", type="tool", tool_call_id="t1", content="ok")))
        self.assertIsNone(render.stream_chunk_text(_event("end")))

    def test_journal_projection_uses_the_same_phrase(self) -> None:
        entry = _entry("model_tool", "model_tool_call", {"calls": ["web_search"]})
        self.assertEqual(render.journal_line(entry), "model calls web_search")

    def test_terminal_phrases(self) -> None:
        self.assertEqual(
            render.journal_line(_entry("terminal", "run_completed", {"generation": 2})),
            "run completed (generation 2)",
        )
        self.assertEqual(
            render.journal_line(_entry("terminal", "stop_reason", {"reason": "token_capped"})),
            "run failed-resume (stop reason: token_capped)",
        )
        self.assertEqual(
            render.journal_line(_entry("exhaustion", "clarification_bound_exhausted", {"bound": 2})),
            "clarification bound exhausted (2)",
        )


class EngineHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"
        self.state = bundle_actions.start(
            self.runs, problem_text="研究认证壁垒", composition="all_real",
            deerflow_pin=_PIN, now=_FIXED_NOW,
        )
        self.handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / self.state.thread_id)

    def test_on_event_receives_events_without_changing_rules(self) -> None:
        seen: list[str] = []

        def stream_fn(message: str):
            yield _event("messages-tuple", message={"type": "ai", "tool_calls": [
                {"id": "t1", "name": "web_search", "args": {}}
            ]})
            yield _event("end")

        result = pump.run_research(
            self.handle, stream_fn=stream_fn, on_event=lambda event: seen.append(event.type)
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(seen, ["messages-tuple", "end"])

    def test_terminal_entry_journaled_on_completion(self) -> None:
        def stream_fn(message: str):
            yield _event("messages-tuple", message={"type": "ai", "content": "结论"})
            yield _event("end")

        pump.run_research(self.handle, stream_fn=stream_fn)
        from deerflow_deep_research.runtime.bundle import journal as journal_mod

        entries = journal_mod.read_entries(self.handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "run_completed" for e in entries))


class WatchTailTest(unittest.TestCase):
    def test_bounded_tail_exits_on_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            journal_path = Path(td) / "journal.jsonl"
            lines = [
                json.dumps({"ts": "t", "category": "lifecycle", "event": "started", "detail": {}}),
                json.dumps({"ts": "t", "category": "terminal", "event": "run_completed", "detail": {"generation": 1}}),
            ]
            journal_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            rendered, reached_terminal, _position = pump.tail_journal(journal_path, position=0)
            self.assertTrue(reached_terminal)
            self.assertEqual(len(rendered), 2)
            # Already-terminal: renders history and exits, never waits.
            rendered2, reached2, _pos2 = pump.tail_journal(journal_path, position=0)
            self.assertTrue(reached2)
            self.assertEqual(len(rendered2), 2)

    def test_open_tail_without_terminal_keeps_position(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            journal_path = Path(td) / "journal.jsonl"
            journal_path.write_text(
                json.dumps({"ts": "t", "category": "lifecycle", "event": "started", "detail": {}}) + "\n",
                encoding="utf-8",
            )
            rendered, reached_terminal, _position = pump.tail_journal(journal_path, position=0)
            self.assertFalse(reached_terminal)
            self.assertEqual(len(rendered), 1)


class GoldenReplayTest(unittest.TestCase):
    def test_recorded_exhaustion_scenario_renders_the_pinned_shape(self) -> None:
        recorded = json.loads(_GOLDEN.read_text(encoding="utf-8"))
        rendered = [render.journal_line(_entry(e["category"], e["event"], e["detail"])) for e in recorded["entries"]]
        self.assertEqual(rendered, recorded["expected_lines"])


class DiagnoseSurfaceTest(unittest.TestCase):
    """The diagnose projection: stable phrases, read-only over a real bundle.

    @impl DIAG-001"""

    def test_diagnosis_lines_phrase_is_stable(self) -> None:
        d = SimpleNamespace(
            klass="model_call_failed",
            stage="binding — DeerFlow model call (framework error-fallback)",
            evidence=("diagnostics/journal.jsonl",),
            detail="model call failed (error_type: rate_limit)",
        )
        out = render.diagnosis_lines(d)
        self.assertIn("diagnosis: model_call_failed", out)
        self.assertIn("stage: binding", out)
        self.assertIn("evidence: diagnostics/journal.jsonl", out)
        self.assertNotIn("（无", out)

    def test_running_render_carries_the_no_evidence_phrase(self) -> None:
        d = SimpleNamespace(
            klass="running", stage="run pump process — still active",
            evidence=(), detail="generation 1 is still running",
        )
        out = render.diagnosis_lines(d)
        self.assertIn("diagnosis: running", out)
        self.assertIn("（无——运行仍在进行）", out)

    def test_diagnose_classifies_and_leaves_the_bundle_byte_identical(self) -> None:
        import contextlib
        import hashlib
        import os
        from io import StringIO

        from deerflow_deep_research.domain.state_machine import rule_run_terminal
        from deerflow_deep_research.runtime.bundle.journal import append_entry
        from deerflow_deep_research.runtime.interaction import cli

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = bundle_actions.start(
                root, problem_text="诊断对象", composition="fixture", deerflow_pin=_PIN
            )
            handle = bundle_state.BundleHandle.open(
                next(
                    bucket / state.thread_id
                    for bucket in sorted(root.iterdir())
                    if (bucket / state.thread_id).is_dir()
                )
            )
            # Drive an honest cancelled terminal: request first (the domain rule
            # refuses cancellation without one), then the terminal rule + entry.
            from dataclasses import replace as dc_replace

            fresh = bundle_state.read_state(handle)
            bundle_state.write_state(handle, fresh, dc_replace(fresh, cancel_requested=True))
            fresh = bundle_state.read_state(handle)
            bundle_state.write_state(handle, fresh, rule_run_terminal(fresh, "cancelled"))
            append_entry(handle, _entry("terminal", "run_cancelled", {"generation": 1}))

            def tree_hashes() -> dict:
                hashes = {}
                for path in sorted(handle.root.rglob("*")):
                    if path.is_file():
                        hashes[str(path.relative_to(handle.root))] = hashlib.sha256(
                            path.read_bytes()
                        ).hexdigest()
                return hashes

            before = tree_hashes()
            with patch.dict(os.environ, {"DEEP_RESEARCH_RUNS_ROOT": str(root)}):
                out = StringIO()
                with contextlib.redirect_stdout(out):
                    cli.cmd_diagnose(SimpleNamespace(bundle_id=state.thread_id))
            printed = out.getvalue()
            self.assertEqual(tree_hashes(), before, "diagnose must not mutate any bundle artifact")
            self.assertIn("diagnosis: cancelled", printed)
            self.assertIn("stage: operator decision", printed)

    def test_diagnose_reports_a_live_run_without_classification(self) -> None:
        import contextlib
        import os
        from io import StringIO

        from deerflow_deep_research.runtime.interaction import cli

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = bundle_actions.start(
                root, problem_text="活跑", composition="fixture", deerflow_pin=_PIN
            )
            with patch.dict(os.environ, {"DEEP_RESEARCH_RUNS_ROOT": str(root)}):
                out = StringIO()
                with contextlib.redirect_stdout(out):
                    cli.cmd_diagnose(SimpleNamespace(bundle_id=state.thread_id))
            self.assertIn("diagnosis: running", out.getvalue())


if __name__ == "__main__":
    unittest.main()
