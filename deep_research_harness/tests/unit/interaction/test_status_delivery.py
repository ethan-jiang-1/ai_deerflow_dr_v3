"""Status presents the orthogonal delivery fact on one composed line."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from deerflow_deep_research.runtime.interaction import cli


def _state(delivery, artifact=None):
    return SimpleNamespace(
        status="completed", generation=1, revision=3, thread_id="t",
        owner_pid=99, composition="fixture", delivery=delivery,
        delivery_artifact=artifact,
    )


class StatusDeliveryLineTest(unittest.TestCase):
    def _print_status(self, state) -> str:
        fake_entrypoint = SimpleNamespace(
            SCOPES_ROOT=Path("/scopes"),
            resolve_bundle=lambda scopes, bid: "HANDLE",
        )
        out = io.StringIO()
        with (
            mock.patch.object(cli, "entrypoint", fake_entrypoint),
            mock.patch.object(cli.bundle_actions, "status", return_value=state),
            mock.patch(
                "deerflow_deep_research.runtime.bundle.journal.read_entries",
                return_value=[],
            ),
            redirect_stdout(out),
        ):
            cli.cmd_status(SimpleNamespace(bundle_id="b1"))
        return out.getvalue()

    def test_admitted_line_names_the_artifact(self) -> None:
        text = self._print_status(_state("admitted", "final/report-gen1.md"))
        self.assertIn("delivery: admitted (final/report-gen1.md)", text)

    def test_rejected_and_no_answer_lines(self) -> None:
        self.assertIn("delivery: rejected", self._print_status(_state("rejected")))
        self.assertIn("delivery: no-answer", self._print_status(_state("no-answer")))

    def test_not_recorded_line(self) -> None:
        self.assertIn("delivery: (not recorded)", self._print_status(_state(None)))


if __name__ == "__main__":
    unittest.main()
