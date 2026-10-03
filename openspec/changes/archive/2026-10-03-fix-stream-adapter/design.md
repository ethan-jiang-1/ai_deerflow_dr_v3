# Design

## Context

Verified by the live dump (see the plan's protocol notes): real `messages-tuple`
events carry the message chunk itself as a flat dict (`type`/`content`/`id`, with
`tool_calls` appearing as complete dicts when the model emits them) at token
granularity; `values` events carry full snapshots (already the authoritative terminal
picture, unchanged); `end` carries `usage` (stop_reason only on caps). The current
adapter reads `data["message"]` — a wrapper shape the fixture fakes assumed and the
real stream never sends, so the journal sink records nothing on real streams and the
renderer falls back to a useless per-token line. Policy routing:
`change-admission`; `skip_specs` because the deerflow-wiring requirement already
declares the behavior being repaired.

## Goals / Non-Goals

**Goals:** the engine conforms to the real stream shape; the journal records
aggregated per-turn entries on real streams; the live view streams AI tokens inline
with stable phrases for tools/state/turns.

**Non-Goals:** no terminal-rule changes, no spec text changes, no watch/projection
changes, no full deep-research run (follows separately).

## Decisions

1. **The adapter reads the data as the chunk** (`data` IS the message dict). The
   dict/object adapter stays (`_msg_field`) since the values path still receives
   message objects in real snapshots. Fake test events are reshaped to flat chunks —
   the fakes now mimic reality, which is the point the bug taught.
2. **Aggregation at turn granularity** (`_consume_turn` accumulates): AI text chunks
   append to a turn buffer; complete tool calls are collected; at turn end one
   `model_tool` entry is journaled per turn — `detail = {"calls": [...],
   "answer_excerpt": <last ≤80 chars>}` when calls exist, else `{"answer_excerpt":
   …}`. The existing phrase `model calls <tools>` renders unchanged (the golden
   stays valid); text-only turns gain a stable `model answered` projection.
3. **Streaming mode in the renderer** (`render.stream_chunk_text(event) -> str | None`):
   returns the inline text for an AI content chunk (None for everything else). The
   CLI's live handler prints it with `end=""`; non-None events fall through to the
   existing `event_line` phrases with a leading newline. The phrase vocabulary is
   unchanged; streaming is a presentation mode of the same module (the entry-surface
   requirement's "one rendering vocabulary" holds).
4. **Real-stream verification is part of the change**: a small real-ladder run must
   show (a) aggregated `model_tool` entries in the journal and (b) the live view
   streaming inline — the two failures this change exists to fix.

## Alternatives

- **Token-level journal entries** — rejected: the ledger would drown in token spam;
   the journal's bounded-honest semantics live at event granularity, and the plan's
   aggregation decision was explicit.
- **Renderer-side buffering of chunks into lines** — rejected: inline streaming is
   the honest live view (the user watches the model type); buffering would reintroduce
   the per-line spam with extra latency.
- **A spec delta describing the adapter shape** — rejected: the deerflow-wiring
   requirement already declares "feeding the journal"; this change conforms to it,
   and `skip_specs` is the honest shape (do not invent requirements).

## Risks / Trade-offs

- [Another masked-shape class of fake] → the fakes are reshaped to the real dump;
   real-ladder verification is part of the change's own gates (the discipline the bug
   taught: real runs are the test).
- [High-frequency on_event callbacks] → the handler prints only (O(1)); journal I/O
   happens once per turn.
- [Golden/phrase churn] → affected assertions updated red-green in this change; the
   stable-phrase discipline (volatile values excluded) is preserved.

## Migration Plan

Single apply, red-before-green: adapter/aggregation/streaming tests red (current
adapter ignores real-shaped chunks) → engine + renderer changes green; CLI live
handler swap; golden assertion updates; real-ladder verification; verification
sequence; reviews; archive; the plan closes as CLS-007; commit.

## Open Questions

(none — the real shapes were verified by the live dump recorded in the plan)
