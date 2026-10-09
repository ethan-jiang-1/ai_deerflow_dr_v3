"""The complete-graph replay: a recorded real journey drives the real graph, zero credentials.

Ladder level 3's missing proof (CLS-017's E item): the recorded model I/O journal
plus the materialized search corpus replay the ENTIRE journey offline — plan turn,
research tool turns, final report, admission — through the real framework assembly
(real graph, real middleware, real checkpointer, real hold point). A key miss or a
corpus miss fails loudly; nothing silently diverges.

The fixture (tests/fixtures/replay/e2-complete-journey/) is extracted verbatim from
the real run bundle 55c35d44 (2026-10-10, post-BUG-001-fix acceptance run); its
provenance sidecar records the model, deerflow pin, and invocation. Machine
desensitization scan: 0 key-pattern hits, 27 public framework-comparison queries,
public-source report (maintainer pre-clearance 2026-10-10; scan recorded in the
change's Delivery Record).

@impl DEW-001"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = HARNESS_ROOT / "tests" / "fixtures" / "replay" / "e2-complete-journey"
PROBLEM = "对比 2025-2026 年主流开源 deep research 框架的能力边界与成熟度"

try:
    from langgraph.checkpoint.sqlite import SqliteSaver  # noqa: F401

    _FRAMEWORK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FRAMEWORK_AVAILABLE = False


@unittest.skipUnless(_FRAMEWORK_AVAILABLE, "deerflow environment required: run `uv sync` in deep_research_harness/")
class CompleteGraphReplayTest(unittest.TestCase):
    def _replay_config_root(self, td: str) -> Path:
        """A test-lane configuration whose seams point at the replay providers.

        Zero credentials structurally: no `$VAR` reference appears anywhere —
        the replay serves everything from the fixture."""
        root = Path(td) / "configs"
        root.mkdir()
        fixture_config = (HARNESS_ROOT / "config" / "fixture.yaml").read_text(encoding="utf-8")
        replay = fixture_config.replace(
            "use: deerflow_deep_research.runtime.scripted:ScriptedChatModel",
            "use: deerflow_deep_research.runtime.replay_fixture:JourneyReplayModel",
        ).replace(
            "use: deerflow_deep_research.runtime.scripted:fake_web_search",
            "use: deerflow_deep_research.runtime.replay_fixture:replay_web_search",
        )
        # web_fetch joins the tool set: the recorded journey used it once
        # (fixture.yaml declares only web_search). Summarization is disabled:
        # its middleware owns a second model instance whose trigger point is
        # context-size-dependent — the framing variance between the recorded
        # and replayed assemblies would interleave its calls differently and
        # misalign the journey order (the provider filters its recorded lines
        # out of the serving queue; see JourneyReplayModel).
        replay = replay.replace(
            "summarization:",
            "  - name: web_fetch\n"
            "    group: web\n"
            "    use: deerflow_deep_research.runtime.replay_fixture:replay_web_fetch\n\n"
            "summarization_disabled_for_replay:\n",
            1,
        )
        self.assertFalse(
            re.search(r"api_key:\s*\$\w+", replay),
            "the replay config must carry no secret reference",
        )
        (root / "record.yaml").write_text(replay, encoding="utf-8")
        return root

    def test_recorded_journey_replays_the_complete_graph_zero_credential(self) -> None:
        import os
        import sys

        sys.path.insert(0, str(HARNESS_ROOT / "src"))
        os.environ["DEERFLOW_REPLAY_ROOT"] = str(FIXTURE_DIR)
        from deerflow_deep_research.runtime import assembly
        from deerflow_deep_research.runtime.adapters import client as hclient
        from deerflow_deep_research.runtime.bundle import bundle_actions

        with tempfile.TemporaryDirectory() as td:
            runs_root = Path(td) / "runs"
            state = bundle_actions.start(
                runs_root, problem_text=PROBLEM, composition="fixture", deerflow_pin="0000000000000000000000000000000000000000"
            )
            handle = assembly.resolve_bundle(runs_root, state.thread_id)
            with hclient.bundle_checkpointer(handle) as saver:
                bc = hclient.build_client(
                    self._replay_config_root(td), "record", checkpointer=saver,
                    model_name="fixture-scripted", available_skills=["deep-research"],
                    snapshot_dir=handle.root / "diagnostics", pin="0000000000000000000000000000000000000000",
                )
                result = assembly.pump.run_research(
                    handle, stream_fn=hclient.make_stream_fn(bc, state.thread_id),
                    on_plan=lambda plan: plan,  # the headless auto-confirm (BUG-001's fix)
                )

            terminal = getattr(getattr(result, "state", result), "status", None)
            self.assertEqual(terminal, "completed", f"replay journey must complete: {terminal}")

            journal = (handle.root / "diagnostics" / "journal.jsonl").read_text(encoding="utf-8")
            self.assertIn("plan_proposed", journal)
            self.assertIn("plan_confirmed", journal)
            self.assertIn("run_completed", journal)
            self.assertIn("disposition_recorded", journal)

            report = (handle.root / "final" / "report-gen1.md").read_text(encoding="utf-8")
            recorded_lines = [
                json.loads(l)
                for l in (FIXTURE_DIR / "model-io.jsonl").read_text(encoding="utf-8").splitlines()
                if l.strip()
            ]
            recorded_report = recorded_lines[-1]["output"]
            self.assertEqual(
                report.strip(), recorded_report.strip(),
                "the replayed final report must be the recorded report, verbatim",
            )
            self.assertNotIn("<research-plan>", report)
            self.assertTrue(
                "Sources" in report or "来源" in report,
                "the replayed report carries a Sources-class section",
            )

            ledger = (handle.root / "evidence" / "submissions.jsonl").read_text(encoding="utf-8")
            self.assertIn('"admit"', ledger, "the replayed report passes the admission hold point")


if __name__ == "__main__":
    unittest.main()
