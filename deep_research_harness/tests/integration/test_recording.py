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

from langchain_core.messages import HumanMessage

from deerflow_deep_research.runtime.recording import JournalingMixin
from deerflow_deep_research.runtime.scripted import ScriptedChatModel
from deerflow_deep_research.runtime.scripted.replay_model import ReplayChatModel, replay_key


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
                lines = [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines()]
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
                lines = [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines()]
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


class AsyncPathTest(unittest.TestCase):
    def test_sync_stream_path_journals_the_assembled_turn(self) -> None:
        """The path the framework actually uses: v2 protocol streaming drives
        the sync ``_stream`` bridge (never _generate/_agenerate/_astream — the
        entry-point spy probe pinned it). A base with native _stream must be
        journaled by the streaming override, chunks untouched."""
        from langchain_core.messages import AIMessageChunk
        from langchain_core.outputs import ChatGenerationChunk

        class _SyncStreamScripted(ScriptedChatModel):
            def _stream(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
                item = self.script[min(self.cursor, len(self.script) - 1)]
                self.cursor += 1
                text = str(item.get("content", ""))
                for piece in (text[:2], text[2:]):
                    yield ChatGenerationChunk(message=AIMessageChunk(content=piece))

        class _JournaledSyncStream(JournalingMixin, _SyncStreamScripted):
            def __init__(self) -> None:
                ScriptedChatModel.__init__(self)
                self._init_journal(pin="sync-stream-pin")

        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            with _EnvScript([{"content": "同步流回答"}], sink):
                model = _JournaledSyncStream()
                pieces = [c.message.content for c in model._stream([HumanMessage(content="同步问")])]
                self.assertEqual("".join(pieces), "同步流回答")
                lines = [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(len(lines), 1, f"expected one line, got {lines}")
                self.assertEqual(lines[0]["output"], "同步流回答")

    def test_streaming_path_journals_the_assembled_turn(self) -> None:
        """The real bypass: OpenAI-family models stream natively via _astream,
        which never touches _generate/_agenerate. A base with its own _astream
        (the real-model shape) must be journaled by the streaming override —
        chunks re-emitted untouched, the merged turn appended once."""
        import asyncio

        from langchain_core.messages import AIMessageChunk
        from langchain_core.outputs import ChatGenerationChunk

        class _StreamingScripted(ScriptedChatModel):
            async def _astream(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
                item = self.script[min(self.cursor, len(self.script) - 1)]
                self.cursor += 1
                text = str(item.get("content", ""))
                for piece in (text[:2], text[2:]):
                    yield ChatGenerationChunk(message=AIMessageChunk(content=piece))

        class _JournaledStream(JournalingMixin, _StreamingScripted):
            def __init__(self) -> None:
                ScriptedChatModel.__init__(self)
                self._init_journal(pin="stream-pin")

        async def _drive() -> list:
            out = []
            with _EnvScript([{"content": "流式回答整段"}], Path(_drive_sink[0])):
                model = _JournaledStream()
                async for chunk in model._astream([HumanMessage(content="流问")]):
                    out.append(chunk.message.content)
            return out

        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            _drive_sink = [str(sink)]
            pieces = asyncio.run(_drive())
            self.assertEqual("".join(pieces), "流式回答整段")
            lines = [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(lines), 1, f"expected one line, got {lines}")
            self.assertEqual(lines[0]["output"], "流式回答整段")

    def test_async_path_journals_exactly_once(self) -> None:
        """The framework drives the graph via astream → _agenerate; with a base
        that has no _agenerate of its own, the default delegates to the sync
        override — the duplicate guard must leave exactly one line."""
        import asyncio

        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            with _EnvScript([{"content": "异步回答"}], sink):
                model = _JournaledScripted()
                result = asyncio.run(model._agenerate([HumanMessage(content="异步问")]))
                self.assertEqual(result.generations[0].message.content, "异步回答")
                lines = [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(len(lines), 1, f"expected one line, got {lines}")
                self.assertEqual(lines[0]["output"], "异步回答")

    def test_async_only_base_journals_from_the_async_override(self) -> None:
        """A base with its own _agenerate (the real-model shape) bypasses the
        sync override entirely; the async override alone must journal."""
        import asyncio

        from langchain_core.messages import AIMessage
        from langchain_core.outputs import ChatGeneration, ChatResult

        class _AsyncScripted(ScriptedChatModel):
            async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
                item = self.script[min(self.cursor, len(self.script) - 1)]
                self.cursor += 1
                return ChatResult(
                    generations=[ChatGeneration(message=AIMessage(content=str(item.get("content", ""))))]
                )

        class _JournaledAsync(JournalingMixin, _AsyncScripted):
            def __init__(self) -> None:
                ScriptedChatModel.__init__(self)
                self._init_journal(pin="async-pin")

        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "model-io.jsonl"
            with _EnvScript([{"content": "纯异步回答"}], sink):
                model = _JournaledAsync()
                result = asyncio.run(model._agenerate([HumanMessage(content="纯异步问")]))
                self.assertEqual(result.generations[0].message.content, "纯异步回答")
                lines = [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(len(lines), 1, f"expected one line, got {lines}")
                self.assertEqual(lines[0]["output"], "纯异步回答")


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
