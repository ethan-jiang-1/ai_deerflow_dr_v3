# Proposal: Establish Behavior Assertion Lane

## Why

The repo's quality-first ruling (CLS-017 裁决③, 2026-10-08) names **产出质量** — "the content
we produce is right" — as the endpoint, with test assets as the constraining mechanism. That
ruling also judged the trigger condition for a "行为断言 eval 栈" (behavior-assertion eval
stack, CLS-010 Tier C) as **already met**: research-engine quality has no automated
acceptance, stunt-ladder level 4 (behavior assertion, live face) is unplanned, and the
retained real-model sample has no test consumer. The machine-assertable surface of research
quality today is three points (report structure contract, materialization counts, source
traceability); behavior — what a real research run actually did (which tools, how the event
stream composes, how long) — asserts nothing. CLS-017's standing instruction (line 114):
when the output-quality surface exceeds the run-admission skeleton, establish the
`test-evidence` owning main spec first — it does not exist yet (12 specs, governance README
on record). The trigger row has fired and is consumed by this change's issue card.

## What Changes

- **New capability `test-evidence`** (the owning main spec named in governance records since
  the skeleton era): owns the evidence-ladder honesty discipline (every declared tier states
  what it does NOT prove) and the level-4 behavior-assertion semantics — assertions derive
  purely from recorded journals of real runs, observe rather than admit (they never gate run
  admission), and any event vocabulary they match on is a declared closed set.
- **New registered machine `behavior-profile`** (`engine/behavior_profile.py`, pure stdlib,
  zero I/O at the seam): derives a behavior profile from a run's `diagnostics/journal.jsonl`
  — per-tool call counts from `model_tool_call.calls`, event-kind composition, and the
  wall-clock span from first/last `ts`. Registered in `DECLARED_MACHINES` with a
  quality-register row (drift test keeps both sides in sync, same pattern as
  `source-traceability`).
- **Fixture-pinned behavior assertions**: a journal fixture extracted from a real recorded
  bundle (runs/ is local evidence and stays out of git; same precedent as
  `real-small-stream.json`): the profile of the real run is pinned by declared values, and a
  degenerate-research negative (a journal with zero search/fetch calls) is named and fails.
- **First test consumer for the retained real-model sample** (`tests/fixtures/replay/
  real-model-io.jsonl`): a replay assertion that the recorded key replays to the recorded
  output, with the sample's provenance limits (no input/model/pin/command — cannot
  independently verify realness) stated in the test that consumes it.
- **Ladder table sync**: `testing-and-evaluation.md` stunt-ladder row 4 moves ⬜ 未规划 → ✅
  with an honest limits column (token totals are NOT asserted — the journal has no
  structured token field; observation, not admission).

## Capabilities

### New Capabilities

- `test-evidence`: the owning spec for test-evidence semantics — the evidence ladder's
  honest boundaries (each tier declares what it does not prove), the behavior-assertion
  (level-4) semantics (pure derivation from recorded real-run journals, observe-not-admit,
  closed event vocabularies), and retained-sample consumption honesty (a consumed real
  sample states its provenance limits at the point of consumption).

### Modified Capabilities

<!-- none: adding a DECLARED_MACHINES entry plus its register row is registry operation
     under run-admission's existing "quality register stays in sync with the machines"
     requirement (the drift test enforces it); no existing requirement's observable
     behavior changes. -->

## Impact

- New: `openspec/changes/.../specs/test-evidence/spec.md` (delta; becomes
  `openspec/specs/test-evidence/spec.md` at archive); `deep_research_harness/src/
  deerflow_deep_research/engine/behavior_profile.py`; `deep_research_harness/tests/unit/
  engine/test_behavior_profile.py`; a journal fixture under `tests/fixtures/` (extracted
  verbatim from a real recorded run, with provenance noted); a sample-consumer test.
- Modified: `engine/machines.py` (one `DECLARED_MACHINES` entry), `docs/quality-register.md`
  (one row), `docs/testing-and-evaluation.md` (ladder row 4 + row 3 note updated), possibly
  `tests/README.md` (fixture registry row).
- Not touched: `deerflow/` gitlink (read-only, never modified or source-browsed by this
  change); run admission semantics (`validator`/`gate`/`ledger` untouched — behavior
  assertion observes, never admits); entry-surface CLI (no new subcommand; profiling a live
  bundle from the CLI is a later trigger); token-dimension assertion (no structured journal
  field — registered as a level-4 limit, not silently faked by parsing content strings);
  E/F/G items (CLS-017 rulings stand: E needs a recording commitment, F is first-round-out,
  G is explicitly not-done).

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/
  engine/behavior_profile.py` — the behavior-assertion semantics live in the new
  `test-evidence` spec, and this pure module is the machine that implements them; the
  registered-machine and fixture-pinning seams are the enforcement.
- **Seam classification:** deterministic-guardrail — pure functions over recorded textual
  facts (journal lines), closed vocabularies, red-first unit tests; no model, prompt, state
  machine, or lifecycle outcome is touched.
- **Question:** Can "what a real research run actually did" (tool selection, event
  composition, wall-clock span) be asserted by machine over recorded journals — pinned by
  real-run fixtures with degenerate negatives — under an owning spec that keeps every tier
  honest about what it does not prove, without touching run admission and without faking
  the token dimension the journal does not carry?
- **Necessary adjacent/external contracts:** `run-admission` capability (answers: the
  quality-register sync requirement the new machine registers under — observation never
  joins admission); `delivery-lanes` capability (answers: the standing proof-lane registry
  this ladder complements); `docs/testing-and-evaluation.md` ladder table (answers: the
  level-4 definition "工具选择/token/时长, 显式 opt-in" this change instantiates and its
  honest-limits column); CLS-017 (answers: 裁决③ output-quality endpoint, the E/F/G
  exclusions, and the line-114 owning-spec instruction); the issue card
  `_backlog/issues/2026-10-09-behavior-assertion-eval-stack.md` (answers: the fired-trigger
  consumption, the inventory, and the standing apply authorization).
- **Evidence seam:** red-first unit tests — machine↔register drift (delete the register row
  → red), fixture pinning (change a declared count → red), degenerate negative (zero
  search calls → named red), replay consumer (recorded output mismatch → red); `make
  verify` exit 0; closeout gate exit 0; doc-hygiene exit 0.
- **Not in scope:** token-dimension assertion (no structured journal field; declared limit);
  live-bundle CLI profiling (entry-surface untouched); E complete-graph replay (needs a
  recording commitment from the maintainer); F statement-level grounding sampling (semantic
  ruling + `agents/` bounded role, first-round-out per CLS-017); G multi-run variance
  (explicitly not-done); any change to run admission semantics.
- **Triggered review policies:** change-admission, local-context

## Impact on resident budgets

No resident-budget file is touched (`AGENTS.md`, `CLAUDE.md` stubs, harness `AGENTS.md`,
`openspec/config.yaml` unchanged); `docs/quality-register.md` and
`docs/testing-and-evaluation.md` are docs-layer (registered, link-checked), not budgeted.
