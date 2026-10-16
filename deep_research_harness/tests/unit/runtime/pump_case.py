"""The shared case for the pump's behaviour-family tests.

The run-engine test file was one 674-line grab bag; its four families now live in
`test_pump*.py` and share this case. The scripted-event helpers come from
`tests/support.py` (aliased to the names the moved bodies already used, so every
body stayed verbatim).

@impl DEW-001"""

from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from support import ai as _ai
from support import ask_call as _ask_call
from support import chunk_event as _chunk_event
from support import event as _event
from support import tool_result as _tool_result

from deerflow_deep_research.domain import state_machine
from deerflow_deep_research.runtime import pump
from deerflow_deep_research.runtime.bundle import bundle_actions, bundle_state

_PIN = "c" * 40
_FIXED_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_FIXED_BUCKET = "d_20261003"


def journal_mod_entries(handle):
    from deerflow_deep_research.runtime.bundle import journal as journal_mod

    return journal_mod.read_entries(handle)


class PumpCase(unittest.TestCase):
    # The marked-plan vocabulary the plan-gate tests share (it lives in the old
    # file's class body, which the first split pass had missed).
    _PLAN_TEXT = "研究计划：\n1. 广度探索认证壁垒的全景\n2. 深挖 A 国消费级法规"
    _MARKED_PLAN = "<research-plan>\n" + _PLAN_TEXT + "\n</research-plan>"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs = Path(self._tmp.name) / "runs"
        self.state = bundle_actions.start(
            self.runs, problem_text="研究 A 国无人机供应链的认证壁垒", composition="all_real",
            deerflow_pin=_PIN, now=_FIXED_NOW,
        )
        self.handle = bundle_state.BundleHandle.open(self.runs / _FIXED_BUCKET / self.state.thread_id)

    def _absorbed_turn_messages(self) -> list[dict]:
        """The 5128f695 incident shape: the terminal AI message asks alongside a
        search, and the framework answers the ask in-turn — the ask call lands in the
        answered set, so no unanswered question is detected."""
        return [
            _ai(tool_calls=[
                _ask_call("c1"),
                {"id": "t1", "name": "web_search", "args": {"query": "认证壁垒"}},
            ]),
            _tool_result("t1"),
            {"type": "tool", "tool_call_id": "c1", "content": "ok"},  # the framework's in-turn answer
        ]

    def _lifecycle(self) -> list:
        return [e for e in journal_mod_entries(self.handle) if e.category == "lifecycle"]

    def _drive_to_completion(self, answer: str) -> state_machine.BundleState:
        def stream_fn(message: str):
            yield _event("values", title="t", messages=[_ai(answer)])
            yield _chunk_event(_ai(answer))
            yield _event("end")

        return pump.run_research(self.handle, stream_fn=stream_fn)
