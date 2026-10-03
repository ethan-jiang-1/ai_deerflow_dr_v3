"""The assembly snapshot middleware: what the model actually saw, once per run.

The injection slot has no error isolation (lead chain #32) — this hook is
self-defending: its own failures are journaled to a visible error note instead of
breaking the run. Framework-dependent module (imports AgentMiddleware); imported
lazily by the binding, never by the unit lane.

@impl DEW-001"""

from __future__ import annotations

import json
from pathlib import Path


def build_snapshot_middleware(snapshot_dir: Path, *, model_name: str, pin: str):
    """Build the first-round capture hook: rendered system prompt + visible tools,
    written once per run before the first model call completes."""

    from langchain.agents.middleware import AgentMiddleware  # framework import (lazy)

    captured = {"done": False}

    def _write_error_note(message: str) -> None:
        try:
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            (snapshot_dir / "assembly-snapshot-error.txt").write_text(message + "\n", encoding="utf-8")
        except Exception:  # noqa: BLE001 — the last-resort note failed too; do not raise into the chain
            pass

    class _AssemblySnapshot(AgentMiddleware):
        def wrap_model_call(self, request, handler):  # noqa: ANN001, ANN202
            self._capture_once(request)
            return handler(request)

        async def awrap_model_call(self, request, handler):  # noqa: ANN001, ANN202
            self._capture_once(request)
            return await handler(request)

        def _capture_once(self, request) -> None:  # noqa: ANN001
            if captured["done"]:
                return
            captured["done"] = True
            try:
                snapshot_dir.mkdir(parents=True, exist_ok=True)
                payload = {
                    "system_prompt": getattr(request, "system_prompt", ""),
                    "tools": [getattr(tool, "name", str(tool)) for tool in getattr(request, "tools", []) or []],
                    "model_name": model_name,
                    "deerflow_pin": pin,
                }
                (snapshot_dir / "assembly-snapshot.json").write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
            except Exception as exc:  # noqa: BLE001 — self-defending: journal, never break the chain
                _write_error_note(f"assembly snapshot capture failed: {exc}")

    return _AssemblySnapshot()
