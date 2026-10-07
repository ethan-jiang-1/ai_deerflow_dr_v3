"""DeerFlow client binding: explicit config resolution and ruled defaults.

The framework import is lazy (inside build_client) so mirror-constant and
config-resolution logic stay testable without the framework.

@impl DEW-001"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from ...domain import bundle
from .contracts import client_surface

CONFIG_NAMES: tuple[str, ...] = ("base", "fixture")

# The embedded stream's recursion limit is a PER-CALL override (upstream
# deerflow/backend/packages/harness/deerflow/client.py:293) — the
# AppConfig top-level key is not consumed by the embedded path. Deep research exhausts
# the default 100 at ~10 tool rounds; 300 is a conservative start (framework max 1000).
DEEP_RESEARCH_RECURSION_LIMIT = 1000  # proven by the completing gen-5 run (evidence arc 23->86->209->completed)


def make_stream_fn(client, thread_id: str, *, recursion_limit: int = DEEP_RESEARCH_RECURSION_LIMIT):
    """Build the run's stream callable: the single seam where stream calls are made,
    carrying the thread id and the per-call recursion limit."""

    def _stream(message: str):
        return client.stream(message, thread_id=thread_id, recursion_limit=recursion_limit)

    return _stream

# The ruled binding defaults (see runtime/contracts/client_surface.CONSUMED_DEFAULTS).
BINDING_DEFAULTS: dict[str, object] = dict(client_surface.CONSUMED_DEFAULTS)


def resolve_config_path(config_root: Path, name: str) -> Path:
    """Resolve an explicit checked-in configuration path. No framework auto-discovery:
    an unknown name or a missing file fails loudly naming the request."""

    if name not in CONFIG_NAMES:
        raise ValueError(
            f"unknown configuration {name!r}: expected one of {CONFIG_NAMES} "
            "(explicit config resolution — the framework's default discovery is refused)"
        )
    path = Path(config_root) / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(
            f"configuration {name!r} not found at {path} — pass an explicit, checked-in path"
        )
    return path


@contextmanager
def bundle_checkpointer(handle):
    """Open the bundle's sync SqliteSaver via the framework's own factory seam
    (from_conn_string + setup). Framework import is lazy."""

    from langgraph.checkpoint.sqlite import SqliteSaver  # framework import (lazy)

    conn_str = str(Path(handle.root) / bundle.checkpoint_relative())
    with SqliteSaver.from_conn_string(conn_str) as saver:
        saver.setup()
        yield saver


def build_client(
    config_root: Path,
    config_name: str,
    *,
    checkpointer,
    middlewares=None,
    model_name: str | None = None,
    available_skills: object | None = None,
    snapshot_dir: Path | None = None,
    pin: str | None = None,
):
    """Construct the embedded DeerFlowClient with the ruled defaults.

    ``available_skills`` is sourced from the owning ladder's declaration by the
    assembly (resolve_skills) and passed through verbatim — never hard-coded
    here; the default ``None`` is the unwired binding posture (deerflow-wiring
    delta). When ``snapshot_dir`` is given, the assembly-snapshot middleware is
    injected first (plan decision 4's escape hatch, first use). The framework
    import is deliberately lazy: this function requires the deerflow-harness
    dependency; the unit lane never calls it."""

    from deerflow.client import DeerFlowClient  # lazy: framework import

    config_path = resolve_config_path(config_root, config_name)
    # The framework re-resolves lazily in later code paths (agent build, extensions);
    # pin its own resolution seam to our explicit file so nothing auto-discovers a
    # different config.yaml behind the binding's back.
    import os

    os.environ["DEER_FLOW_CONFIG_PATH"] = str(config_path)
    injected = list(middlewares) if middlewares else []
    if snapshot_dir is not None:
        from .snapshot_middleware import build_snapshot_middleware

        injected.insert(0, build_snapshot_middleware(snapshot_dir, model_name=model_name or "", pin=pin or ""))
    return DeerFlowClient(
        config_path=str(config_path),
        checkpointer=checkpointer,
        model_name=model_name,
        thinking_enabled=True,
        subagent_enabled=True,
        plan_mode=False,
        available_skills=available_skills,
        middlewares=injected,
    )


def summarize_prior_thread(checkpoint_path, thread_id: str) -> str:
    """A mechanical projection of the prior thread (framework-lazy): counts, the
    original question, the prior final-answer excerpt. Deterministic code — the model
    decides how to use it, never what it says."""

    from langgraph.checkpoint.sqlite import SqliteSaver  # framework import (lazy)

    with SqliteSaver.from_conn_string(str(checkpoint_path)) as saver:
        state = saver.get_tuple({"configurable": {"thread_id": thread_id}})
        messages = (
            state.checkpoint.get("channel_values", {}).get("messages", []) if state and state.checkpoint else []
        )
    humans = [m for m in messages if getattr(m, "type", "") == "human"]
    tools = [m for m in messages if getattr(m, "type", "") == "tool"]
    answers = [m for m in messages if getattr(m, "type", "") == "ai" and getattr(m, "content", "")]
    question = str(humans[0].content)[:300] if humans else "(未记录)"
    excerpt = str(answers[-1].content)[-800:] if answers else "(无最终回答)"
    return (
        f"# 上一代上下文摘要（机械投影）\n\n"
        f"- 原始问题：{question}\n"
        f"- 消息总数：{len(messages)}；工具结果：{len(tools)}\n"
        f"- 上一代最终回答（末 800 字）：\n\n{excerpt}\n"
    )
