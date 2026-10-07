"""Refine foreground rerun wiring: cmd_refine drives the create execution chain.

Pins the Phase 5 round-2 ruling: after creating the next generation, refine
drives ``run_foreground`` over that generation's direction document, continuing
the bundle's declared composition ladder; cancel keeps its positive CLI wiring
here (the journey exercises cancel-on-terminal as a negative control instead).
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from deerflow_deep_research.runtime.interaction import cli


def _fake_refined(composition: str = "all_real", generation: int = 2):
    return SimpleNamespace(
        status="active", generation=generation, thread_id="t-refined",
        composition=composition, revision=7,
    )


class RefineForegroundWiringTest(unittest.TestCase):
    def test_cmd_refine_drives_run_foreground_with_generation_and_ladder(self) -> None:
        calls: list[dict] = []
        refined = _fake_refined("all_real")
        record = SimpleNamespace(generation=2, direction_text="深挖成本侧证据")

        fake_assembly = SimpleNamespace(
            runs_root=lambda: Path("/runs"), CONFIG_ROOT=Path("/config"),
            resolve_bundle=lambda runs, bid: "HANDLE",
            read_pin=lambda: "p" * 40,
            config_name_for_composition=lambda c: {"fixture": "fixture", "all_real": "base"}[c],
            run_foreground=lambda handle, **kw: calls.append({"handle": handle, **kw})
            or SimpleNamespace(status="completed", generation=2, revision=8),
        )
        args = SimpleNamespace(bundle_id="b1", direction="深挖成本侧证据")
        out = io.StringIO()
        with (
            mock.patch.object(cli, "assembly", fake_assembly),
            mock.patch.object(cli.bundle_actions, "refine", return_value=(refined, record)),
            redirect_stdout(out),
        ):
            cli.cmd_refine(args)

        self.assertEqual(len(calls), 1, "cmd_refine must drive the foreground chain once")
        self.assertEqual(calls[0]["handle"], "HANDLE")
        self.assertEqual(calls[0]["config_name"], "base", "all_real composition continues on the base ladder")
        self.assertEqual(calls[0]["thread_id"], "t-refined")
        self.assertIn("run completed", out.getvalue())
        self.assertIn("state: completed", out.getvalue())

    def test_cmd_refine_maps_fixture_composition_to_fixture_ladder(self) -> None:
        calls: list[dict] = []
        refined = _fake_refined("fixture")
        record = SimpleNamespace(generation=2, direction_text="d")

        fake_assembly = SimpleNamespace(
            runs_root=lambda: Path("/runs"), CONFIG_ROOT=Path("/config"),
            resolve_bundle=lambda runs, bid: "HANDLE",
            read_pin=lambda: "p" * 40,
            config_name_for_composition=lambda c: {"fixture": "fixture", "all_real": "base"}[c],
            run_foreground=lambda handle, **kw: calls.append({"handle": handle, **kw})
            or SimpleNamespace(status="completed", generation=2, revision=8),
        )
        args = SimpleNamespace(bundle_id="b1", direction="d")
        with (
            mock.patch.object(cli, "assembly", fake_assembly),
            mock.patch.object(cli.bundle_actions, "refine", return_value=(refined, record)),
            redirect_stdout(io.StringIO()),
        ):
            cli.cmd_refine(args)

        self.assertEqual(calls[0]["config_name"], "fixture")


class CompositionLadderMappingTest(unittest.TestCase):
    def test_composition_maps_to_config_name(self) -> None:
        from deerflow_deep_research.runtime.assembly import config_name_for_composition

        self.assertEqual(config_name_for_composition("fixture"), "fixture")
        self.assertEqual(config_name_for_composition("all_real"), "base")

    def test_unwired_composition_fails_loudly(self) -> None:
        from deerflow_deep_research.runtime.assembly import config_name_for_composition

        for composition in ("mixed", "bogus"):
            with self.subTest(composition=composition):
                with self.assertRaises(ValueError) as ctx:
                    config_name_for_composition(composition)
                self.assertIn(composition, str(ctx.exception))


class CancelPositiveWiringTest(unittest.TestCase):
    """The journey now exercises cancel-on-terminal as a negative control, so the
    positive CLI wiring (active bundle → request recorded) is pinned here."""

    def test_cmd_cancel_records_request(self) -> None:
        cancelled = SimpleNamespace(status="active", generation=1, revision=2)
        fake_assembly = SimpleNamespace(
            runs_root=lambda: Path("/runs"),
            resolve_bundle=lambda runs, bid: "HANDLE",
        )
        args = SimpleNamespace(bundle_id="b1")
        out = io.StringIO()
        with (
            mock.patch.object(cli, "assembly", fake_assembly),
            mock.patch.object(cli.bundle_actions, "cancel", return_value=cancelled) as cancel,
            redirect_stdout(out),
        ):
            cli.cmd_cancel(args)

        cancel.assert_called_once_with("HANDLE")
        self.assertIn("cancellation requested", out.getvalue())


if __name__ == "__main__":
    unittest.main()
