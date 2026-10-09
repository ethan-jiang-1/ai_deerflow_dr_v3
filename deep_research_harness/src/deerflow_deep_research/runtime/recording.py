"""Journaling mixin: journal every model ``_generate`` pair to a sink file.

Companion module ``recording_deepseek.py`` composes this mixin onto the framework's
real model for the ``record`` configuration (``config/record.yaml``); this module
stays framework-free so the unit test lane can apply the mixin to the harness's own
``ScriptedChatModel``.

The journal line is ``{"key", "output"}`` plus an optional ``tool_calls`` list —
the exact schema ``ReplayChatModel`` serves by — keyed by the normalized-input
hash. A one-time metadata sidecar (model class, deerflow pin, invocation,
timestamp) is written next to the sink: the provenance CLS-017's E item demanded
(the legacy retained sample lacked it).

Deliberate boundaries (on record): usage/token metadata is NOT journaled — the
recording boundary matches the ladder's declared token limit; the mixin changes
no wrapped-model semantics (binding, tool protocols, middleware order are
inherited untouched — only ``_generate`` and construction-time journal setup are
overridden).

@impl DEW-001"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from .scripted.replay_model import _journal_tool_calls, replay_key

SINK_ENV = "DEERFLOW_RECORD_SINK"


class JournalingMixin:
    """Journal every ``_generate`` pair to ``$DEERFLOW_RECORD_SINK``.

    Apply as ``class X(JournalingMixin, SomeChatModel)`` — the mixin's
    ``_generate`` delegates to ``super()`` (the wrapped model) and appends the
    journal line, so the wrapped model's behavior is bit-identical; only the
    journal file differs.
    """

    def _init_journal(self, *, pin: str | None = None) -> None:
        raw = os.environ.get(SINK_ENV)
        if not raw:
            raise RuntimeError(
                f"{SINK_ENV} is required for the record configuration — set it to "
                "the journal path (e.g. the run bundle's diagnostics/ directory)"
            )
        self._journal_sink = Path(raw)
        self._journal_sink.parent.mkdir(parents=True, exist_ok=True)
        self._last_journal_line: dict | None = None
        self._write_sidecar(pin=pin)

    def _write_sidecar(self, *, pin: str | None) -> None:
        sidecar = Path(str(self._journal_sink) + ".meta.json")
        if sidecar.is_file():
            return
        payload = {
            "model": type(self).__name__,
            "base_model": [c.__name__ for c in type(self).__mro__[1:3]],
            "deerflow_pin": pin,
            "argv": list(sys.argv),
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "journal_schema": ["key", "output", "tool_calls?"],
            "deliberate_limits": ["usage/token metadata not journaled"],
        }
        sidecar.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def _journal_result(self, messages, result) -> None:  # noqa: ANN001
        """Append the I/O pair for one model turn (shared by sync and async paths).

        The consecutive-duplicate guard exists because the async default path
        delegates to the sync override: when the wrapped model has no
        ``_agenerate`` of its own, one astream call flows through BOTH
        overrides and would journal the identical pair twice. Identical
        consecutive pairs are one turn; different turns always append.
        """
        message = result.generations[0].message
        line: dict = {
            "key": replay_key(messages),
            "output": str(message.content),
        }
        calls = _journal_tool_calls(list(getattr(message, "tool_calls", None) or []))
        if calls:
            line["tool_calls"] = calls
        if line == self._last_journal_line:
            return
        self._last_journal_line = line
        with self._journal_sink.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
        result = super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        self._journal_result(messages, result)
        return result

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
        """Journal the async path too — the framework drives the graph via
        astream, which reaches ``_agenerate`` and bypasses a sync-only override
        (the first E-2 attempt recorded zero lines exactly this way: sidecar
        written, journal empty)."""
        result = await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
        self._journal_result(messages, result)
        return result
