"""The declared upstream gitlink lock never drifts from the recorded pointer.

The submodule commit is declared in the governance registry
(``openspec/governance/project-structure.toml``) and recorded as the
``deerflow`` gitlink in HEAD. This test fails the deterministic suite the
moment the two disagree.

When the harness code-side mirror exists
(``CURRENT_DEERFLOW_PIN`` in ``deep_research_harness/tests/contract/
test_deerflow_public_api.py``), the declared lock must additionally equal
that pin: the v2.1.0 upgrade updated one side and not the other, which
left the architecture gate red while every routine lane stayed green.
The v3 skeleton has not established the harness contract test yet, so
that leg activates automatically when the file appears.
"""

from __future__ import annotations

import re
import subprocess
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "openspec/governance/project-structure.toml"
PIN_TEST = REPO_ROOT / "deep_research_harness/tests/contract/test_deerflow_public_api.py"

_GITLINK_COMMIT_RE = re.compile(r'^commit\s*=\s*"([0-9a-f]{40})"\s*$', re.MULTILINE)
_PIN_RE = re.compile(r'^CURRENT_DEERFLOW_PIN\s*=\s*"([0-9a-f]{40})"\s*$', re.MULTILINE)


def _committed_gitlink() -> str | None:
    """The gitlink sha recorded for ``deerflow`` in HEAD, or None when absent."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD:deerflow"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha if re.fullmatch(r"[0-9a-f]{40}", sha) else None


class UpstreamPinAgreementTest(unittest.TestCase):
    def test_declared_gitlink_lock_equals_the_committed_pointer(self) -> None:
        manifest = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
        declared = manifest["upstream_gitlink"]["commit"]

        raw = REGISTRY.read_text(encoding="utf-8")
        lock_match = _GITLINK_COMMIT_RE.search(raw)
        self.assertIsNotNone(lock_match, "gitlink commit line not found in the structure registry")

        committed = _committed_gitlink()
        self.assertIsNotNone(committed, "HEAD records no deerflow gitlink; is the submodule committed?")
        self.assertEqual(
            declared,
            committed,
            "the structure registry's declared lock and the committed deerflow gitlink disagree; "
            "update both sides in the same change so the architecture gate stays green",
        )

    def test_declared_gitlink_lock_equals_the_code_side_pin_when_present(self) -> None:
        if not PIN_TEST.is_file():
            self.skipTest(
                "harness contract test not established yet (v3 skeleton); "
                "the pin agreement activates when test_deerflow_public_api.py lands"
            )
        manifest = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
        declared = manifest["upstream_gitlink"]["commit"]

        pin_match = _PIN_RE.search(PIN_TEST.read_text(encoding="utf-8"))
        self.assertIsNotNone(pin_match, "CURRENT_DEERFLOW_PIN not found in the harness contract test")

        self.assertEqual(
            declared,
            pin_match.group(1),
            "upstream gitlink lock and CURRENT_DEERFLOW_PIN disagree; "
            "update both sides in the same change so the architecture gate stays green",
        )


if __name__ == "__main__":
    unittest.main()
