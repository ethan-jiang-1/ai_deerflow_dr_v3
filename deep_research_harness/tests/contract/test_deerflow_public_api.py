"""Contract test: the declared DeerFlow surface against the real framework.

`runtime/adapters/contracts/client_surface.py` is the mirror — the surfaces this harness
consumes, typed and declared. This test compares every declaration against the installed
framework, and against the app's own call site where the declaration is about *our* usage
rather than the framework's shape. A drift fails naming the surface.

The framework is pinned (``CURRENT_DEERFLOW_PIN``, which the governance suite requires to
equal the structure registry's declared lock), so a drift here means the pin moved without
the mirror moving with it. Skipped without the framework environment — the unit lane never
needs it.

@impl DEW-001"""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import unittest
from pathlib import Path

from deerflow_deep_research.runtime.adapters.contracts import client_surface

HARNESS_ROOT = Path(__file__).resolve().parents[2]

#: The pinned framework revision — the harness-side anchor of the two-anchor pin.
#:
#: The agreement between this constant and the structure registry's declared lock is asserted
#: from the governance side (that suite reads both), which is the direction the dependency
#: rule requires: this package must not know the governance layer's paths.

CURRENT_DEERFLOW_PIN = "ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7"

_RECORDING = HARNESS_ROOT / "tests" / "fixtures" / "replay" / "real-small-stream.json"
_CLIENT_ADAPTER = HARNESS_ROOT / "src" / "deerflow_deep_research" / "runtime" / "adapters" / "client.py"


def _framework_available() -> bool:
    """Whether the pinned framework is importable in this environment."""
    try:
        importlib.import_module("deerflow.client")
    except Exception:  # noqa: BLE001 — any failure means "not usable here"
        return False
    return True


_FRAMEWORK_AVAILABLE = _framework_available()
_SKIP_REASON = "deerflow environment required: run `uv sync` in deep_research_harness/"


@unittest.skipUnless(_FRAMEWORK_AVAILABLE, _SKIP_REASON)
class DeclaredSurfaceVersusFrameworkTest(unittest.TestCase):
    """Every declaration in the mirror, checked against the installed framework."""

    def test_constructor_params_match_the_mirror_exactly(self) -> None:
        """Names, order and placement — the shape the mirror calls "the framework's"."""
        from deerflow.client import DeerFlowClient

        real = []
        for name, parameter in inspect.signature(DeerFlowClient.__init__).parameters.items():
            if name == "self":
                continue
            if parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
                real.append((name, "positional"))
            elif parameter.kind is inspect.Parameter.KEYWORD_ONLY:
                real.append((name, "keyword-only"))
            else:
                real.append((name, str(parameter.kind)))
        self.assertEqual(
            tuple(real),
            client_surface.CONSTRUCTOR_PARAMS,
            "DeerFlowClient's constructor drifted from the declared surface",
        )

    def test_stream_event_families_match_the_mirror_exactly(self) -> None:
        from deerflow.client import StreamEventType

        self.assertEqual(
            tuple(StreamEventType.__args__),
            client_surface.STREAM_EVENT_FAMILIES,
            "the stream event families drifted from the declared surface",
        )

    def test_stream_accepts_every_consumed_kwarg(self) -> None:
        """`thread_id` is explicit; `recursion_limit` rides the framework's ``**kwargs``.

        The distinction is the point: the mirror's comment records that the embedded
        stream's recursion limit is a per-call override, and the framework exposes it only
        through the catch-all — so a signature change that drops ``**kwargs`` breaks the
        binding even though no named parameter disappears.
        """
        from deerflow.client import DeerFlowClient

        signature = inspect.signature(DeerFlowClient.stream)
        explicit = {
            name
            for name, parameter in signature.parameters.items()
            if parameter.kind in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        }
        catches_all = any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()
        )
        for consumed in client_surface.CONSUMED_STREAM_KWARGS:
            self.assertTrue(
                consumed in explicit or catches_all,
                f"stream no longer accepts the consumed kwarg {consumed!r}; "
                f"explicit={sorted(explicit)}, **kwargs={catches_all}",
            )
        self.assertTrue(catches_all, "recursion_limit rides **kwargs; the catch-all must stay")

    def test_the_subclassed_model_class_exists(self) -> None:
        from deerflow.models.patched_deepseek import PatchedChatDeepSeek

        self.assertIsInstance(
            PatchedChatDeepSeek, type, "the class this harness subclasses is no longer a class"
        )

    def test_the_checkpointer_seam_exists(self) -> None:
        """The declared seam mixes a dotted path and a bare member of the same factory.

        ``("SqliteSaver.from_conn_string", "setup")`` — the first names the factory, the second
        a method on it. Both must resolve, so the entry is split when it is dotted and taken as
        a member of the factory when it is not.
        """
        from langgraph.checkpoint.sqlite import SqliteSaver

        owners = {"SqliteSaver": SqliteSaver}
        for symbol in client_surface.CHECKPOINTER_SEAM:
            head, dot, attribute = symbol.partition(".")
            owner, member = (owners.get(head), attribute) if dot else (SqliteSaver, symbol)
            self.assertIsNotNone(owner, f"unknown checkpointer owner in {symbol!r}")
            self.assertTrue(hasattr(owner, member), f"the checkpointer seam lost {symbol!r}")


class DeclaredSurfaceVersusOurUsageTest(unittest.TestCase):
    """Where the declaration is about *our* usage, the call site is the reality.

    Deliberately **not** gated on the framework: both cases read our own source and a recorded
    stream, so they hold in the framework-free unit lane too.
    """

    def _client_call(self) -> ast.Call:
        tree = ast.parse(_CLIENT_ADAPTER.read_text(encoding="utf-8"), filename=str(_CLIENT_ADAPTER))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
                if name == "DeerFlowClient":
                    return node
        raise AssertionError("no DeerFlowClient call found in the adapter")

    def test_the_consumed_defaults_are_still_what_the_binding_passes(self) -> None:
        """The ruled defaults: the literals must match, and the skill surface stays a pass-through."""
        call = self._client_call()
        passed = {keyword.arg: keyword.value for keyword in call.keywords}
        for key, expected in client_surface.CONSUMED_DEFAULTS.items():
            self.assertIn(key, passed, f"the binding no longer passes {key!r}")
            if key == "available_skills":
                self.assertIsInstance(
                    passed[key],
                    ast.Name,
                    "available_skills must stay a pass-through from the ladder, never hard-coded",
                )
            else:
                self.assertIsInstance(passed[key], ast.Constant, f"{key!r} is no longer a literal")
                self.assertIs(passed[key].value, expected, f"{key!r} drifted from the ruled default")

    def test_the_declared_snapshot_fields_appear_in_a_real_recording(self) -> None:
        """Positive evidence from a recorded stream.

        This proves the declaration is not fiction — each declared `values` field occurs in a
        real payload. It does **not** prove completeness: the framework exposes no public
        state schema, so a field absent from this recording could still exist upstream.
        """
        self.assertTrue(_RECORDING.is_file(), f"recording missing: {_RECORDING}")
        recorded = json.loads(_RECORDING.read_text(encoding="utf-8"))
        observed: set[str] = set()
        for event in recorded["events"]:
            if event.get("type") != "values":
                continue
            payload = event.get("data") or event
            observed.update(payload.keys())
        missing = sorted(set(client_surface.VALUES_PAYLOAD_FIELDS) - observed)
        self.assertEqual(
            missing, [], f"declared snapshot fields never seen in a real recording: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
