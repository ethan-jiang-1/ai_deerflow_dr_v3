"""Explicit event recording tool; base calls external APIs and overwrites a sample.

Run from the source checkout through `make record-stream` or this script. This is
not a test runner or a sanitization tool. Recorded events are consumed by replay tests.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT / "src"))

from deerflow_deep_research.runtime import entry
from deerflow_deep_research.runtime.bundle import bundle_actions  # noqa: E402
from deerflow_deep_research.runtime.adapters import client as cb  # noqa: E402

DEFAULT_PROBLEM = "用三句话说明 EASA UAS 开放类别的核心限制"
DEFAULT_OUTPUT = HARNESS_ROOT / "tests/fixtures/replay/real-small-stream.json"


def record(problem: str, config: str, *, scopes_root: Path, output: Path) -> int:
    """Record to an explicit path; no lifecycle/admission completion is implied."""
    pin = entry.read_pin()
    state = bundle_actions.start(
        scopes_root, problem_text=problem,
        composition="all_real" if config == "base" else "fixture", deerflow_pin=pin,
    )
    handle = entry.resolve_bundle(scopes_root, state.thread_id)
    events = []
    with cb.bundle_checkpointer(handle) as saver:
        client = cb.build_client(
            entry.CONFIG_ROOT, config, checkpointer=saver,
            snapshot_dir=handle.root / "diagnostics", pin=pin,
        )
        for event in client.stream(problem, thread_id=state.thread_id):
            data = getattr(event, "data", None)
            events.append({"type": event.type, "data": data if isinstance(data, dict) else {"_repr": repr(data)[:200]}})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"problem": problem, "config": config, "events": events}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"recorded {len(events)} events -> {output}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", nargs="?", default=DEFAULT_PROBLEM)
    parser.add_argument("config", nargs="?", choices=("base", "fixture"), default="base")
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="recording path (existing file is overwritten)",
    )
    parser.add_argument("--scopes-root", type=Path, default=entry.SCOPES_ROOT, help="local Bundle data root")
    args = parser.parse_args(argv)
    return record(args.problem, args.config, scopes_root=args.scopes_root, output=args.output)


if __name__ == "__main__":
    sys.exit(main())
