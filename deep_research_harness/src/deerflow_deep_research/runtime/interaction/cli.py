#!/usr/bin/env python3
"""Entry surface: six thin verbs over the run-bundle substrate.

Presentation only — every command delegates to the runtime actions; this script owns
no state authority (the owning spec lives in the repository's spec tree).

@impl ENS-001"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from ...domain import bundle
from .. import run_engine
from .. import entry as entrypoint
from ..bundle import bundle_actions, bundle_state
from . import render

COMMANDS = ("create", "status", "watch", "cancel", "refine", "inspect")

INTERACTIVE_ENV = "DEEP_RESEARCH_INTERACTIVE"


def _clarification_handler():
    """Build the interactive clarification handler when the context allows prompting.

    Gating: stdin is a TTY, or DEEP_RESEARCH_INTERACTIVE is set truthy (the override
    exists so subprocess contexts can drive the prompt and users can force it on).
    A non-interactive context gets no handler and the run engine keeps the bounded
    automatic continuation — stdin is never read.
    """

    override = os.environ.get(INTERACTIVE_ENV, "").strip().lower()
    interactive = sys.stdin.isatty() or override in {"1", "true", "yes", "on"}
    if not interactive:
        return None

    def handler(question: str) -> str:
        print(render.clarification_question(question))
        print(render.CLARIFICATION_PROMPT_HINT)
        try:
            return input("> ").strip()
        except EOFError:
            return ""  # a closed stdin declines; the engine falls back to the auto-reply

    return handler


def _plan_handler():
    """Build the interactive plan-gate handler when the context allows prompting.

    Same gate as the clarification handler (TTY or DEEP_RESEARCH_INTERACTIVE). The
    operator confirms the plan (Enter), appends a revision note (typed text), skips
    the injection (s), or aborts (q). A non-interactive context gets no handler and
    the engine never enters a plan phase.
    """

    override = os.environ.get(INTERACTIVE_ENV, "").strip().lower()
    interactive = sys.stdin.isatty() or override in {"1", "true", "yes", "on"}
    if not interactive:
        return None

    def handler(plan: str):
        print(render.proposed_plan(plan))
        print(render.PLAN_PROMPT_HINT)
        try:
            line = input("> ").strip()
        except EOFError:
            return None  # a closed stdin skips the gate; the run proceeds without injection
        if line == "s":
            return None
        if line == "q":
            raise SystemExit("plan gate aborted by operator")
        if not line:
            return plan
        return plan + "\n\n用户修订意见：" + line

    return handler


def _terminal_line(state) -> str:
    from types import SimpleNamespace

    entry = SimpleNamespace(
        category="terminal",
        event={"completed": "run_completed", "cancelled": "run_cancelled"}.get(
            state.status, "run_failed_resume"
        ),
        detail=(
            {"generation": state.generation, "reason": "see journal timeline"}
            if state.status == "failed-resume" else {"generation": state.generation}
        ),
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
        entrypoint.runs_root(), problem_text=args.problem, composition=composition, deerflow_pin=entrypoint.read_pin()
    )
    handle = entrypoint.resolve_bundle(entrypoint.runs_root(), state.thread_id)
    print(f"bundle {state.thread_id} started (config: {args.config}, composition: {state.composition})")

    try:
        result = entrypoint.run_foreground(
            handle, config_root=entrypoint.CONFIG_ROOT, config_name=args.config,
            thread_id=state.thread_id, pin=entrypoint.read_pin(), on_event=_live_renderer(),
            on_clarification=_clarification_handler(), on_plan=_plan_handler(),
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
    handle = entrypoint.resolve_bundle(entrypoint.runs_root(), args.bundle_id)
    state = bundle_actions.status(handle)
    print(f"state: {state.status} (generation {state.generation}, revision {state.revision})")
    delivery = getattr(state, "delivery", None)
    artifact = getattr(state, "delivery_artifact", None)
    if delivery == "admitted":
        print(f"delivery: admitted ({artifact})")
    elif delivery in {"rejected", "no-answer"}:
        print(f"delivery: {delivery}")
    else:
        print("delivery: (not recorded)")
    print(f"thread: {state.thread_id} | owner PID: {state.owner_pid} | composition: {state.composition}")
    from deerflow_deep_research.runtime.bundle import journal as journal_mod

    entries = journal_mod.read_entries(handle)
    for entry in entries[-5:]:
        print("  " + render.journal_line(entry))
    print(f"journal: {len(entries)} entries")


def cmd_watch(args) -> None:
    handle = entrypoint.resolve_bundle(entrypoint.runs_root(), args.bundle_id)
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
    handle = entrypoint.resolve_bundle(entrypoint.runs_root(), args.bundle_id)
    result = bundle_actions.cancel(handle)
    print(f"cancellation requested (state: {result.status}, generation {result.generation})")


def cmd_refine(args) -> None:
    handle = entrypoint.resolve_bundle(entrypoint.runs_root(), args.bundle_id)
    refined, record = bundle_actions.refine(handle, args.direction)
    print(f"generation {record.generation} started: {record.direction_text}")
    print(f"state: {refined.status}")
    # Phase 5 round-2 ruling: the next generation runs now, in the foreground,
    # over its own direction document, continuing the bundle's composition ladder.
    config_name = entrypoint.config_name_for_composition(refined.composition)
    try:
        result = entrypoint.run_foreground(
            handle, config_root=entrypoint.CONFIG_ROOT, config_name=config_name,
            thread_id=refined.thread_id, pin=entrypoint.read_pin(), on_event=_live_renderer(),
            on_clarification=_clarification_handler(),
        )
    except ImportError as exc:
        raise SystemExit(
            f"refine requires the deerflow environment (missing module: {exc.name}). "
            "Remedy: run `uv sync` inside deep_research_harness/, then "
            "`uv run python3 cli.py refine …`."
        ) from exc
    print(_terminal_line(result))
    print(f"state: {result.status} (generation {result.generation}, revision {result.revision})")


def cmd_inspect(args) -> None:
    handle = entrypoint.resolve_bundle(entrypoint.runs_root(), args.bundle_id)
    state = bundle_state.read_state(handle)
    print(f"state: {state.status} (generation {state.generation}, composition {state.composition})")
    from deerflow_deep_research.runtime.bundle import journal as journal_mod
    from deerflow_deep_research.runtime.bundle.admission import read_admitted_counts

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
        ("inspect", cmd_inspect, "journal timeline, admitted evidence, snapshot"),
    ):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("bundle_id")
        command.set_defaults(func=func)

    refine = sub.add_parser("refine", help="enter the next generation without running it")
    refine.add_argument("bundle_id")
    refine.add_argument("direction")
    refine.set_defaults(func=cmd_refine)

    args = parser.parse_args(argv)
    args.func(args)
    return 0
