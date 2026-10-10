"""SearchLog: every web_search/web_fetch result becomes a readable file.

The round-4 ruling's fact owner: materialization is the readable projection of
data the checkpoint already holds — process diagnostics under
``diagnostics/searches/``, never admission evidence (the ``evidence/`` contract
is untouched). Deduplicated by tool-call id across the chunk and values-snapshot
event sources; a result without a paired observed call is not materialized.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from . import atomic

SEARCH_TOOL_NAMES: tuple[str, ...] = ("web_search", "web_fetch")


def _normalize_arguments(arguments) -> dict:
    """Framework tool_calls may carry arguments as a JSON string; the materialized
    file always carries a readable dict (a parse failure keeps the raw string)."""

    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str) and arguments.strip():
        try:
            parsed = json.loads(arguments)
            return parsed if isinstance(parsed, dict) else {"raw": arguments}
        except ValueError:
            return {"raw": arguments}
    return {}


class SearchLog:
    """Record search/fetch tool results as ``gen{N}-{seq:03d}-{name}.json`` files.

    ``note_call`` builds the call-id -> (tool name, arguments) pairing from
    observed AI messages; ``note_result`` materializes when the paired tool is a
    search tool and the call id has not been written yet. The generation prefix
    isolates runs (a refine re-run is a fresh instance whose sequence restarts).
    """

    def __init__(self, handle, generation: int) -> None:
        self._dir = Path(handle.root) / "diagnostics" / "searches"
        self._generation = generation
        self._calls: dict[str, tuple[str, dict]] = {}
        self._written: set[str] = set()
        self._seq = 0

    def note_call(self, call_id: str, name: str, arguments) -> None:
        if call_id:
            self._calls[call_id] = (name, _normalize_arguments(arguments))

    def note_result(self, call_id: str, content: str) -> None:
        if not call_id or call_id in self._written or call_id not in self._calls:
            return
        name, arguments = self._calls[call_id]
        if name not in SEARCH_TOOL_NAMES:
            return
        self._written.add(call_id)
        self._seq += 1
        payload = {
            "generation": self._generation,
            "seq": self._seq,
            "tool": name,
            "arguments": arguments,
            "content": content or "",
            "call_id": call_id,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        self._dir.mkdir(parents=True, exist_ok=True)
        atomic.atomic_write_bytes(
            self._dir / f"gen{self._generation}-{self._seq:03d}-{name}.json",
            (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
