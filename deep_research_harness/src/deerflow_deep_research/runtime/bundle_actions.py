"""Run-bundle actions: start / status / cancel / refine.

Pure stdlib. The actions compose the domain's pure rules with the state store and the
journal — they are the only writers, and every failure path fails loudly in
human-readable terms. The embedded client (wiring change) will drive these same
actions from the entry surface.

@impl RUB-001"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ..domain import bundle, journal_policy, state_machine
from ..domain.state_machine import BundleState, RefineRecord
from . import atomic, bundle_state
from .bundle_state import BundleHandle, write_state
from .journal import append_entry

Liveness = Callable[[int], bool]


def _default_liveness(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # the process exists and is not ours to signal
    return True


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _journal(handle: BundleHandle, category: str, event: str, detail: dict) -> None:
    append_entry(
        handle,
        journal_policy.JournalEntry(timestamp=_now_iso(), category=category, event=event, detail=detail),
    )


def start(
    scopes_root: Path,
    *,
    problem_text: str,
    composition: str,
    deerflow_pin: str,
    owner_pid: int | None = None,
    bundle_id: str | None = None,
    now: datetime | Callable[[], datetime] | None = None,
) -> BundleState:
    """Create a bundle atomically: build a staging tree, then publish it wholesale.

    Nothing is discoverable until the complete contract exists; a failure anywhere
    removes the staging tree and leaves no partial bundle."""

    if now is None:
        moment = datetime.now(timezone.utc)
    elif callable(now):
        moment = now()
    else:
        moment = now
    bucket = bundle.bucket_for_date(moment.year, moment.month, moment.day)
    bid = bundle_id or str(uuid.uuid4())
    # One UUID is both the bundle directory name and the client thread id (one run,
    # one thread); the wiring change reuses it verbatim.
    state = state_machine.rule_start(
        thread_id=bid,
        owner_pid=owner_pid or os.getpid(),
        deerflow_pin=deerflow_pin,
        composition=composition,
    )

    scopes = Path(scopes_root)
    staging = scopes / bundle.staging_name(bid)
    target = scopes / bucket / bid
    try:
        staging.mkdir(mode=0o700, parents=True)  # an existing staging or bundle path fails loudly here
        for relative in bundle.subtree_dirs():
            (staging / relative).mkdir(mode=0o700)
        atomic.atomic_write_text(staging / bundle.request_problem_relative(), problem_text + "\n")
        import json

        atomic.atomic_write_text(
            staging / bundle.state_relative(),
            json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n",
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic.publish_dir(staging, target)
    except FileExistsError as exc:
        _drop_staging(staging)
        raise state_machine.RuleViolation(
            f"bundle id collision: {target} already exists — deletion is permanent, so "
            "start refuses to overwrite"
        ) from exc
    except Exception:
        _drop_staging(staging)
        raise
    return state


def _drop_staging(staging: Path) -> None:
    import shutil

    shutil.rmtree(staging, ignore_errors=True)


def status(handle: BundleHandle, *, liveness: Liveness | None = None) -> BundleState:
    """Observe the run; a dead owner on an active bundle transfers to failed-resume."""

    probe = liveness or _default_liveness
    state = bundle_state.read_state(handle)
    transferred = state_machine.rule_crash_transfer(state, owner_alive=probe(state.owner_pid))
    if transferred is None:
        return state
    written = write_state(handle, state, transferred)
    _journal(
        handle,
        "terminal",
        "crash_detected",
        {"owner_pid": state.owner_pid, "reason": "owner PID no longer alive while state was active"},
    )
    return written


def cancel(handle: BundleHandle) -> BundleState:
    state = bundle_state.read_state(handle)
    requested = state_machine.rule_cancel(state)
    written = write_state(handle, state, requested)
    _journal(handle, "lifecycle", "cancellation_requested", {"generation": written.generation})
    return written


def refine(
    handle: BundleHandle, direction_text: str, *, fresh_context: str | None = None
) -> tuple[BundleState, RefineRecord]:
    """Refine the next generation. With ``fresh_context``, restart light: a new thread
    id, the prior lineage recorded, and the seed document in request/."""

    import uuid as _uuid

    state = bundle_state.read_state(handle)
    next_thread = str(_uuid.uuid4()) if fresh_context is not None else None
    refined, record = state_machine.rule_refine(state, direction_text, next_thread_id=next_thread)
    written = write_state(handle, state, refined)
    atomic.atomic_write_text(
        handle.root / bundle.refine_request_relative(record.generation), direction_text
    )
    if fresh_context is not None:
        atomic.atomic_write_text(
            handle.root / bundle.generation_context_relative(record.generation),
            fresh_context + "\n",
        )
    _journal(handle, "lifecycle", "refined", {"generation": record.generation})
    return written, record


def write_unanswered_questions(handle: BundleHandle, questions: list[str]) -> None:
    """Preserve unanswered clarification question texts (bounded-continuation exhaustion
    routes here before the failed-resume transfer)."""

    import json

    atomic.atomic_write_text(
        handle.root / bundle.UNANSWERED_QUESTIONS_RELATIVE,
        json.dumps({"questions": questions}, ensure_ascii=False, indent=2) + "\n",
    )
