"""Entry assembly and launcher behavior, without importing the framework."""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from deerflow_deep_research.runtime import entry
from deerflow_deep_research.runtime.bundle import bundle_actions
from deerflow_deep_research.runtime.interaction import cli

HARNESS = Path(__file__).resolve().parents[3]
PIN = "c" * 40


class RunsRootResolutionTest(unittest.TestCase):
    def test_default_runs_root_is_repository_root_outside_the_application(self):
        from deerflow_deep_research.domain import bundle as domain_bundle

        self.assertEqual(entry.RUNS_ROOT, HARNESS.parent / "runs")
        self.assertEqual(entry.RUNS_ROOT.name, domain_bundle.RUNS_ROOT_NAME)
        # The application subtree must not contain run-bundle data.
        self.assertNotIn(HARNESS, entry.RUNS_ROOT.parents)

    def test_env_override_redirects_runs_root_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {entry.RUNS_ROOT_ENV: directory}):
                self.assertEqual(entry.runs_root(), Path(directory))
        # Without the override the repository default resolves.
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(entry.RUNS_ROOT_ENV, None)
            self.assertEqual(entry.runs_root(), entry.RUNS_ROOT)


def without_framework(path: Path, *arguments: str):
    """Block runtime dependencies even when the invoking interpreter has them installed."""
    program = """
import importlib.abc, runpy, sys
class NoFramework(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'deerflow', 'langgraph', 'langchain', 'langchain_core', 'yaml'}:
            raise ModuleNotFoundError('blocked runtime dependency: ' + fullname, name=fullname)
sys.meta_path.insert(0, NoFramework())
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""
    return subprocess.run(
        [sys.executable, "-I", "-S", "-c", program, str(path), *arguments],
        cwd=HARNESS, capture_output=True, text=True,
    )


class EntryCompositionTest(unittest.TestCase):
    def test_lookup_uses_bundle_bucket_contract_and_missing_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = Path(directory)
            state = bundle_actions.start(runs, problem_text="question", composition="fixture", deerflow_pin=PIN)
            handle = entry.resolve_bundle(runs, state.thread_id)
            self.assertEqual(handle.root.name, state.thread_id)
            with self.assertRaisesRegex(SystemExit, "permanently unavailable"):
                entry.resolve_bundle(runs, "ffffffff-ffff-ffff-ffff-ffffffffffff")

    def test_wholesale_relocated_bundle_stays_operable(self):
        """Locks the migration-safety property: state records carry no absolute paths,
        so a bundle directory moved wholesale (retired scopes/ root -> runs/) keeps
        working under the new root."""
        import shutil
        from datetime import datetime, timezone

        with tempfile.TemporaryDirectory() as old_root, tempfile.TemporaryDirectory() as new_root:
            state = bundle_actions.start(
                Path(old_root), problem_text="question", composition="fixture", deerflow_pin=PIN,
                bundle_id="0f0e0d0c-0b0a-4938-8276-5f5d4e3d2c1b",
                now=datetime(2026, 10, 3, tzinfo=timezone.utc),
            )
            # Move the whole date bucket (the one-time physical relocation shape).
            shutil.move(str(Path(old_root) / "d_20261003"), str(Path(new_root) / "d_20261003"))
            handle = entry.resolve_bundle(Path(new_root), state.thread_id)
            observed = bundle_actions.status(handle)
            self.assertEqual(observed.thread_id, state.thread_id)
            self.assertEqual(observed.status, "active")

    def test_foreground_assembly_forwards_bundle_config_pin_and_live_sink(self):
        from deerflow_deep_research.runtime import run_engine
        from deerflow_deep_research.runtime.adapters import client

        handle = SimpleNamespace(root=Path("/bundle"))
        saver, stream, sink, result = object(), object(), object(), object()
        config = HARNESS / "config"
        yaml_stub = SimpleNamespace(safe_load=lambda text: {"models": [{"name": "fixture-scripted"}]})
        with (
            patch.dict(sys.modules, {"yaml": yaml_stub}),
            patch.object(client, "bundle_checkpointer", return_value=contextlib.nullcontext(saver)),
            patch.object(client, "build_client", return_value="client") as build,
            patch.object(client, "make_stream_fn", return_value=stream) as make_stream,
            patch.object(run_engine, "run_research", return_value=result) as run,
        ):
            actual = entry.run_foreground(
                handle, config_root=config, config_name="fixture", thread_id="thread", pin=PIN, on_event=sink,
            )
        self.assertIs(actual, result)
        build.assert_called_once_with(
            config, "fixture", checkpointer=saver, model_name="fixture-scripted",
            snapshot_dir=Path("/bundle/diagnostics"), pin=PIN,
        )
        make_stream.assert_called_once_with("client", "thread")
        run.assert_called_once_with(handle, stream_fn=stream, on_event=sink, on_clarification=None, on_plan=None)

    def test_pin_failure_names_the_missing_framework_checkout(self):
        with patch.object(entry.subprocess, "run", side_effect=OSError("missing git")):
            with self.assertRaisesRegex(SystemExit, "cannot resolve the deerflow pin"):
                entry.read_pin(Path("/missing"))

    def test_create_publishes_bundle_and_started_line_before_foreground_and_explains_missing_dependency(self):
        output = io.StringIO()

        def missing_dependency(handle, **kwargs):
            self.assertTrue((handle.root / "state.json").is_file())
            self.assertIn("started (config: fixture, composition: fixture)", output.getvalue())
            self.assertEqual(kwargs["thread_id"], handle.root.name)
            raise ModuleNotFoundError("missing langgraph", name="langgraph")

        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(entry, "RUNS_ROOT", Path(directory)),
            patch.object(entry, "read_pin", return_value=PIN),
            patch.object(entry, "run_foreground", side_effect=missing_dependency),
            contextlib.redirect_stdout(output),
            self.assertRaisesRegex(SystemExit, r"missing module: langgraph.*uv sync"),
        ):
            cli.main(["create", "question", "--config", "fixture"])


class LauncherTest(unittest.TestCase):
    def test_help_remains_usable_without_framework(self):
        result = without_framework(HARNESS / "cli.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for verb in ("create", "status", "watch", "cancel", "refine", "inspect"):
            self.assertIn(verb, result.stdout)

    def test_recorder_help_remains_usable_without_framework(self):
        result = without_framework(HARNESS / "tools/record_stream.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--output", result.stdout)

    def test_no_framework_harness_rejects_planted_eager_import(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "eager.py"
            script.write_text("import deerflow\n", encoding="utf-8")
            result = without_framework(script, "--help")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blocked runtime dependency: deerflow", result.stderr)

    def test_observation_commands_disclose_missing_bundle(self):
        for verb in ("status", "watch", "inspect"):
            with self.subTest(verb=verb):
                result = without_framework(HARNESS / "cli.py", verb, "ffffffff-ffff-ffff-ffff-ffffffffffff")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("permanently unavailable", result.stderr)

    def test_refine_help_discloses_next_generation_without_automatic_run(self):
        result = without_framework(HARNESS / "cli.py", "--help")
        self.assertIn("without running", result.stdout)


if __name__ == "__main__":
    unittest.main()
