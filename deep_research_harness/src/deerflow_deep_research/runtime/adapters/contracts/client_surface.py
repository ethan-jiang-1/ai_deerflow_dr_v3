"""Contract mirror: the DeerFlow surfaces this harness consumes, as typed declarations.

Shape only — the implementation is the framework's, always. The contract test compares
these declarations against the real framework surface; a drift fails naming the surface.

@impl DEW-001"""

from __future__ import annotations

# (parameter name, placement) in declaration order. placement is
# "positional" (positional-or-keyword) or "keyword-only".
CONSTRUCTOR_PARAMS: tuple[tuple[str, str], ...] = (
    ("config_path", "positional"),
    ("checkpointer", "positional"),
    ("model_name", "keyword-only"),
    ("thinking_enabled", "keyword-only"),
    ("subagent_enabled", "keyword-only"),
    ("plan_mode", "keyword-only"),
    ("agent_name", "keyword-only"),
    ("available_skills", "keyword-only"),
    ("middlewares", "keyword-only"),
    ("environment", "keyword-only"),
)

# The stream event families (client.py: StreamEventType Literal).
STREAM_EVENT_FAMILIES: tuple[str, ...] = ("values", "messages-tuple", "custom", "end")

# The `values` snapshot payload fields (verified: todos are NOT in the snapshot —
# the plan-mode TodoList is invisible to watch unless surfaced via custom events).
VALUES_PAYLOAD_FIELDS: tuple[str, ...] = ("title", "messages", "artifacts", "summary_text")

# The defaults this binding consumes (plan-ruled): full skill surface, no plan mode,
# subagents on.
CONSUMED_DEFAULTS: dict[str, object] = {
    "thinking_enabled": True,
    "subagent_enabled": True,
    "plan_mode": False,
    "available_skills": None,
}

# The checkpointer seam: the framework's own sync SQLite factory
# (runtime/checkpointer/provider.py: SqliteSaver.from_conn_string + setup()).
CHECKPOINTER_SEAM: tuple[str, ...] = ("SqliteSaver.from_conn_string", "setup")

# Consumed stream-call kwargs (verified client.py:293): the embedded stream's
# recursion_limit is a PER-CALL override (default 100, NOT the AppConfig top-level
# key — the recursion-chain scar) — the binding's make_stream_fn injects
# DEEP_RESEARCH_RECURSION_LIMIT there. Pinned here and by test.
CONSUMED_STREAM_KWARGS: tuple[str, ...] = ("thread_id", "recursion_limit")
