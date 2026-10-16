"""The command line: plain mode and the self-test delegate."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys

from .rules import violations


def _self_test() -> list[str]:
    """Run the negative-control battery and return the failing case identities.

    Thin delegate by design: the cases and their assertion identities live in
    ``_battery.py`` (one home), and the governance unittest battery
    (``tests/governance/test_doc_hygiene.py``) drives the same registry. This
    module keeps the CLI contract — command, stdout, exit codes — not a second
    copy of the assertions.
    """
    import _battery

    return _battery.failing_controls()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true", help="run negative-control fixtures")
    args = parser.parse_args()

    if args.self_test:
        errs = _self_test()
        if errs:
            print("doc-hygiene self-test FAILED:", file=sys.stderr)
            print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
            return 1
        print("doc-hygiene self-test passed.")
        return 0

    found = violations(args.project_root.resolve())
    if found:
        print("doc-layer hygiene violations:", file=sys.stderr)
        print("\n".join(f"- {v}" for v in found), file=sys.stderr)
        return 1
    print("doc-layer hygiene passed.")
    return 0
