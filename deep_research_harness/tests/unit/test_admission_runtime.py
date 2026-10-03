"""Run-admission runtime tests: hash-chain ledger, hold point, dispositions, journal.

@impl RUA-001"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from deerflow_deep_research.domain import bundle
from deerflow_deep_research.engine import verdicts
from deerflow_deep_research.engine.validator import AdmissionContext, ArtifactSubmission
from deerflow_deep_research.domain.state_machine import RuleViolation
from deerflow_deep_research.runtime import bundle_actions, bundle_state
from deerflow_deep_research.runtime import admission as admission_mod
from deerflow_deep_research.runtime import journal as journal_mod
from deerflow_deep_research.runtime.ledger import LedgerEntry, commit_entry, read_ledger

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
_FIXED_BUCKET = "d_20261003"


def _submission(**overrides) -> ArtifactSubmission:
    kwargs: dict = {
        "kind": "evidence",
        "filename": "supply-chain-notes.md",
        "content": "认证壁垒调研笔记".encode("utf-8"),
        "provenance": {"producer": "research-skill"},
    }
    kwargs.update(overrides)
    return ArtifactSubmission(**kwargs)


class AdmissionRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.scopes = Path(self._tmp.name) / "scopes"
        self.state = bundle_actions.start(
            self.scopes, problem_text="p", composition="all_real", deerflow_pin=_PIN, now=_FIXED_NOW
        )
        self.handle = bundle_state.BundleHandle.open(self.scopes / _FIXED_BUCKET / self.state.thread_id)

    def _ledger_path(self) -> Path:
        return self.handle.root / "evidence" / "submissions.jsonl"

    def test_submit_admits_and_places_content(self) -> None:
        entry = admission_mod.submit_artifact(self.handle, _submission())
        self.assertEqual(entry.disposition, "admit")
        self.assertEqual(entry.seq, 1)
        placed = self.handle.root / "evidence" / "evidence" / "supply-chain-notes.md"
        self.assertTrue(placed.is_file())
        self.assertEqual(entry.artifact_path, "evidence/evidence/supply-chain-notes.md")
        entries = read_ledger(self.handle)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].content_hash, entry.content_hash)

    def test_chain_survives_roundtrip_and_grows_monotonically(self) -> None:
        first = admission_mod.submit_artifact(self.handle, _submission(filename="a.md"))
        second = admission_mod.submit_artifact(self.handle, _submission(filename="b.md", content="第二条".encode()))
        self.assertEqual((first.seq, second.seq), (1, 2))
        self.assertNotEqual(first.entry_hash, second.entry_hash)
        entries = read_ledger(self.handle)
        self.assertEqual([e.seq for e in entries], [1, 2])

    def test_tampered_field_fails_naming_sequence(self) -> None:
        admission_mod.submit_artifact(self.handle, _submission())
        admission_mod.submit_artifact(self.handle, _submission(filename="b.md", content="第二条".encode()))
        lines = self._ledger_path().read_text(encoding="utf-8").splitlines()
        tampered = json.loads(lines[1])
        tampered["disposition"] = "reject"  # edit a recorded field after the fact
        lines[1] = json.dumps(tampered, ensure_ascii=False)
        self._ledger_path().write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(admission_mod.LedgerTampered) as ctx:
            read_ledger(self.handle)
        self.assertIn("seq 2", str(ctx.exception))

    def test_inserted_entry_breaks_linkage(self) -> None:
        admission_mod.submit_artifact(self.handle, _submission())
        forged = dict(json.loads(self._ledger_path().read_text(encoding="utf-8").splitlines()[0]))
        forged["seq"] = 2
        forged["prev_hash"] = "f" * 64
        with self._ledger_path().open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(forged, ensure_ascii=False) + "\n")
        with self.assertRaises(admission_mod.LedgerTampered):
            read_ledger(self.handle)

    def test_reject_places_nothing_but_records(self) -> None:
        entry = admission_mod.submit_artifact(self.handle, _submission(provenance={}))
        self.assertEqual(entry.disposition, "reject")
        self.assertEqual(entry.result_code, "missing_provenance")
        self.assertEqual(entry.artifact_path, "")
        evidence_tree = self.handle.root / "evidence"
        placed = [p for p in evidence_tree.rglob("*") if p.is_file() and p.name != "submissions.jsonl"]
        self.assertEqual(placed, [], "a rejected submission must place no content")
        entries = read_ledger(self.handle)
        self.assertTrue(any("producer" in reason for reason in entries[0].reasons))

    def test_duplicate_content_is_rejected(self) -> None:
        admission_mod.submit_artifact(self.handle, _submission())
        entry = admission_mod.submit_artifact(self.handle, _submission(filename="again.md"))
        self.assertEqual(entry.disposition, "reject")
        self.assertEqual(entry.result_code, "duplicate_content")

    def test_replay_of_reworked_content_records_reference(self) -> None:
        rejected = admission_mod.submit_artifact(self.handle, _submission(provenance={}))
        self.assertEqual(rejected.disposition, "reject")
        # Rework: same content, now with provenance — hash matches the rejected entry.
        reworked = _submission(provenance={"producer": "research-skill"})
        self.assertEqual(reworked.content, _submission().content)
        replayed = admission_mod.submit_artifact(self.handle, reworked)
        self.assertEqual(replayed.disposition, "replay")
        self.assertEqual(replayed.replay_of, rejected.seq)
        placed = self.handle.root / "evidence" / "evidence" / "supply-chain-notes.md"
        self.assertTrue(placed.is_file())

    def test_illegal_disposition_is_rejected_loudly(self) -> None:
        ok_verdict = verdicts.ValidatorVerdict(result_code="ok", reasons=(), content_hash="a" * 64)
        with self.assertRaises(RuleViolation):
            commit_entry(
                self.handle,
                LedgerEntry(
                    seq=1,
                    timestamp="2026-10-03T12:00:00+00:00",
                    disposition="pardon",
                    kind="evidence",
                    filename="x.md",
                    artifact_path="",
                    content_hash="a" * 64,
                    result_code="ok",
                    reasons=(),
                    replay_of=None,
                    prev_hash="0" * 64,
                    entry_hash="",
                ),
                verdict=ok_verdict,
            )

    def test_verdict_less_commit_is_refused(self) -> None:
        with self.assertRaises(admission_mod.VerdictlessCommit):
            commit_entry(
                self.handle,
                LedgerEntry(
                    seq=1,
                    timestamp="2026-10-03T12:00:00+00:00",
                    disposition="admit",
                    kind="evidence",
                    filename="x.md",
                    artifact_path="evidence/evidence/x.md",
                    content_hash="a" * 64,
                    result_code="ok",
                    reasons=(),
                    replay_of=None,
                    prev_hash="0" * 64,
                    entry_hash="",
                ),
                verdict=None,
            )

    def test_verdict_contradicting_commit_is_refused(self) -> None:
        bad_verdict = verdicts.ValidatorVerdict(result_code="empty_content", reasons=("x",), content_hash="")
        with self.assertRaises(admission_mod.VerdictContradiction):
            commit_entry(
                self.handle,
                LedgerEntry(
                    seq=1,
                    timestamp="2026-10-03T12:00:00+00:00",
                    disposition="admit",
                    kind="evidence",
                    filename="x.md",
                    artifact_path="evidence/evidence/x.md",
                    content_hash="a" * 64,
                    result_code="ok",
                    reasons=(),
                    replay_of=None,
                    prev_hash="0" * 64,
                    entry_hash="",
                ),
                verdict=bad_verdict,
            )

    def test_validation_journal_entries_accompany_dispositions(self) -> None:
        admission_mod.submit_artifact(self.handle, _submission())
        admission_mod.submit_artifact(self.handle, _submission(provenance={}))
        entries = journal_mod.read_entries(self.handle)
        validation = [e for e in entries if e.category == "validation"]
        self.assertEqual(len(validation), 2)
        self.assertEqual({e.detail.get("disposition") for e in validation}, {"admit", "reject"})

    def test_admitted_counts_feed_the_gate(self) -> None:
        admission_mod.submit_artifact(self.handle, _submission())
        admission_mod.submit_artifact(
            self.handle,
            _submission(filename="report.md", kind="final_report", content="报告".encode()),
        )
        counts = admission_mod.read_admitted_counts(self.handle)
        self.assertEqual(counts, {"evidence": 1, "final_report": 1})


    def test_final_report_places_to_final(self) -> None:
        entry = admission_mod.submit_artifact(
            self.handle,
            _submission(kind="final_report", filename="report-gen1.md", content="# 简报\n内容".encode()),
        )
        self.assertEqual(entry.disposition, "admit")
        placed = self.handle.root / "final" / "report-gen1.md"
        self.assertTrue(placed.is_file())
        self.assertEqual(entry.artifact_path, "final/report-gen1.md")


if __name__ == "__main__":
    unittest.main()
