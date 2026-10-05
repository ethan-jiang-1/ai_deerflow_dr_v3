"""SearchLog: every web_search/web_fetch result becomes a readable file.

The recorder is the persistence-cluster fact owner for the round-4 ruling:
materialization is the readable projection of data the checkpoint already
holds — process diagnostics under diagnostics/searches/, never admission
evidence.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from deerflow_deep_research.runtime.bundle import search_log
from deerflow_deep_research.runtime.bundle.bundle_state import BundleHandle


def _handle(root: Path) -> BundleHandle:
    (root / "request").mkdir(parents=True)
    (root / "state.json").write_text("{}", encoding="utf-8")
    return BundleHandle.open(root)


class SearchLogTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "bundle"
        self.handle = _handle(self.root)
        self.log = search_log.SearchLog(self.handle, generation=1)

    def _note_search(self, call_id: str = "call-s1", query: str = "无人机 认证壁垒") -> None:
        self.log.note_call(call_id, "web_search", {"query": query})
        self.log.note_result(call_id, "[fixture] Canned search results for: " + query)

    def test_search_result_materializes_with_query_and_content(self) -> None:
        self._note_search()
        path = self.root / "diagnostics" / "searches" / "gen1-001-web_search.json"
        self.assertTrue(path.is_file(), "the search file must exist")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["generation"], 1)
        self.assertEqual(payload["seq"], 1)
        self.assertEqual(payload["tool"], "web_search")
        self.assertEqual(payload["arguments"], {"query": "无人机 认证壁垒"})
        self.assertIn("Canned search results", payload["content"])
        self.assertIn("recorded_at", payload)
        self.assertEqual(payload["call_id"], "call-s1")

    def test_duplicate_call_id_writes_once(self) -> None:
        self._note_search()
        self._note_search()  # same call_id again (values-snapshot repeat)
        files = sorted((self.root / "diagnostics" / "searches").glob("*.json"))
        self.assertEqual(len(files), 1, "call-id dedupe must prevent double writes")

    def test_sequence_increments_per_run(self) -> None:
        self._note_search("call-s1", "第一个问题")
        self._note_search("call-s2", "第二个问题")
        files = sorted((self.root / "diagnostics" / "searches").glob("*.json"))
        self.assertEqual([f.name for f in files], [
            "gen1-001-web_search.json", "gen1-002-web_search.json",
        ])

    def test_non_search_tool_writes_nothing(self) -> None:
        self.log.note_call("c-calc", "calculator", {"expr": "1+1"})
        self.log.note_result("c-calc", "2")
        self.assertFalse((self.root / "diagnostics" / "searches").exists())

    def test_web_fetch_is_materialized(self) -> None:
        self.log.note_call("call-f1", "web_fetch", {"url": "https://example.invalid/x"})
        self.log.note_result("call-f1", "page text")
        path = self.root / "diagnostics" / "searches" / "gen1-001-web_fetch.json"
        self.assertTrue(path.is_file())
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["arguments"], {"url": "https://example.invalid/x"})

    def test_orphan_result_without_call_writes_nothing(self) -> None:
        self.log.note_result("call-unknown", "some content")
        self.assertFalse((self.root / "diagnostics" / "searches").exists())

    def test_generation_prefix_isolates_runs(self) -> None:
        gen2 = search_log.SearchLog(self.handle, generation=2)
        gen2.note_call("call-g2", "web_search", {"query": "下一代问题"})
        gen2.note_result("call-g2", "结果")
        self.assertTrue((self.root / "diagnostics" / "searches" / "gen2-001-web_search.json").is_file())


if __name__ == "__main__":
    unittest.main()
