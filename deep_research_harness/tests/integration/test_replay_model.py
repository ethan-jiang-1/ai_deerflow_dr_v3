"""Level-2 stand-in tests: content-addressed recording/replay at the LLM boundary.

@impl DEW-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from deerflow_deep_research.runtime.scripted.replay_model import (
    ReplayChatModel,
    RecordingChatModel,
    replay_key,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def _messages(with_volatile: bool = False) -> list:
    msgs = [HumanMessage(content="研究 EASA 无人机要求")]
    if with_volatile:
        msgs.insert(0, SystemMessage(content="当前日期 2026-10-04，trace abc-123"))
    return msgs


class NormalizationTest(unittest.TestCase):
    def test_volatile_content_is_stripped(self) -> None:
        a = replay_key(_messages(with_volatile=True))
        b = replay_key(_messages(with_volatile=False))
        self.assertEqual(a, b, "volatile substrings must not change the key")

    def test_different_inputs_differ(self) -> None:
        self.assertNotEqual(replay_key(_messages()), replay_key(
            [HumanMessage(content="另一个问题")]))


class RecordReplayTest(unittest.TestCase):
    def test_record_then_replay_serves_the_recorded_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "io.jsonl"
            recorder = RecordingChatModel(sink=sink, script=[
                {"content": "录制的回答"}
            ])
            result = recorder._generate([HumanMessage(content="q")])
            self.assertEqual(result.generations[0].message.content, "录制的回答")
            replay = ReplayChatModel(sink=sink)
            served = replay._generate([HumanMessage(content="q")])
            self.assertEqual(served.generations[0].message.content, "录制的回答")

    def test_miss_fails_loudly_with_known_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "io.jsonl"
            recorder = RecordingChatModel(sink=sink, script=[
                {"content": "录制的回答"}
            ])
            recorder._generate([HumanMessage(content="q")])
            replay = ReplayChatModel(sink=sink)
            with self.assertRaises(KeyError) as ctx:
                replay._generate([HumanMessage(content="没录过的问题")])
            self.assertIn("known", str(ctx.exception))
            self.assertIn("Input preview", str(ctx.exception))


class RetainedSampleTest(unittest.TestCase):
    """First test consumer of the retained real-model sample.

    Provenance limits, declared at the point of consumption (test-evidence
    spec): the sample records key/output only — the original input, model id,
    pin, and recording command are unrecorded, so replay-to-output cannot be
    driven and origin realness cannot be verified. The assertions below claim
    only the sample's shape contract and its participation in the replay
    machinery (a different input misses loudly, naming the retained key).
    """

    _SAMPLE = (
        Path(__file__).resolve().parents[1] / "fixtures" / "replay" / "real-model-io.jsonl"
    )

    def _record(self) -> dict:
        line = self._SAMPLE.read_text(encoding="utf-8").splitlines()[0]
        return json.loads(line)

    def test_retained_sample_shape_contract(self) -> None:
        record = self._record()
        self.assertEqual(len(record["key"]), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in record["key"]))
        self.assertTrue(record["output"].strip())

    def test_retained_sample_participates_in_replay_machinery(self) -> None:
        record = self._record()
        with tempfile.TemporaryDirectory() as td:
            sink = Path(td) / "io.jsonl"
            sink.write_text(
                json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            replay = ReplayChatModel(sink=sink)
            with self.assertRaises(KeyError) as ctx:
                replay._generate([HumanMessage(content="未录制的输入")])
            self.assertIn(record["key"], str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
