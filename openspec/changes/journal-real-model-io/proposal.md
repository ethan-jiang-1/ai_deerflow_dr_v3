# Proposal: Journal Real Model I/O

## Why

CLS-017's deferred item E — a real-model recording driving the complete graph with zero
credentials — received its立项 commitment (maintainer, 2026-10-10: cost and desensitization
both approved; the final desensitization stamp stays human). Probing found the blocker is
two-layered: the recording wrapper exists (`RecordingChatModel` inner-mode) but has no
runtime knob, and — deeper — the journal format stores only `content`
("不保留完整 tool_calls/usage 协议", on record), while research turns are driven by
`tool_calls`; recording without extending the format cannot replay research behavior at
all. This change lands the wiring and the format extension (zero API spend, scripted
inner models), so the follow-up real run (E-2) and the zero-credential complete-graph
replay (E-3) become possible.

## What Changes

- **New harness provider `runtime/recording.py`**: `JournalingMixin` (journals every
  `_generate` pair to the `DEERFLOW_RECORD_SINK` path; construction fails loudly when the
  env is unset; writes a one-time metadata sidecar — model class, deerflow pin, argv,
  timestamp — next to the sink) and `JournalingDeepSeek(JournalingMixin,
  PatchedChatDeepSeek)` (framework import stays lazy: the module loads only via the
  record configuration's `use:` seam).
- **Journal protocol extension** in `runtime/scripted/replay_model.py`: journal lines
  gain an optional `tool_calls` field (`[{name, args, id}]`); the recorder captures
  `AIMessage.tool_calls` when present and `ReplayChatModel` reconstructs
  `AIMessage(content, tool_calls)` — so a recorded research journey replays its tool
  turns. Backward compatible: old lines without the field replay content-only (the
  retained real-model-io sample keeps working). Usage/token metadata remains
  deliberately unrecorded (same boundary as ladder level 4's token dimension).
- **New checked-in configuration `config/record.yaml`**: base.yaml's real composition
  with the model `use:` seam pointed at the journaling provider; the bundle's declared
  composition stays `all_real` (it is a real run, journaled) — the CLI's existing
  else-branch already maps it honestly.
- **Registry/docs sync**: `required-paths.toml` (+record.yaml), `COMMANDS.md` (+ the
  `DEERFLOW_RECORD_SINK=… CONFIG=record make create …` recipe), the ladder table's
  level-3 note, and the two test-asset registries' limitation rows (tool_calls now
  recorded; usage still not).

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `deerflow-wiring`: the "Configuration resolution is explicit and never
  auto-discovered" requirement's closed set of checked-in configurations grows from
  `{base, fixture}` to `{base, fixture, record}`, with record's semantics pinned
  (real model wrapped by the journaling provider, `DEERFLOW_RECORD_SINK` required,
  composition stays `all_real`).

## Impact

- New: `runtime/recording.py`, `config/record.yaml`, tests for the mixin/journal/replay
  reconstruction.
- Modified: `runtime/scripted/replay_model.py` (journal write/read gain optional
  `tool_calls`; recorder script-mode also captures them), `runtime/scripted/__init__.py`
  unchanged, `required-paths.toml`, `COMMANDS.md`, `docs/testing-and-evaluation.md`
  (level-3 note), `tests/README.md` + `tests/fixtures/README.md` (limitation rows),
  `_backlog` issue card (E card, first change linked).
- Not touched: `deerflow/` gitlink (read-only; the framework model class is imported and
  subclassed at a harness-owned seam, never modified); run admission semantics
  (composition vocabulary unchanged — `record` is a config, not a composition);
  `engine/` machines; CLI verbs (the `--config` passthrough already handles it); no real
  API call in this change (E-2 is the spend point, separately authorized).

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/
  runtime/scripted/replay_model.py` — the journal protocol is the contract both the
  recorder and the replayer consume; the wiring provider is the thin seam that feeds it.
- **Seam classification:** wiring — composition/seam plumbing around a model boundary;
  the journal extension is a deterministic serialization detail, red-first testable, no
  model, prompt, or lifecycle semantics touched.
- **Question:** Can the recording knob and the tool_calls-carrying journal land as
  wiring (config closed set +1, provider seam, format extension with backward
  compatibility) so that a follow-up real run produces a fixture that drives the
  complete graph offline — without spending API budget in this change and without
  touching run admission?
- **Necessary adjacent/external contracts:** `deerflow-wiring` capability (answers: the
  config-resolution closed set this change extends, and the contract-mirror discipline
  the new provider seam must not disturb); `test-evidence` capability (answers: the
  ladder semantics the level-3 asset must stay honest about — usage/token stays
  unrecorded); the E issue card `_backlog/issues/2026-10-10-real-model-io-complete-replay.md`
  (answers: the three-slice plan, the cost/desensitization commitments, the human
  final-stamp boundary); `run-admission` capability (answers: composition stays
  `all_real` — no vocabulary change).
- **Evidence seam:** red-first unit/integration tests — unset `DEERFLOW_RECORD_SINK` →
  loud construction failure; a scripted tool-call turn journals a `tool_calls` line and
  replays as `AIMessage(content, tool_calls)`; old-format lines (the retained sample)
  still replay content-only; `--config record` resolves to record.yaml with composition
  `all_real`; `make verify` exit 0; closeout gate exit 0.
- **Not in scope:** the real API run (E-2, separately triggered after this archives);
  desensitization tooling (human final stamp, per the fixtures discipline — no
  sanitizer is built here); usage/token recording (boundary consistent with level 4);
  admission or CLI-verb changes; E-3's complete-graph replay test (its own change, fed
  by E-2's recording).
- **Triggered review policies:** change-admission, deerflow-downstream-boundary, local-context
