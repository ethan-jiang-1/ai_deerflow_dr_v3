"""Read-state diagnosis honesty: directory-level absence is not file corruption.

The diagnosis for the gen-7 incident (fixture-level experiments, no LLM) proved the
atomic write path has no missing window and that the observed "state.json is missing"
signature is produced by directory-level invisibility. These tests lock that
distinction in.
"""

from __future__ import annotations

import tempfile
import threading
import unittest
import unittest.mock as um
from datetime import datetime, timezone
from pathlib import Path

from deerflow_deep_research.domain import bundle
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
_FIXED_BUCKET = "d_20261004"


class DiagnosisFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.scopes = Path(self._tmp.name) / "scopes"
        state = bundle_actions.start(
            self.scopes,
            problem_text="诊断问题",
            composition="all_real",
            deerflow_pin=_PIN,
            now=_FIXED_NOW,
        )
        self.root = self.scopes / _FIXED_BUCKET / state.thread_id
        self.handle = bundle_state.BundleHandle.open(self.root)

    def _move_root_away(self) -> None:
        moved = self.root.parent / (self.root.name + ".moved")
        self.root.rename(moved)
        self.addCleanup(moved.rename, self.root)


class DirectoryAbsenceTest(DiagnosisFixtureTest):
    def test_bundle_directory_absent_reports_unavailable(self) -> None:
        """A transiently invisible directory is indistinguishable from deletion."""
        self._move_root_away()
        with self.assertRaises(bundle_state.BundleUnavailable):
            bundle_state.read_state(self.handle)

    def test_file_absent_with_directory_present_reports_corruption_with_evidence(
        self,
    ) -> None:
        (self.root / bundle.state_relative()).unlink()
        with self.assertRaises(bundle_state.StateCorruption) as ctx:
            bundle_state.read_state(self.handle)
        message = str(ctx.exception)
        self.assertIn("phase=stat", message)
        self.assertIn("tmp-siblings", message)


class ReadWindowTest(DiagnosisFixtureTest):
    def test_read_window_directory_absence_is_classified(self) -> None:
        """A directory vanishing between the existence check and the read is
        classified, not escaped as a bare FileNotFoundError."""
        real_read_text = Path.read_text

        def racing_read_text(path_self, *args, **kwargs):
            if self.root.exists():
                self._move_root_away()
            return real_read_text(path_self, *args, **kwargs)

        with um.patch.object(Path, "read_text", racing_read_text):
            with self.assertRaises(bundle_state.BundleUnavailable):
                bundle_state.read_state(self.handle)


class AtomicWriteNegativeControlTest(DiagnosisFixtureTest):
    def test_concurrent_atomic_rewrites_produce_no_missing_shape(self) -> None:
        """The write path has no missing window: readers never observe a missing
        state.json while writers atomically replace it (the experiment that
        overturned the FS-pressure hypothesis, as a regression test)."""
        current = bundle_state.read_state(self.handle)
        missing_shapes: list[str] = []
        stop = threading.Event()

        def writer() -> None:
            local = current
            for _ in range(60):
                if stop.is_set():
                    return
                try:
                    local = bundle_state.write_state(self.handle, local, local)
                except bundle_state.StateRevisionConflict:
                    local = bundle_state.read_state(self.handle)

        def reader() -> None:
            while not stop.is_set():
                try:
                    bundle_state.read_state(self.handle)
                except bundle_state.StateCorruption as exc:
                    if "missing" in str(exc):
                        missing_shapes.append(str(exc))
                except bundle_state.BundleUnavailable:
                    pass  # legal only if the directory is genuinely gone

        threads = [threading.Thread(target=writer) for _ in range(2)]
        threads += [threading.Thread(target=reader) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads[:2]:
            thread.join()
        stop.set()
        for thread in threads[2:]:
            thread.join()
        self.assertEqual(missing_shapes, [])


if __name__ == "__main__":
    unittest.main()
