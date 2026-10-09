"""The record configuration's model: the framework's real model, journaled.

Composed at module scope (this module is reached only through
``config/record.yaml``'s ``use:`` seam, so the framework import happens exactly
when a recording run constructs its client). The mixin owns the journaling; the
framework class owns every model semantic — subclassing is leverage, the
framework subtree is never modified.

@impl DEW-001"""

from __future__ import annotations

from deerflow.models.patched_deepseek import PatchedChatDeepSeek  # framework import, record-run only

from .recording import JournalingMixin


class JournalingDeepSeek(JournalingMixin, PatchedChatDeepSeek):
    """``PatchedChatDeepSeek`` + the journaling mixin; no other override."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN401 — the config loader passes model kwargs
        super().__init__(**kwargs)
        self._init_journal(pin=self._read_pin())

    @staticmethod
    def _read_pin() -> str | None:
        try:
            from .assembly import read_pin  # same runtime layer (..assembly would be a level-2 hop to a nonexistent module — caught by the import-boundary guard)

            return read_pin()
        except Exception:  # noqa: BLE001 — pin is metadata, never a run blocker
            return None
