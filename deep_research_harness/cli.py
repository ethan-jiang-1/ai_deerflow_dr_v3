#!/usr/bin/env python3
"""Entry surface: six thin verbs over the run-bundle substrate.

Presentation only — every command delegates to the runtime actions; this script owns
no state authority (the owning spec lives in the repository's spec tree).

@impl ENS-001"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from deerflow_deep_research.domain import bundle  # noqa: E402
from deerflow_deep_research.runtime import bundle_actions, bundle_state, render, run_engine  # noqa: E402

HARNESS_ROOT = Path(__file__).resolve().parent
CONFIG_ROOT = HARNESS_ROOT / "config"
SCOPES_ROOT = HARNESS_ROOT / "scopes"
DEERFLOW_DIR = HARNESS_ROOT.parent / "deerflow"

COMMANDS = ("create", "status", "watch", "cancel", "refine", "inspect")


def _pin() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(DEERFLOW_DIR), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"cannot resolve the deerflow pin: {exc}") from exc


def _resolve_bundle(bundle_id: str) -> bundle_state.BundleHandle:
    if SCOPES_ROOT.is_dir():
        for bucket_dir in sorted(SCOPES_ROOT.iterdir()):
            candidate = bucket_dir / bundle_id
            if bundle.is_valid_bucket(bucket_dir.name) and candidate.is_dir():
                return bundle_state.BundleHandle.open(candidate)
    raise SystemExit(
        f"bundle {bundle_id} is permanently unavailable: no such directory under "
        f"{SCOPES_ROOT} (deletion is permanent; there is no recovery path)"
    )


def _terminal_line(state) -> str:
    from types import SimpleNamespace

    entry = SimpleNamespace(
        category="terminal",
        event={"completed": "run_completed", "cancelled": "run_cancelled"}.get(
            state.status, "run_failed_resume"
        ),
        detail={"generation": state.generation, "reason": "see journal timeline"} if state.status == "failed-resume" else {"generation": state.generation},
    )
    return render.journal_line(entry)


def _live_renderer():
    """Streaming live view: AI tokens print inline (no newline); tools, state
    changes, and turn ends render as the shared phrase lines."""

    state = {"inline": False}

    def _render(event) -> None:
        text = render.stream_chunk_text(event)
        if text is not None:
            print(text, end="", flush=True)
            state["inline"] = True
            return
        if state["inline"]:
            print()
            state["inline"] = False
        print(render.event_line(event))

    return _render


def cmd_create(args) -> None:
    composition = "fixture" if args.config == "fixture" else "all_real"
    state = bundle_actions.start(
        SCOPES_ROOT, problem_text=args.problem, composition=composition, deerflow_pin=_pin()
    )
    handle = _resolve_bundle(state.thread_id)
    print(f"bundle {state.thread_id} started (config: {args.config}, composition: {state.composition})")

    from deerflow_deep_research.runtime import client as client_binding

    try:
        with client_binding.bundle_checkpointer(handle) as saver:
            client = client_binding.build_client(
                CONFIG_ROOT,
                args.config,
                checkpointer=saver,
                snapshot_dir=handle.root / "diagnostics",
                pin=_pin(),
            )
            result = run_engine.run_research(
                handle,
                stream_fn=client_binding.make_stream_fn(client, state.thread_id),
                on_event=_live_renderer(),
            )
    except ImportError as exc:
        raise SystemExit(
            f"create requires the deerflow environment (missing module: {exc.name}). "
            "Remedy: run `uv sync` inside deep_research_harness/, then "
            "`uv run python3 cli.py create …` (or `make create PROBLEM=…`)."
        ) from exc
    print(_terminal_line(result))
    print(f"state: {result.status} (generation {result.generation}, revision {result.revision})")


def cmd_status(args) -> None:
    handle = _resolve_bundle(args.bundle_id)
    state = bundle_actions.status(handle)
    print(f"state: {state.status} (generation {state.generation}, revision {state.revision})")
    print(f"thread: {state.thread_id} | owner PID: {state.owner_pid} | composition: {state.composition}")
    from deerflow_deep_research.runtime import journal as journal_mod

    entries = journal_mod.read_entries(handle)
    for entry in entries[-5:]:
        print("  " + render.journal_line(entry))
    print(f"journal: {len(entries)} entries")


def cmd_watch(args) -> None:
    handle = _resolve_bundle(args.bundle_id)
    journal_path = handle.root / bundle.journal_relative()
    position = 0
    while True:
        entries, reached_terminal, position = run_engine.tail_journal(journal_path, position)
        for entry in entries:
            print(render.journal_line(entry))
        if reached_terminal:
            return
        time.sleep(0.5)


def cmd_cancel(args) -> None:
    handle = _resolve_bundle(args.bundle_id)
    result = bundle_actions.cancel(handle)
    print(f"cancellation requested (state: {result.status}, generation {result.generation})")


def cmd_refine(args) -> None:
    handle = _resolve_bundle(args.bundle_id)
    refined, record = bundle_actions.refine(handle, args.direction)
    print(f"generation {record.generation} started: {record.direction_text}")
    print(f"state: {refined.status}")


def cmd_inspect(args) -> None:
    handle = _resolve_bundle(args.bundle_id)
    state = bundle_state.read_state(handle)
    print(f"state: {state.status} (generation {state.generation}, composition {state.composition})")
    from deerflow_deep_research.runtime import journal as journal_mod
    from deerflow_deep_research.runtime.admission import read_admitted_counts

    print("--- journal timeline ---")
    for entry in journal_mod.read_entries(handle):
        print("  " + render.journal_line(entry))
    print("--- admitted evidence ---")
    for kind, count in sorted(read_admitted_counts(handle).items()):
        print(f"  {kind}: {count}")
    snapshot = handle.root / "diagnostics" / "assembly-snapshot.json"
    print("--- assembly snapshot ---")
    if snapshot.is_file():
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
        print(f"  model: {payload.get('model_name', '?')} | tools: {', '.join(payload.get('tools', []))}")
    else:
        print("  (absent: run pre-dates the snapshot middleware)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Deep Research harness entry surface (create/status/watch/cancel/refine/inspect)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="start a bundle and run in the foreground")
    create.add_argument("problem")
    create.add_argument("--config", choices=["fixture", "base"], default="fixture")
    create.set_defaults(func=cmd_create)

    for name, func, help_text in (
        ("status", cmd_status, "state, journal summary, owner liveness"),
        ("watch", cmd_watch, "journal projection until the run is terminal"),
        ("cancel", cmd_cancel, "record a cancellation request"),
        ("inspect", cmd_inspect, "journal timeline, admitted evidence, snapshot, checkpoint"),
    ):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("bundle_id")
        command.set_defaults(func=func)

    refine = sub.add_parser("refine", help="re-run a terminal bundle as the next generation")
    refine.add_argument("bundle_id")
    refine.add_argument("direction")
    refine.set_defaults(func=cmd_refine)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
