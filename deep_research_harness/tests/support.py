"""Shared test fixtures: one temporary run-bundle builder, one clock, one event kit.

The suite used to carry a copy of each of these in every file that needed one
(eighteen `bundle_actions.start(`, thirty-seven `TemporaryDirectory()`); changing
how a bundle is constructed meant editing a dozen files. They live here once.

Nothing in this module is a test: `unittest` discovery finds no test case here.

@impl DEW-001"""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state, journal

# The upstream pin every fixture declares. One canonical value, as the real
# ladder does: a bundle records the pin it ran against.
PIN = "c" * 40


def fixed_now(day: int = 3, hour: int = 12) -> datetime:
    """A deterministic clock for a fixture (the bucket name is derived from it)."""
    return datetime(2026, 10, day, hour, 0, tzinfo=UTC)


def bucket_for(now: datetime) -> str:
    """The run-bundle bucket that ``now`` falls into (`d_YYYYMMDD`)."""
    return f"d_{now:%Y%m%d}"


def build_run_bundle(
    runs_root: Path,
    *,
    problem: str = "研究 A 国无人机供应链的认证壁垒",
    composition: str = "all_real",
    now: datetime | None = None,
) -> tuple[object, bundle_state.BundleHandle]:
    """Start one bundle under ``runs_root`` and open it; returns (state, handle).

    The one construction path every fixture uses, so a change to how a bundle is
    started lands here instead of in a dozen test files.
    """
    moment = now or fixed_now()
    state = bundle_actions.start(
        runs_root, problem_text=problem, composition=composition,
        deerflow_pin=PIN, now=moment,
    )
    return state, bundle_state.BundleHandle.open(
        runs_root / bucket_for(moment) / state.thread_id
    )


class RunBundle:
    """A temporary runs root plus one started bundle, cleaned up with the test.

    ``runs`` is the runs root; ``handle`` is the opened bundle. Register it with
    ``addCleanup`` (or use it as a context manager) so the temporary tree goes away.
    """

    def __init__(self, case, *, problem: str = "研究 A 国无人机供应链的认证壁垒",
                 composition: str = "all_real", now: datetime | None = None) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        case.addCleanup(self._tmp.cleanup)
        self.now = now or fixed_now()
        self.runs = Path(self._tmp.name) / "runs"
        self.state, self.handle = build_run_bundle(
            self.runs, problem=problem, composition=composition, now=self.now
        )

    def reopen(self) -> bundle_state.BundleHandle:
        """Re-open the same bundle (for a second process-shaped observation)."""
        return bundle_state.BundleHandle.open(
            self.runs / bucket_for(self.now) / self.state.thread_id
        )


def read_journal(handle) -> list:
    """Every journal entry of one bundle, in file order."""
    return journal.read_entries(handle)


# ---------------------------------------------------------------- scripted stream
def event(event_type: str, **data) -> SimpleNamespace:
    """One stream event in the real shape (``type`` + ``data``)."""
    return SimpleNamespace(type=event_type, data=data)


def chunk_event(chunk: dict) -> SimpleNamespace:
    """A real-shaped messages-tuple event: the data IS the message chunk (flat)."""
    return SimpleNamespace(type="messages-tuple", data=chunk)


def ai(content: str = "", tool_calls: list | None = None) -> dict:
    """An AI message chunk, optionally carrying tool calls."""
    message: dict = {"type": "ai", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return message


def tool_result(call_id: str) -> dict:
    """A tool-result chunk answering one call id."""
    return {"type": "tool", "tool_call_id": call_id, "content": "ok"}


def ask_call(call_id: str = "c1", question: str = "范围选哪国市场？") -> dict:
    """A clarification tool call in the framework's shape."""
    return {"id": call_id, "name": "ask_clarification", "args": {"question": question}}
