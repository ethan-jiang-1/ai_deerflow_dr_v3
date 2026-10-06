"""Plan-gate interaction: gating, three-way handler behavior, and create-only wiring.

@impl ENS-001"""

from __future__ import annotations

import builtins
import contextlib
import io
import os
import unittest
from types import SimpleNamespace
from unittest import mock

from deerflow_deep_research.runtime.interaction import cli, render

INTERACTIVE_ENV = "DEEP_RESEARCH_INTERACTIVE"


class PlanGatingTest(unittest.TestCase):
    def test_noninteractive_context_builds_no_plan_handler(self) -> None:
        with (
            mock.patch.object(cli.sys.stdin, "isatty", return_value=False),
            mock.patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop(INTERACTIVE_ENV, None)
            self.assertIsNone(cli._plan_handler())

    def test_tty_builds_a_plan_handler(self) -> None:
        with (
            mock.patch.object(cli.sys.stdin, "isatty", return_value=True),
            mock.patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop(INTERACTIVE_ENV, None)
            self.assertIsNotNone(cli._plan_handler())

    def test_env_override_builds_a_plan_handler_without_a_tty(self) -> None:
        with (
            mock.patch.object(cli.sys.stdin, "isatty", return_value=False),
            mock.patch.dict(os.environ, {INTERACTIVE_ENV: "1"}),
        ):
            self.assertIsNotNone(cli._plan_handler())


class PlanHandlerBehaviorTest(unittest.TestCase):
    def _handler(self) -> object:
        with mock.patch.dict(os.environ, {INTERACTIVE_ENV: "1"}):
            return cli._plan_handler()

    PLAN = "研究计划：\n1. 广度探索\n2. 深挖 A 国法规"

    def test_enter_confirms_the_plan_unchanged(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", return_value=""),
            contextlib.redirect_stdout(out),
        ):
            result = self._handler()(self.PLAN)
        self.assertEqual(result, self.PLAN)
        self.assertIn(self.PLAN, out.getvalue())
        self.assertIn(render.PLAN_PROMPT_HINT, out.getvalue())

    def test_typed_text_appends_a_revision_note(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", return_value="补一个竞品对比角度"),
            contextlib.redirect_stdout(out),
        ):
            result = self._handler()(self.PLAN)
        self.assertIn(self.PLAN, result)
        self.assertIn("用户修订意见：补一个竞品对比角度", result)

    def test_s_skips_the_plan(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", return_value="s"),
            contextlib.redirect_stdout(out),
        ):
            result = self._handler()(self.PLAN)
        self.assertIsNone(result)

    def test_q_aborts_the_run(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", return_value="q"),
            contextlib.redirect_stdout(out),
        ):
            with self.assertRaises(SystemExit):
                self._handler()(self.PLAN)

    def test_eof_skips_the_gate(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", side_effect=EOFError),
            contextlib.redirect_stdout(out),
        ):
            result = self._handler()(self.PLAN)
        self.assertIsNone(result)


class PlanWiringTest(unittest.TestCase):
    def test_create_passes_the_plan_handler_refine_passes_none(self) -> None:
        sentinel = lambda p: p
        create_calls: list[dict] = []
        refine_calls: list[dict] = []
        fake_for_create = SimpleNamespace(
            runs_root=lambda: "/runs",
            CONFIG_ROOT="/config",
            resolve_bundle=lambda runs, bid: "HANDLE",
            read_pin=lambda: "p" * 40,
            run_foreground=lambda handle, **kw: create_calls.append(kw)
            or SimpleNamespace(status="completed", generation=1, revision=3),
        )
        refined = SimpleNamespace(status="active", generation=2, composition="fixture", thread_id="t2")
        record = SimpleNamespace(generation=2, direction_text="深挖")
        fake_for_refine = SimpleNamespace(
            runs_root=lambda: "/runs",
            CONFIG_ROOT="/config",
            resolve_bundle=lambda runs, bid: "HANDLE",
            read_pin=lambda: "p" * 40,
            config_name_for_composition=lambda c: "fixture",
            run_foreground=lambda handle, **kw: refine_calls.append(kw)
            or SimpleNamespace(status="completed", generation=2, revision=8),
        )
        with (
            mock.patch.object(cli, "entrypoint", fake_for_create),
            mock.patch.object(cli.bundle_actions, "start") as start,
            mock.patch.object(cli, "_clarification_handler", return_value=None),
            mock.patch.object(cli, "_plan_handler", return_value=sentinel),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            start.return_value = SimpleNamespace(thread_id="t", composition="fixture")
            cli.cmd_create(SimpleNamespace(problem="问题", config="fixture"))
        self.assertIs(create_calls[0].get("on_plan"), sentinel)

        with (
            mock.patch.object(cli, "entrypoint", fake_for_refine),
            mock.patch.object(cli.bundle_actions, "refine", return_value=(refined, record)),
            mock.patch.object(cli, "_clarification_handler", return_value=None),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            cli.cmd_refine(SimpleNamespace(bundle_id="b1", direction="深挖"))
        # refine never gates: the direction document already is the plan.
        self.assertIsNone(refine_calls[0].get("on_plan"))


if __name__ == "__main__":
    unittest.main()
