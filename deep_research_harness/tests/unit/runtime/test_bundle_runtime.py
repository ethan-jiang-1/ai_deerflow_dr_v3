"""Run-bundle runtime tests: staging publish, CAS state store, lease, journal, actions.

@impl RUB-001"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from deerflow_deep_research.domain import bundle, journal_policy, state_machine
from deerflow_deep_research.domain.state_machine import RuleViolation
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state
from deerflow_deep_research.runtime.bundle import journal as journal_mod

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_FIXED_BUCKET = "d_20261003"


class StartPublishTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"

    def _start(self, **overrides) -> tuple[state_machine.BundleState, bundle_state.BundleHandle]:
        kwargs: dict = {
            "problem_text": "研究 A 国无人机供应链的认证壁垒",
            "composition": "all_real",
            "deerflow_pin": _PIN,
            "now": _FIXED_NOW,
        }
        kwargs.update(overrides)
        state = bundle_actions.start(self.runs, **kwargs)
        root = self.runs / _FIXED_BUCKET / state.thread_id
        return state, bundle_state.BundleHandle.open(root)

    def test_start_materializes_exactly_the_declared_contract(self) -> None:
        state, handle = self._start()
        names = sorted(child.name for child in handle.root.iterdir())
        self.assertEqual(names, sorted([*bundle.BUNDLE_SUBTREES, bundle.STATE_FILENAME]))
        for forbidden in ("synthesis", "review"):
            self.assertNotIn(forbidden, names)
        problem = (handle.root / bundle.request_problem_relative()).read_text(encoding="utf-8")
        self.assertIn("无人机供应链", problem)
        self.assertEqual(state.status, "active")
        self.assertEqual(state.generation, 1)
        self.assertEqual(state.revision, 1)
        self.assertEqual(state.composition, "all_real")
        self.assertEqual(state.owner_pid, os.getpid())

    def test_start_rejects_illegal_composition_and_creates_nothing(self) -> None:
        with self.assertRaises(RuleViolation) as ctx:
            self._start(composition="half_real")
        self.assertIn("half_real", str(ctx.exception))
        self.assertFalse(self.runs.exists() and any(self.runs.iterdir()))

    def test_start_fails_loud_on_bundle_collision(self) -> None:
        fixed_id = "0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b"
        _, handle = self._start(bundle_id=fixed_id)
        with self.assertRaises(RuleViolation) as ctx:
            self._start(bundle_id=fixed_id)
        self.assertIn("collision", str(ctx.exception).lower())
        self.assertEqual(bundle_state.read_state(handle).status, "active")


class StateStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"
        state = bundle_actions.start(
            self.runs, problem_text="p", composition="all_real", deerflow_pin=_PIN, now=_FIXED_NOW
        )
        self.handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / state.thread_id)

    def test_conflicting_write_is_rejected_naming_revisions(self) -> None:
        writer_a = bundle_state.read_state(self.handle)
        writer_b = bundle_state.read_state(self.handle)
        written = bundle_state.write_state(self.handle, writer_b, writer_b)
        self.assertEqual(written.revision, 2)
        with self.assertRaises(bundle_state.StateRevisionConflict) as ctx:
            bundle_state.write_state(self.handle, writer_a, writer_a)
        self.assertIn("expected 1", str(ctx.exception))
        self.assertIn("actual 2", str(ctx.exception))

    def test_lease_mismatch_rejects_the_write(self) -> None:
        state = bundle_state.read_state(self.handle)
        # Simulate the directory being replaced under the writer: the handle's captured
        # identity no longer matches the live directory.
        self.handle.identity = (self.handle.identity[0] + 1, self.handle.identity[1] + 1)
        with self.assertRaises(bundle_state.LeaseViolation) as ctx:
            bundle_state.write_state(self.handle, state, state)
        self.assertIn("lease", str(ctx.exception).lower())

    def test_deleted_bundle_reports_permanent_unavailability(self) -> None:
        import shutil

        root = self.handle.root
        shutil.rmtree(root)
        with self.assertRaises(bundle_state.BundleUnavailable) as ctx:
            bundle_state.BundleHandle.open(root)
        self.assertIn("permanently unavailable", str(ctx.exception))


class CrashTransferTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"

    def _start(self, **overrides) -> tuple[state_machine.BundleState, bundle_state.BundleHandle]:
        kwargs: dict = {
            "problem_text": "p",
            "composition": "all_real",
            "deerflow_pin": _PIN,
            "now": _FIXED_NOW,
        }
        kwargs.update(overrides)
        state = bundle_actions.start(self.runs, **kwargs)
        handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / state.thread_id)
        return state, handle

    def test_dead_owner_transfers_to_failed_resume_with_terminal_entry(self) -> None:
        child = subprocess.Popen(["true"])
        child.wait()  # the PID exists no more
        state, handle = self._start(owner_pid=child.pid)
        result = bundle_actions.status(handle)
        self.assertEqual(result.status, "failed-resume")
        entries = journal_mod.read_entries(handle)
        self.assertTrue(any(e.category == "terminal" and e.event == "crash_detected" for e in entries))
        self.assertEqual(state.status, "active")  # the pre-observation snapshot is untouched

    def test_live_owner_keeps_active(self) -> None:
        _, handle = self._start()
        result = bundle_actions.status(handle, liveness=lambda pid: True)
        self.assertEqual(result.status, "active")
        entries = journal_mod.read_entries(handle)
        self.assertFalse(any(e.category == "terminal" for e in entries))


class JournalTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"
        state = bundle_actions.start(
            self.runs, problem_text="p", composition="all_real", deerflow_pin=_PIN, now=_FIXED_NOW
        )
        self.handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / state.thread_id)

    def _entry(self, index: int, category: str = "model_tool") -> journal_policy.JournalEntry:
        return journal_policy.JournalEntry(
            timestamp=f"2026-10-03T00:00:{index:02d}Z",
            category=category,
            event=f"event-{index}",
            detail={},
        )

    def test_append_read_roundtrip_and_closed_categories(self) -> None:
        journal_mod.append_entry(self.handle, self._entry(1))
        journal_mod.append_entry(self.handle, self._entry(2, category="admission"))
        entries = journal_mod.read_entries(self.handle)
        self.assertEqual([e.event for e in entries], ["event-1", "event-2"])
        with self.assertRaises(RuleViolation):
            journal_mod.append_entry(self.handle, self._entry(3, category="gossip"))

    def test_retention_never_evicts_anchors(self) -> None:
        with (
            mock.patch.object(journal_mod, "JOURNAL_BOUND", 10),
            mock.patch.object(journal_mod, "COMPACTION_THRESHOLD", 8),
            mock.patch.object(journal_mod, "COMPACTION_TAIL", 4),
        ):
            for i in range(30):
                category = "admission" if i % 10 == 0 else "model_tool"
                journal_mod.append_entry(self.handle, self._entry(i, category=category))
        entries = journal_mod.read_entries(self.handle)
        self.assertLessEqual(len(entries), 10)
        self.assertEqual(sum(1 for e in entries if e.category == "admission"), 3)
        self.assertEqual(entries[-1].event, "event-29")

    def test_corrupted_tail_fails_loudly(self) -> None:
        journal_mod.append_entry(self.handle, self._entry(1))
        journal_path = self.handle.root / bundle.journal_relative()
        with journal_path.open("a", encoding="utf-8") as fh:
            fh.write('{"ts": "2026-10-03T00:00:99Z", "category": "model_tool"\n')
        with self.assertRaises(journal_mod.JournalCorruption) as ctx:
            journal_mod.read_entries(self.handle)
        self.assertIn("line 2", str(ctx.exception))


class RefineAndCancelTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"
        self.state = bundle_actions.start(
            self.runs, problem_text="p", composition="all_real", deerflow_pin=_PIN, now=_FIXED_NOW
        )
        self.handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / self.state.thread_id)

    def test_cancel_records_the_request(self) -> None:
        result = bundle_actions.cancel(self.handle)
        self.assertTrue(result.cancel_requested)
        self.assertEqual(result.status, "active")
        entries = journal_mod.read_entries(self.handle)
        self.assertTrue(any(e.category == "lifecycle" and e.event == "cancellation_requested" for e in entries))

    def test_refine_writes_direction_and_bumps_generation(self) -> None:
        done = state_machine.rule_run_terminal(self.state, "completed")
        bundle_state.write_state(self.handle, self.state, done)
        refined, record = bundle_actions.refine(self.handle, "深挖成本侧证据")
        self.assertEqual(refined.status, "active")
        self.assertEqual(refined.generation, 2)
        self.assertEqual(record.generation, 2)
        request_file = self.handle.root / "request" / "refine-2.txt"
        self.assertEqual(request_file.read_text(encoding="utf-8"), "深挖成本侧证据")
        entries = journal_mod.read_entries(self.handle)
        self.assertTrue(any(e.category == "lifecycle" and e.event == "refined" for e in entries))


    def test_fresh_context_refine_seeds_and_migrates(self) -> None:
        done = state_machine.rule_run_terminal(self.state, "completed")
        bundle_state.write_state(self.handle, self.state, done)
        old_thread = self.state.thread_id
        refined, record = bundle_actions.refine(self.handle, "直接写简报", fresh_context="先前材料摘要：3 份文件")
        self.assertNotEqual(refined.thread_id, old_thread)
        self.assertEqual(refined.prior_thread_ids, (old_thread,))
        seed = self.handle.root / "request" / f"generation-{record.generation}-context.md"
        self.assertTrue(seed.is_file())
        self.assertIn("先前材料摘要", seed.read_text(encoding="utf-8"))


    def test_refine_takes_calling_process_as_owner(self) -> None:
        state = bundle_actions.start(
            self.runs, problem_text="p", composition="all_real", deerflow_pin=_PIN,
            owner_pid=12345, now=_FIXED_NOW,  # a dead create-process pid
        )
        handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / state.thread_id)
        done = state_machine.rule_run_terminal(state, "completed")
        bundle_state.write_state(handle, state, done)
        refined, _record = bundle_actions.refine(handle, "深挖成本侧证据")
        self.assertEqual(refined.owner_pid, os.getpid(),
                         "the refined generation's owner must be the calling process, "
                         "not the inherited dead pid of the create process")


if __name__ == "__main__":
    unittest.main()
