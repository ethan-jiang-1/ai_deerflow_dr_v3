"""Binding-doc guard: the documented knob values must equal the code constants.

The binding knob table in ``docs/research-process.md`` is a projection of the
ruled defaults; its fact source is
``runtime/adapters/contracts/client_surface.py`` (CONSUMED_DEFAULTS) and
``runtime/adapters/client.py`` (DEEP_RESEARCH_RECURSION_LIMIT). A code change
that alters a knob without updating the doc turns this guard red, and vice
versa. The run-evidence traceability section heading in ``docs/run-bundle.md``
is likewise locked against silent deletion.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from deerflow_deep_research.runtime.adapters.client import DEEP_RESEARCH_RECURSION_LIMIT
from deerflow_deep_research.runtime.adapters.contracts.client_surface import (
    CONSUMED_DEFAULTS,
)

DOCS = Path(__file__).resolve().parents[3] / "docs"


class BindingKnobDocTest(unittest.TestCase):
    def test_documented_knob_values_equal_the_code_constants(self) -> None:
        text = (DOCS / "research-process.md").read_text(encoding="utf-8")
        for key, value in CONSUMED_DEFAULTS.items():
            pair = f"{key}={value}"
            self.assertIn(pair, text, f"binding doc must carry the ruled pair {pair!r}")

    def test_documented_recursion_limit_matches_the_per_call_constant(self) -> None:
        text = (DOCS / "research-process.md").read_text(encoding="utf-8")
        pair = f"recursion_limit={DEEP_RESEARCH_RECURSION_LIMIT}"
        self.assertIn(
            pair, text,
            f"binding doc must carry the per-call {pair!r} (not the AppConfig top-level value)",
        )


class RunEvidenceDocTest(unittest.TestCase):
    def test_run_bundle_map_keeps_the_traceability_section(self) -> None:
        text = (DOCS / "run-bundle.md").read_text(encoding="utf-8")
        self.assertIn(
            "## 一次 run 的证据关联", text,
            "run-bundle map must keep the run-evidence traceability section",
        )


if __name__ == "__main__":
    unittest.main()
