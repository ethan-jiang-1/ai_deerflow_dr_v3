"""Level-2 stand-ins: content-addressed recording/replay at the LLM boundary.

Pure stdlib + langchain-core. Recording wraps a real model (composition) and journals
{normalized-input-hash: output} to a JSONL sink; replay serves recorded outputs by the
same hash. Misses fail loudly with the known-key list and an input preview — never
silent. The system prompt is EXCLUDED from the key (a frequently-edited detail, not
the contract); volatile substrings (dates, UUIDs, system-reminder blocks) are stripped.

@impl DEW-001"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

_VOLATILE_PATTERNS = (
    re.compile(r"<system-reminder>.*?</system-reminder>", re.S),
    re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"),
    re.compile(r"\d{4}-\d{2}-\d{2}"),
    re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^ ]*"),
)


def _strip_volatile(text: str) -> str:
    for pattern in _VOLATILE_PATTERNS:
        text = pattern.sub("", text)
    return text.strip()


def normalize_messages(messages: list) -> list[dict]:  # noqa: ANN001 — langchain message list
    """Canonical form for the replay key: non-system messages, volatile content
    stripped. This is the exact normalization the key hashes — the recorded
    fixture must survive it verbatim."""

    simplified: list[dict] = []
    for message in messages:
        kind = getattr(message, "type", None) or (
            message.get("type", "") if isinstance(message, dict) else ""
        )
        if kind == "system":
            continue
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content", "")
        simplified.append({"type": str(kind), "content": _strip_volatile(str(content or ""))})
    return simplified


def _canonical_messages(messages: list) -> str:  # noqa: ANN001
    return json.dumps(normalize_messages(messages), sort_keys=True, ensure_ascii=False)


def replay_key(messages: list) -> str:  # noqa: ANN001
    return hashlib.sha256(_canonical_messages(messages).encode("utf-8")).hexdigest()


class ReplayMiss(KeyError):
    """No recorded output for this input — the fixture is stale or incomplete."""

    def __init__(self, key: str, input_preview: str, known_keys: list[str]) -> None:
        preview = _strip_volatile(input_preview)[:800]
        super().__init__(
            f"replay miss: no recorded output for key {key} — known keys: "
            f"{known_keys}. Input preview: {preview}. Re-record the fixture."
        )


class _Base(BaseChatModel):
    sink: Path

    @property
    def _llm_type(self) -> str:
        return "replay-fixture"

    def _load(self) -> dict[str, dict]:
        """Return the full journal lines keyed by replay key.

        A line is ``{"key", "output"}`` plus an optional ``tool_calls`` list
        (``[{"name", "args", "id"}]``) — legacy lines without the field replay
        content-only, so old fixtures (the retained real-model-io sample) keep
        working unchanged.
        """
        if not Path(self.sink).is_file():
            return {}
        recorded: dict[str, dict] = {}
        for line in Path(self.sink).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            raw = json.loads(line)
            recorded[raw["key"]] = raw
        return recorded

    def _append(self, key: str, output: str, tool_calls: list | None = None) -> None:
        line: dict = {"key": key, "output": output}
        if tool_calls:
            line["tool_calls"] = tool_calls
        with Path(self.sink).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def _journal_tool_calls(calls: list) -> list[dict] | None:  # noqa: ANN001 — langchain/script tool-call dicts
    """Normalize tool calls (name/args/id[/type]) to the journal form; None when absent."""
    if not calls:
        return None
    return [
        {"name": str(c.get("name")), "args": c.get("args", {}), "id": str(c.get("id"))}
        for c in calls
    ]


def _tool_call_message(content: str, tool_calls: list | None):  # noqa: ANN202 — AIMessage
    if tool_calls:
        prepared = [
            {"name": c["name"], "args": c["args"], "id": c["id"], "type": "tool_call"}
            for c in tool_calls
        ]
        return AIMessage(content=content, tool_calls=prepared)
    return AIMessage(content=content)


class RecordingChatModel(_Base):
    """Delegates to a scripted sequence (or inner model) and journals each
    normalized-input-hash -> output pair — content, plus tool_calls when the turn
    carried them — to the sink."""

    script: list[dict] = Field(default_factory=list)
    cursor: int = 0
    inner: Any | None = None

    def __init__(self, *, sink, script: list[dict] | None = None, **kwargs) -> None:  # noqa: ANN001, ANN401
        super().__init__(sink=Path(sink), script=script or [], **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
        if self.inner is not None:
            # Recording mode: delegate to the real model, journal the I/O pair.
            result = self.inner._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
            message = result.generations[0].message
            self._append(
                replay_key(messages),
                str(message.content),
                _journal_tool_calls(list(getattr(message, "tool_calls", None) or [])),
            )
            return result
        index = min(self.cursor, len(self.script) - 1)
        self.cursor += 1
        item = self.script[index]
        output = str(item.get("content", ""))
        calls = _journal_tool_calls(item.get("tool_calls"))
        self._append(replay_key(messages), output, calls)
        return ChatResult(generations=[ChatGeneration(message=_tool_call_message(output, calls))])


class ReplayChatModel(_Base):
    """Serves recorded outputs by normalized-input hash. A miss fails loudly with
    the known-key list and an input preview — the fixture's staleness signal."""

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
        key = replay_key(messages)
        recorded = self._load()
        if key not in recorded:
            raise ReplayMiss(key, _canonical_messages(messages), sorted(recorded))
        line = recorded[key]
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=_tool_call_message(str(line["output"]), line.get("tool_calls"))
                )
            ]
        )
