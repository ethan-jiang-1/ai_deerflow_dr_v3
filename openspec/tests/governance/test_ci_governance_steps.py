"""The deterministic CI workflow carries the governance-side obligations.

The v2 contract updated in place for v3 (this change records both deliberate
divergences so they cannot rot silently):

- Workflow identity: v3 names the workflow ``governance.yml`` (one
  governance gate, one name); v2 used ``agent-tests.yml``.
- Path filters select all of ``openspec/**``, not just
  ``openspec/governance/**`` + ``openspec/tests/governance/**``. v2's
  narrower stance existed to keep spec/document edits from spinning the full
  harness suite; the v3 governance suite is seconds-fast stdlib with no
  harness tests yet, and spec/delta edits do affect the requirement and
  specification checkers on active changes — change ①'s diff proved that.
  When the harness suite grows, its owning change re-decides this stance.
- The governance ruff lint is deliberately deferred: the first v3 CI stays
  zero-dependency (pinned Python + pinned OpenSpec CLI only). The v2
  obligation ("``make verify`` can never lint the governance tree, so CI is
  the only host") remains real and lands with its own follow-up change.

Carried over unchanged from v2:

- The suite invocation must match the command the suite docstrings
  document, without ``-t .``: the governance suite is a plain directory,
  not a package, and unittest discovery with a distinct top-level
  directory raises ``ImportError: Start directory is not importable``
  (verified on Python 3.12.10 and 3.13.5). The ``-t .`` form therefore
  never executed a single test, which is how a red suite stayed unnoticed.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "governance.yml"

_CI_ESTABLISHED = WORKFLOW.is_file()
_SKIP_REASON = "CI workflow not established yet; pins activate when governance.yml lands"


@unittest.skipUnless(_CI_ESTABLISHED, _SKIP_REASON)
class CiGovernanceStepsTests(unittest.TestCase):
    def test_both_path_filters_select_all_governance_surfaces(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for filter_line in (
            '      - "openspec/**"',
            '      - "deep_research_harness/**"',
            '      - ".githooks/**"',
        ):
            self.assertEqual(
                workflow.count(filter_line),
                2,
                f"pull_request and push must both select {filter_line}",
            )

    def test_governance_suite_runs_the_documented_discover_command(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "python3 -m unittest discover -s openspec/tests/governance -q",
            workflow,
            "the workflow must run the governance suite with the command its "
            "docstrings document",
        )
        self.assertNotIn(
            "-s openspec/tests/governance -t",
            workflow,
            "discovery with a distinct top-level directory cannot import the "
            "governance suite (not a package); the -t form never ran a test",
        )


if __name__ == "__main__":
    unittest.main()
