"""Wiring mirror + config resolution tests (framework-free unit lane).

@impl DEW-001"""

from __future__ import annotations

import unittest
from pathlib import Path

from deerflow_deep_research.runtime import client as client_binding
from deerflow_deep_research.runtime.contracts import client_surface

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_ROOT = _REPO_ROOT / "deep_research_harness" / "config"


class MirrorTest(unittest.TestCase):
    def test_mirror_covers_the_ten_constructor_parameters(self) -> None:
        names = [name for name, _ in client_surface.CONSTRUCTOR_PARAMS]
        self.assertEqual(
            names,
            [
                "config_path",
                "checkpointer",
                "model_name",
                "thinking_enabled",
                "subagent_enabled",
                "plan_mode",
                "agent_name",
                "available_skills",
                "middlewares",
                "environment",
            ],
        )

    def test_mirror_covers_the_four_event_families(self) -> None:
        self.assertEqual(
            client_surface.STREAM_EVENT_FAMILIES,
            ("values", "messages-tuple", "custom", "end"),
        )

    def test_values_payload_fields_exclude_todos(self) -> None:
        self.assertEqual(
            client_surface.VALUES_PAYLOAD_FIELDS,
            ("title", "messages", "artifacts", "summary_text"),
        )
        self.assertNotIn("todos", client_surface.VALUES_PAYLOAD_FIELDS)

    def test_consumed_defaults_match_the_ruled_binding(self) -> None:
        self.assertEqual(client_surface.CONSUMED_DEFAULTS["plan_mode"], False)
        self.assertEqual(client_surface.CONSUMED_DEFAULTS["subagent_enabled"], True)
        self.assertIsNone(client_surface.CONSUMED_DEFAULTS["available_skills"])
        self.assertEqual(client_surface.CONSUMED_DEFAULTS["thinking_enabled"], True)

    def test_checkpointer_seam_is_the_sync_factory(self) -> None:
        self.assertEqual(
            client_surface.CHECKPOINTER_SEAM,
            ("SqliteSaver.from_conn_string", "setup"),
        )


class ConfigResolutionTest(unittest.TestCase):
    def test_explicit_existing_paths_resolve(self) -> None:
        for name in ("base", "fixture"):
            path = client_binding.resolve_config_path(_CONFIG_ROOT, name)
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.parent, _CONFIG_ROOT)

    def test_unknown_name_fails_naming_the_request(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            client_binding.resolve_config_path(_CONFIG_ROOT, "turbo")
        self.assertIn("turbo", str(ctx.exception))

    def test_missing_file_fails_naming_the_request(self) -> None:
        import shutil
        import tempfile

        empty_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, empty_root, True)
        with self.assertRaises(FileNotFoundError) as ctx:
            client_binding.resolve_config_path(empty_root, "base")
        self.assertIn("base", str(ctx.exception))

    def test_binding_defaults_are_the_ruled_ones(self) -> None:
        self.assertEqual(client_binding.BINDING_DEFAULTS["plan_mode"], False)
        self.assertEqual(client_binding.BINDING_DEFAULTS["subagent_enabled"], True)
        self.assertIsNone(client_binding.BINDING_DEFAULTS["available_skills"])


class FixtureSeamsTest(unittest.TestCase):
    def test_fixture_use_seams_point_at_harness_owned_fakes(self) -> None:
        fixture_text = (_CONFIG_ROOT / "fixture.yaml").read_text(encoding="utf-8")
        self.assertIn("deerflow_deep_research.runtime.fixtures", fixture_text)
        for seam in ("use:",):
            self.assertIn(seam, fixture_text)

    def test_base_config_pins_summarization_enabled(self) -> None:
        base_text = (_CONFIG_ROOT / "base.yaml").read_text(encoding="utf-8")
        self.assertIn("summarization", base_text)
        self.assertIn("true", base_text)

    def test_base_config_keeps_secrets_as_var_references(self) -> None:
        base_text = (_CONFIG_ROOT / "base.yaml").read_text(encoding="utf-8")
        self.assertIn("$VAR", base_text)


class StreamSeamMirrorTest(unittest.TestCase):
    def test_consumed_stream_kwargs_are_declared(self) -> None:
        self.assertEqual(
            client_surface.CONSUMED_STREAM_KWARGS, ("thread_id", "recursion_limit")
        )


class StreamFactoryTest(unittest.TestCase):
    def test_stream_fn_carries_the_recursion_limit_and_thread(self) -> None:
        from deerflow_deep_research.runtime import client as cb

        recorded = {}

        class FakeClient:
            def stream(self, message, **kwargs):
                recorded.update(kwargs, message=message)
                return iter(())

        fn = cb.make_stream_fn(FakeClient(), "thread-1")
        fn("研究问题")
        self.assertEqual(recorded["thread_id"], "thread-1")
        self.assertEqual(recorded["recursion_limit"], 1000)


if __name__ == "__main__":
    unittest.main()
