"""Harness-owned scripted-ladder providers: a scripted chat model and a canned search tool.

The framework ships no fake models (verified), so the fixture configuration's `use:`
seams point here. The scripted model subclasses the framework's chat-model base
directly (``_generate``), replaying scripted AIMessages in order — tool calls included
— so the real agent loop (real middleware, real checkpointer, real event stream) runs
against scripted behavior.

The script comes from the ``DEERFLOW_FAKE_SCRIPT`` environment variable (a JSON array
of message objects: {"content": "..."} or {"content": "...", "tool_calls": [...]}),
falling back to a built-in direct answer. Scenarios set the variable before building
the client.

@impl DEW-001"""

from __future__ import annotations

import json
import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool
from pydantic import Field

DEFAULT_SCRIPT: list[dict] = [
    {"content": "Fixture answer: the scripted model completed the task directly."}
]


def _load_script() -> list[dict]:
    raw = os.environ.get("DEERFLOW_FAKE_SCRIPT")
    return json.loads(raw) if raw else DEFAULT_SCRIPT


class ScriptedChatModel(BaseChatModel):
    """Replays the scripted AIMessages in order (the last one repeats on overflow —
    loop caps belong to the caller). A script item may carry ``{"raise": "..."}``:
    ``_generate`` then raises, driving the framework's real error-fallback path."""

    script: list[dict] = Field(default_factory=list)
    cursor: int = 0

    def __init__(self, **kwargs) -> None:  # noqa: ANN401 — the loader passes model-config kwargs
        super().__init__(script=_load_script(), **kwargs)

    @property
    def _llm_type(self) -> str:
        return "scripted-fixture"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
        index = min(self.cursor, len(self.script) - 1)
        self.cursor += 1
        item = self.script[index]
        if item.get("raise"):
            raise RuntimeError(str(item["raise"]))
        kwargs: dict = {"content": item.get("content", "")}
        if item.get("tool_calls"):
            kwargs["tool_calls"] = item["tool_calls"]
        return ChatResult(generations=[ChatGeneration(message=AIMessage(**kwargs))])

    def bind_tools(self, tools, **kwargs):  # noqa: ANN001, ANN202 — framework signature
        # Tool execution happens in the agent's tool node; the scripted model only
        # emits tool_calls. Return self so the agent chain binds unchanged.
        return self


class FakeWebSearchTool(BaseTool):
    """A canned web_search stand-in: returns fixed documents, no network."""

    name: str = "web_search"
    description: str = "Fixture web search returning canned documents."

    def _run(self, query: str, **kwargs) -> str:  # noqa: ANN001
        return (
            "[fixture] Canned search results for: "
            f"{query}\n1. Supply-chain certification requires ISO 9001 and "
            "country-of-origin marking.\n2. Drone imports above 250g fall under "
            "additional registration."
        )


fake_web_search = FakeWebSearchTool()
