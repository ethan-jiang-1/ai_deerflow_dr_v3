"""Journaling mixin tests: every _generate pair lands in the sink, replay round-trips.

The mixin is applied to the harness's own ScriptedChatModel — no framework import,
no API. The composed real-model provider (recording_deepseek.py) is exercised only
by an actual record run (E-2). Scripts load through DEERFLOW_FAKE_SCRIPT, the
documented scripted-model mechanism.

@impl DEW-001"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from deerflow_deep_research.runtime.recording import JournalingMixin
from deerflow_deep_research.runtime.scripted import ScriptedChatModel
from deerflow_deep_research.runtime.scripted.replay_model import ReplayChatModel, replay_key
from langchain_core.messages import HumanMessage


class _JournaledScripted(JournalingMixin, ScriptedChatModel):
    """The mixin over the harness fake — the unit-lane composition."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN401
        ScriptedChatModel.__init__(self, **kwargs)
        self._init_journal(pin="test-pin")


class _EnvScript:
    """Set both env knobs for a test; restore on exit."""

    def __init__(self, script: list[dict], sink: Path) -> None:
        self._script = json.dumps(script, ensure_ascii=False)
        self._sink = str(sink)

    def __enter__(self) -> None:
        os.environ["DEERFLOW_FAKE_SCRIPT"] = self._script
        os.environ["DEERFLOW_RECORD_SINK"] = self._sink

    def __exit__(self, *exc) -> None:  # noqa: ANN002
        os.environ.pop("DEERFLOW_FAKE_SCRIPT", None)
        os.environ.pop("DEERFLOW_RECORD_SINK", None)


class JournalingMixinTest(unittest.TestCase):
    def test_unset_sink_fails_loudly(self) -> None:
        saved = os.environ.pop("DEERFLOW_RECORD_SINK", None)
        try:

            class _Broken(JournalingMixin, ScriptedChatModel):
                def __init__(self) -> None:
                    ScriptedChatModel.__init__(self)
                    self._init_journal()

            with self.assertRaises(RuntimeError) as ctx:
                _Broken()
            self.assertIn("DEERFLOW_RECORD_SINK", str(ctx.exception))
        finally:
            if saved is not None:
                os.environ["DEERFLOW_RECORD_SINK"] = saved

    def test_content_turn_journals_key_output_pair(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            with _EnvScript([{"content": "记录的回答"}], sink):
                model = _JournaledScripted()
                result = model._generate([HumanMessage(content="问题")])
                self.assertEqual(result.generations[0].message.content, "记录的回答")
                lines = [json.loads(l) for l in sink.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(len(lines), 1)
                self.assertEqual(lines[0]["key"], replay_key([HumanMessage(content="问题")]))
                self.assertEqual(lines[0]["output"], "记录的回答")
                self.assertNotIn("tool_calls", lines[0])

    def test_tool_call_turn_journals_calls_whole(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            script = [
                {
                    "content": "",
                    "tool_calls": [
                        {"name": "web_search", "args": {"query": "EASA UAS"}, "id": "call_1"}
                    ],
                }
            ]
            with _EnvScript(script, sink):
                model = _JournaledScripted()
                result = model._generate([HumanMessage(content="开始调研")])
                message = result.generations[0].message
                self.assertTrue(message.tool_calls, "scripted turn must emit tool calls")
                lines = [json.loads(l) for l in sink.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(len(lines), 1)
                self.assertEqual(
                    lines[0]["tool_calls"],
                    [{"name": "web_search", "args": {"query": "EASA UAS"}, "id": "call_1"}],
                )

    def test_sidecar_records_provenance_once(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            with _EnvScript([{"content": "a"}], sink):
                _JournaledScripted()
                _JournaledScripted()
                sidecar = Path(str(sink) + ".meta.json")
                self.assertTrue(sidecar.is_file())
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
                self.assertEqual(meta["deerflow_pin"], "test-pin")
                self.assertIn("recorded_at", meta)
                self.assertIn("JournaledScripted", meta["model"])
                self.assertIn("usage/token", meta["deliberate_limits"][0])


class ReplayRoundTripTest(unittest.TestCase):
    def test_content_journal_replays_through_the_mechanism(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            with _EnvScript([{"content": "答案"}], sink):
                _JournaledScripted()._generate([HumanMessage(content="问")])
            replay = ReplayChatModel(sink=sink)
            served = replay._generate([HumanMessage(content="问")])
            self.assertEqual(served.generations[0].message.content, "答案")

    def test_tool_call_journal_replays_the_tool_turn(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            script = [
                {
                    "content": "",
                    "tool_calls": [
                        {"name": "web_search", "args": {"query": "EASA UAS"}, "id": "call_1"}
                    ],
                }
            ]
            with _EnvScript(script, sink):
                _JournaledScripted()._generate([HumanMessage(content="开始调研")])
            replay = ReplayChatModel(sink=sink)
            served = replay._generate([HumanMessage(content="开始调研")])
            message = served.generations[0].message
            self.assertEqual(message.content, "")
            self.assertEqual(len(message.tool_calls), 1)
            call = message.tool_calls[0]
            self.assertEqual(call["name"], "web_search")
            self.assertEqual(call["args"], {"query": "EASA UAS"})
            self.assertEqual(call["id"], "call_1")

    def test_legacy_line_without_tool_calls_replays_content_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "legacy.jsonl"
            key = replay_key([HumanMessage(content="旧问题")])
            sink.write_text(
                json.dumps({"key": key, "output": "旧答案"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            replay = ReplayChatModel(sink=sink)
            served = replay._generate([HumanMessage(content="旧问题")])
            message = served.generations[0].message
            self.assertEqual(message.content, "旧答案")
            self.assertEqual(message.tool_calls, [])


if __name__ == "__main__":
    unittest.main()
