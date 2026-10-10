"""Replay-fixture providers: the complete-graph replay seams (ladder level 3).

A recorded real journey (model I/O journal + materialized search corpus) drives
the REAL framework graph with zero credentials. The model seam serves the
recorded turns **in journey order**; the search/fetch seams serve the recorded
tool result for each recorded (tool, arguments) pair. Misses fail loudly —
journey exhaustion means the graph diverged structurally from the recorded run.

Why order-based, not key-based (measured, 2026-10-10): the framework's
first-turn message assembly varies with the model configuration and environment
(three distinct first-turn keys were measured for the same problem across the
real run, a CLI-path scripted probe, and a direct-assembly replay:
e96eb2e776fa / 4ce402058705 / 75b4270c727d) — cross-environment key matching
is unsuitable for journey replay. The recorded keys stay in the fixture as
provenance; single-turn replay (``ReplayChatModel``) keeps key matching, where
it belongs.

The fixture root comes from ``DEERFLOW_REPLAY_ROOT`` (the test sets it to
``tests/fixtures/replay/e2-complete-journey``); the provider is test-lane wiring,
not an operator configuration — the checked-in config set is unchanged.

@impl DEW-001"""

from __future__ import annotations

import json
import os
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool
from pydantic import Field

REPLAY_ROOT_ENV = "DEERFLOW_REPLAY_ROOT"

# One journey, one position: the framework constructs the model more than once
# per run (lead agent, summarization middleware, …) and every construction used
# to reset the cursor — the replay's final turn then re-served line 1 (measured:
# the "report" came back plan-marked and was rejected by the admission face).
# The recorded journal is ONE global call sequence; all instances in the process
# share this position. A new fixture root resets it (test isolation).
_SHARED_POSITION: dict = {"root": None, "cursor": 0}


def _reset_shared_position(root: Path) -> None:
    if _SHARED_POSITION["root"] != str(root):
        _SHARED_POSITION["root"] = str(root)
        _SHARED_POSITION["cursor"] = 0


def _replay_root() -> Path:
    raw = os.environ.get(REPLAY_ROOT_ENV)
    if not raw:
        raise RuntimeError(
            f"{REPLAY_ROOT_ENV} is required for the replay-fixture providers — "
            "set it to the recorded journey's fixture directory"
        )
    return Path(raw)


class JourneyReplayModel(BaseChatModel):
    """Serves the recorded journey's model turns in order; exhaustion is loud.

    Turn i of the replayed graph receives the recorded journey's turn i
    (content and tool_calls reconstructed verbatim). A model call beyond the
    recorded journey's length fails loudly — the structural divergence signal:
    the graph made a call the recorded run never made."""

    turns: list = Field(default_factory=list)
    cursor: int = 0

    def __init__(self, **kwargs) -> None:  # noqa: ANN401 — the config loader passes model kwargs
        journal = _replay_root() / "model-io.jsonl"
        if not journal.is_file():
            raise RuntimeError(f"replay journal missing: {journal}")
        raw = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
        # The recorded journal interleaves the agent's calls with middleware model
        # calls (the summarization middleware has its own instance). A mid-journey
        # content-only line cannot be an agent turn — an agent turn ending in plain
        # text would have ENDED the agent loop, and the recorded journey continued
        # past it (proof by continuation). The replay assembly disables
        # summarization, so the agent's calls consume exactly the agent subsequence:
        # the first line (plan), every tool-call line, and the last line (report).
        if len(raw) > 2:
            turns = [raw[0]] + [line for line in raw[1:-1] if line.get("tool_calls")] + [raw[-1]]
        else:
            turns = raw
        _reset_shared_position(_replay_root())
        super().__init__(turns=turns, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "journey-replay-fixture"

    def bind_tools(self, tools, **kwargs):  # noqa: ANN001, ANN202 — framework signature
        return self

    def _serve(self, messages) -> ChatResult:  # noqa: ANN001
        position = self.cursor + 0  # noqa: F841 — instance cursor kept for introspection; serving reads the shared position below
        cursor = _SHARED_POSITION["cursor"]
        if cursor >= len(self.turns):
            raise KeyError(
                f"journey replay exhausted at model call {cursor + 1}: the "
                "graph made a call the recorded journey never made — structural "
                "divergence (re-record the fixture or fix the graph)"
            )
        line = self.turns[cursor]
        _SHARED_POSITION["cursor"] = cursor + 1
        self.cursor = cursor + 1
        tool_calls = [
            {"name": c["name"], "args": c["args"], "id": c["id"], "type": "tool_call"}
            for c in (line.get("tool_calls") or [])
        ]
        message = (
            AIMessage(content=str(line["output"]), tool_calls=tool_calls)
            if tool_calls
            else AIMessage(content=str(line["output"]))
        )
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
        return self._serve(messages)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):  # noqa: ANN001, ANN202
        return self._serve(messages)


def _corpus_lookup() -> dict[tuple[str, str], str]:
    """(tool, canonical-arguments) -> recorded result content; loads once per call."""
    path = _replay_root() / "corpus.jsonl"
    if not path.is_file():
        raise RuntimeError(f"replay corpus missing: {path}")
    corpus: dict[tuple[str, str], str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        key = (str(record["tool"]), json.dumps(record["arguments"], sort_keys=True, ensure_ascii=False))
        corpus[key] = str(record["content"])
    return corpus


def _recorded_result(tool_name: str, arguments: dict) -> str:
    corpus = _corpus_lookup()
    key = (tool_name, json.dumps(arguments, sort_keys=True, ensure_ascii=False))
    if key not in corpus:
        raise KeyError(
            f"replay corpus miss for {tool_name} {arguments!r} — the recorded "
            "journey never made this call; the fixture is stale or the graph diverged"
        )
    return corpus[key]


class ReplayWebSearchTool(BaseTool):
    """Serves the recorded search result for each recorded query."""

    name: str = "web_search"
    description: str = "Replays the recorded web_search results from the fixture corpus."

    def _run(self, query: str, **kwargs) -> str:  # noqa: ANN001
        return _recorded_result("web_search", {"query": query})


class ReplayWebFetchTool(BaseTool):
    """Serves the recorded fetch result for each recorded URL."""

    name: str = "web_fetch"
    description: str = "Replays the recorded web_fetch results from the fixture corpus."

    def _run(self, url: str, **kwargs) -> str:  # noqa: ANN001
        return _recorded_result("web_fetch", {"url": url})


replay_web_search = ReplayWebSearchTool()
replay_web_fetch = ReplayWebFetchTool()
