# Design

## Context

The replay mechanism (`runtime/scripted/replay_model.py`, @impl DEW-001) journals
`{key, output}` where output is message content only; research turns are driven by
`tool_calls`, so complete-graph replay needs them captured and reconstructed. The
framework model (`deerflow.models.patched_deepseek:PatchedChatDeepSeek`) is named by
`config/base.yaml`'s `use:` seam; the CLI's `--config` passthrough already maps any
non-fixture config to composition `all_real`. The E issue card holds the three-slice
plan and the maintainer's cost/desensitization commitments. See proposal.md — Why.

## Goals / Non-Goals

**Goals:**

- A `record` configuration that journals the real model's every turn (content +
  tool_calls + one-time metadata sidecar) with zero behavioral delta versus `base`.
- Journal format extension with strict backward compatibility (legacy content-only
  lines, including the retained sample, keep replaying).
- Zero API spend in this change — all red-greens run against scripted inner models.

**Non-Goals:**

- No E-2 real run here (separately triggered); no E-3 replay test here (its own change);
  no usage/token journaling (matches the ladder's declared token boundary); no
  desensitization tooling (human final stamp, per the fixtures discipline); no
  composition-vocabulary change (`record` is a config, not a composition); no CLI or
  admission changes.

## Decisions

1. **Subclass the framework model, don't wrap it.** `JournalingDeepSeek(JournalingMixin,
   PatchedChatDeepSeek)` inherits `bind_tools` and every protocol behavior from the
   framework class; only `_generate` (delegate to super, append journal line) and
   construction change. Alternative rejected: composing `RecordingChatModel(inner=…)` —
   its delegation bypasses `bind_tools` binding paths and is unexercised against the
   real agent loop; the subclass keeps the framework's own semantics bit-identical.
2. **The mixin is provider-agnostic and testable without the framework.** The journaling
   logic lives in `JournalingMixin`; tests apply it to `ScriptedChatModel` (harness
   fake) — no framework import, no API. Only the concrete `JournalingDeepSeek` touches
   the framework class, imported lazily at module scope of a module only `record.yaml`
   names. This keeps the unit lane framework-free per the test doctrine.
3. **Journal line schema: `{key, output, tool_calls?}`.** `tool_calls` is an optional
   list of `{name, args, id}`; `ReplayChatModel` reconstructs
   `AIMessage(content, tool_calls)` when present. Legacy lines without the field
   replay exactly as before (the `_load` change reads the field with `.get`). The
   script-mode `RecordingChatModel` also captures tool_calls from its script items so
   the mechanism's two modes share one format.
4. **Sidecar for metadata, never journal lines.** Model class, deerflow pin, argv, and
   timestamp go to `<sink>.meta.json`, written once at construction. Keeping meta out
   of the journal lines preserves the replay loader's simple line contract and lets
   E-3 assert provenance completeness without touching the mechanism.
5. **`config/record.yaml` is a full copy of base.yaml with one changed seam** (plus a
   header comment). Shape/secret separation is inherited (credentials stay `$VAR`
   references); the only diff is the model `use:` line. The spec's closed set grows by
   exactly one entry with pinned semantics.

## Risks / Trade-offs

- [Framework re-pin changes PatchedChatDeepSeek's constructor] → the subclass passes
  kwargs through untouched; a constructor break surfaces at E-2's run (loudly), and the
  contract-mirror lane governs the re-pin review moment.
- [Journal grows unbounded during a long run] → append-only jsonl, one line per model
  turn; a full research journey is tens of lines — bounded by the run itself.
- [Sink set but path unwritable] → first append fails loudly with the path; the knob
  fails at the earliest possible turn, not silently mid-run.
- [Legacy-line ambiguity] → a line missing `tool_calls` is legacy by definition; the
  loader treats absent as content-only. No version field is invented until a second
  format break exists.

## Migration Notes

Apply order: red-first tests (unset-env loud failure; tool-call turn journal+replay;
legacy compatibility; record-config resolution) → `JournalingMixin` +
`JournalingDeepSeek` + journal format extension → `config/record.yaml` + registries
(required-paths, COMMANDS, ladder note, asset registries) → receipts (`make verify`,
doc-hygiene, closeout gate, validate) → archive under the standing authorization; E-2
triggers only after this archives.
