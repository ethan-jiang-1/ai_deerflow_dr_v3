"""Interactive clarification gating: when does the CLI prompt, and what flows through.

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


class ClarificationGatingTest(unittest.TestCase):
    def test_noninteractive_context_builds_no_handler(self) -> None:
        with (
            mock.patch.object(cli.sys.stdin, "isatty", return_value=False),
            mock.patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop(INTERACTIVE_ENV, None)
            self.assertIsNone(cli._clarification_handler())

    def test_tty_builds_a_handler(self) -> None:
        with (
            mock.patch.object(cli.sys.stdin, "isatty", return_value=True),
            mock.patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop(INTERACTIVE_ENV, None)
            handler = cli._clarification_handler()
            self.assertIsNotNone(handler)
            self.assertTrue(callable(handler))

    def test_env_override_builds_a_handler_without_a_tty(self) -> None:
        with (
            mock.patch.object(cli.sys.stdin, "isatty", return_value=False),
            mock.patch.dict(os.environ, {INTERACTIVE_ENV: "1"}),
        ):
            self.assertIsNotNone(cli._clarification_handler())

    def test_env_override_falsy_does_not_build_a_handler(self) -> None:
        with (
            mock.patch.object(cli.sys.stdin, "isatty", return_value=False),
            mock.patch.dict(os.environ, {INTERACTIVE_ENV: "0"}),
        ):
            self.assertIsNone(cli._clarification_handler())


class ClarificationHandlerBehaviorTest(unittest.TestCase):
    def _handler(self) -> object:
        with mock.patch.dict(os.environ, {INTERACTIVE_ENV: "1"}):
            return cli._clarification_handler()

    def test_handler_renders_question_and_returns_the_answer(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", return_value="A 国，消费级"),
            contextlib.redirect_stdout(out),
        ):
            answer = self._handler()("范围选哪国市场？")
        self.assertEqual(answer, "A 国，消费级")
        self.assertIn("范围选哪国市场？", out.getvalue())
        self.assertIn(render.CLARIFICATION_PROMPT_HINT, out.getvalue())

    def test_handler_empty_input_declines(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", return_value=""),
            contextlib.redirect_stdout(out),
        ):
            answer = self._handler()("范围选哪国市场？")
        self.assertEqual(answer, "")

    def test_handler_eof_declines(self) -> None:
        out = io.StringIO()
        with (
            mock.patch.object(builtins, "input", side_effect=EOFError),
            contextlib.redirect_stdout(out),
        ):
            answer = self._handler()("范围选哪国市场？")
        self.assertEqual(answer, "")


class ClarificationWiringTest(unittest.TestCase):
    def test_create_passes_the_handler_through_run_foreground(self) -> None:
        sentinel = lambda q: "x"
        calls: list[dict] = []
        fake_entrypoint = SimpleNamespace(
            runs_root=lambda: "/runs",
            CONFIG_ROOT="/config",
            resolve_bundle=lambda runs, bid: "HANDLE",
            read_pin=lambda: "p" * 40,
            run_foreground=lambda handle, **kw: calls.append(kw)
            or SimpleNamespace(status="completed", generation=1, revision=3),
        )
        args = SimpleNamespace(problem="问题", config="fixture")
        with (
            mock.patch.object(cli, "entrypoint", fake_entrypoint),
            mock.patch.object(cli.bundle_actions, "start") as start,
            mock.patch.object(cli, "_clarification_handler", return_value=sentinel),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            start.return_value = SimpleNamespace(
                thread_id="t", composition="fixture",
            )
            cli.cmd_create(args)
        self.assertEqual(calls[0].get("on_clarification"), sentinel)

    def test_refine_passes_the_handler_through_run_foreground(self) -> None:
        sentinel = lambda q: "x"
        calls: list[dict] = []
        refined = SimpleNamespace(status="active", generation=2, composition="fixture", thread_id="t2")
        record = SimpleNamespace(generation=2, direction_text="深挖")
        fake_entrypoint = SimpleNamespace(
            runs_root=lambda: "/runs",
            CONFIG_ROOT="/config",
            resolve_bundle=lambda runs, bid: "HANDLE",
            read_pin=lambda: "p" * 40,
            config_name_for_composition=lambda c: "fixture",
            run_foreground=lambda handle, **kw: calls.append(kw)
            or SimpleNamespace(status="completed", generation=2, revision=8),
        )
        args = SimpleNamespace(bundle_id="b1", direction="深挖")
        with (
            mock.patch.object(cli, "entrypoint", fake_entrypoint),
            mock.patch.object(cli.bundle_actions, "refine", return_value=(refined, record)),
            mock.patch.object(cli, "_clarification_handler", return_value=sentinel),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            cli.cmd_refine(args)
        self.assertEqual(calls[0].get("on_clarification"), sentinel)


if __name__ == "__main__":
    unittest.main()
