# Proposal: Land Complete Graph Replay

## Why

CLS-017's E item — a real recorded journey driving the complete graph with zero
credentials — has everything except the last mile: the recording journal (10 lines: plan
turn, seven tool turns, report turn) and the materialized search corpus (28 query→result
records) exist as local evidence from the post-BUG-001 acceptance run (bundle 55c35d44);
the level-3 ladder note still says "尚无真实模型记录接入图的旅程证明". This change lands
the replay providers, the fixture, and the test that closes that sentence: the recorded
journey replays the REAL framework graph (real assembly, middleware, checkpointer, hold
point) with zero credentials, ending in the recorded report admitted verbatim.

## What Changes

- **New replay providers** (`runtime/replay_fixture.py`, test-lane wiring — the
  checked-in config set is unchanged): `JourneyReplayModel` serves the recorded model
  turns **in journey order** (content + tool_calls reconstructed verbatim; exhaustion
  fails loudly as the structural-divergence signal; a process-shared cursor because the
  framework constructs the model more than once per run — lead agent and middleware each
  got their own cursor-0 instance until the shared position landed, measured as the
  "plan-marked report" rejection); `replay_web_search`/`replay_web_fetch` serve the
  recorded corpus by (tool, arguments) with loud misses.
- **Order-based, not key-based — a measured design decision**: the framework's
  first-turn message assembly varies with the model configuration and environment
  (three distinct first-turn keys measured for the same problem across the real run, a
  CLI-path scripted probe, and a direct assembly: e96eb2e776fa / 4ce402058705 /
  75b4270c727d). Cross-environment key matching is unsuitable for journey replay; the
  recorded keys stay in the fixture as provenance, and single-turn replay
  (`ReplayChatModel`) keeps key matching where it belongs. The serving queue filters
  mid-journey content-only lines (proof by continuation: an agent turn ending in plain
  text would have ended the agent loop, and the recorded journey continued past them —
  they are middleware calls, the summarization instance); the replay assembly disables
  summarization so no middleware call competes for the queue.
- **New fixture** `tests/fixtures/replay/e2-complete-journey/`: the model journal, the
  corpus (28 records), and the recording's provenance sidecar — extracted verbatim from
  the acceptance run. Desensitization: machine scan 0 hits (key patterns, 27 public
  framework-comparison queries, public-source report); maintainer pre-clearance on
  record (2026-10-10); scan results recorded in the Delivery Record.
- **New integration test** `tests/integration/test_complete_graph_replay.py`: drives
  `run_research` through the real assembly with the replay seams (a temp config derived
  from fixture.yaml with three `use:` swaps, summarization disabled, web_fetch added —
  the recorded journey used it) and asserts: completed; `plan_proposed` + `plan_confirmed`
  journaled; the final report equals the recorded report verbatim; no plan markers; a
  Sources-class section; `admit` in the ledger; and the config carries no `$VAR` secret
  reference (structural zero-credential).
- **Bind-tools fix in the mechanism** (`runtime/scripted/replay_model.py`): `_Base`
  gains `bind_tools → self` (the default raises NotImplementedError — surfaced the first
  time the replay drove the real agent chain).
- **Docs**: the ladder table's level-3 note flips ("真实记录接入图的旅程证明" now exists,
  linked to the test); the two test-asset registries gain the fixture rows.

## Capabilities

### New Capabilities

<!-- none: test-lane wiring at existing seams plus a test asset; the checked-in
     configuration set and every spec requirement are unchanged. -->

### Modified Capabilities

<!-- none (skip_specs declared). -->

## Impact

- New: `runtime/replay_fixture.py`, `tests/fixtures/replay/e2-complete-journey/`
  (3 files), `tests/integration/test_complete_graph_replay.py`.
- Modified: `runtime/scripted/replay_model.py` (`_Base.bind_tools`), ladder note in
  `docs/testing-and-evaluation.md`, registry rows in `tests/README.md` and
  `tests/fixtures/README.md`, the E issue card's 落地关联 (closes with this change).
- Not touched: `deerflow/` gitlink (read-only); the checked-in config set; run
  admission (the replayed report passes the hold point like any report — the plan-marker
  refusal face from BUG-001's fix is what caught the cursor bug mid-development); no
  real API call anywhere in this change.

## Change Focus

- **Primary module / causal owner:** `runtime/replay_fixture.py` — the journey-order
  model provider owns the replay semantics; the corpus tools and the fixture feed it.
- **Seam classification:** deterministic-guardrail + wiring — replay serving is a pure
  deterministic function over recorded facts with loud failure signals; no model,
  prompt, or lifecycle semantics are touched.
- **Question:** Can a recorded real journey (model journal + search corpus) drive the
  real framework graph to a completed, admitted, verbatim-identical report with zero
  credentials — with divergence signals that fail loudly instead of silently?
- **Necessary adjacent/external contracts:** the E issue card (answers: the recording,
  the corpus, the desensitization status, the acceptance receipts); `test-evidence`
  capability (answers: the level-3 ladder semantics the proof satisfies);
  `run-admission` (answers: the hold point and the plan-marker face the replayed report
  must pass); `fix-headless-plan-gate` (answers: the headless auto-confirm the replay
  journey exercises again).
- **Evidence seam:** the integration test itself — completed, gate lifecycle journaled,
  report verbatim, admitted, zero secret references; the full suites (`make verify`,
  `make smoke`) green with the new files; the development receipts (each replay failure
  was loud: ReplayMiss naming keys, the plan-marked rejection naming the face, the
  exhaustion error) recorded in the Delivery Record.
- **Not in scope:** an operator-facing replay configuration (test-lane wiring only; the
  config set is unchanged); key-based journey matching (measured unsuitable — see What
  Changes); subagent/delegation replay (the recorded journey had none); re-recording
  (the fixture is the existing acceptance run).
- **Triggered review policies:** change-admission, local-context
