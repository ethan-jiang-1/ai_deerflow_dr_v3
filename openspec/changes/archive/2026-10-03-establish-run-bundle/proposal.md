# Proposal

## Why

The harness has no implementation yet, and everything the entry surface and the embedded
wiring will stand on is the Run Bundle substrate: where a run's durable record lives, who
owns run state, and how the run's history is observed. The debugger is a user-level hard
requirement — watch, journal, and checkpoint replay must be usable from day one — and v2's
hardest lessons (journal O(n²) rewrites, silent migration, unowned state) are recorded
against exactly this substrate. The bundle plan's decisions 1/2/3/5/6 are fully polished
(zero UNVERIFIED, all threads closed), the release sequence is user-ruled (graph-grammar
removal first, this second, wiring third), so the first product change lands the
substrate.

## What Changes

- New `run-bundle` capability (RUB-001), implemented as pure deterministic harness code:
  - **Directory contract**: a run bundle lives at `scopes/{bucket}/{bundle_id}/` with the
    subtrees `request/`, `work/`, `evidence/`, `final/`, `diagnostics/` plus
    `state.json`; the v2 `synthesis/` and `review/` subtrees are not carried over (the
    research cognition engine is DeerFlow's). `checkpoint.sqlite` location is declared in
    the contract with a fail-loud open policy; the file itself is created by the run
    engine in the wiring change. Path constants live in one pure domain module.
  - **State machine** (pure transition rules + runtime action layer): actions
    `start`/`status`/`cancel`/`refine`; states `active`/`completed`/`cancelled`/
    `failed-resume` (v2's suspended/blocked die with HITL deferral). `state.json` is the
    single truth with revision CAS; every write revalidates a directory lease
    (`st_dev`, `st_ino`). Crash detection: `status` on an `active` bundle whose owner PID
    is dead transfers to `failed-resume` — fail-loud, never pretend-alive. Clarification
    continuation state (`auto_proceed_count`, bound N=2) and the unanswered-
    `ask_clarification` detection predicate land as pure functions; the client re-invocation
    loop itself lands with the wiring change.
  - **Journal** (`diagnostics/journal.jsonl`): append-only with the eight start-up
    categories (`admission`, `lifecycle`, `model_tool`, `subagent`, `validation`,
    `submit`, `exhaustion`, `terminal`) as a small closed set; bounded retention with
    priority eviction where `admission` anchors are never evicted; periodic compaction
    that preserves anchors plus the recent tail; a corrupted tail fails loudly instead of
    pretending.
  - **Deletion semantics**: no registry (discovery is directory scanning), deletion is
    permanent with no recovery path, and write paths re-verify liveness.
  - **Explicit composition** recorded in `state.json` at start (`fixture`/`mixed`/
    `all_real`).
- `make verify` becomes real: the harness unittest suite (stdlib only, zero external
  dependencies, offline-safe — the CI job has no dependency-install step, so the gate
  must run on bare `python3`), replacing the loud stub; `make install` gains the matching
  honest no-op shape. The Verification sections of the harness guide, `COMMANDS.md`, and
  `docs/testing-and-evaluation.md` (lane division) are updated to match.
- Explicit scope boundary (bundle plan decision 4 is its own next change): the
  validator / hash-chain ledger / gate admission machinery is NOT in this change — the
  journal reserves the `admission` category so anchors can exist before the ledger does.
  CLI surfaces (entry plan) and the embedded client (wiring plan) are out of scope.

## Capabilities

### New Capabilities

- `run-bundle`: owns the required behavior of the run bundle substrate — the declared
  directory contract, the single-authority state machine with CAS and lease liveness,
  crash detection and bounded clarification-continuation state, the bounded honest
  journal, deletion semantics, and the recorded composition.

### Modified Capabilities

(none)

## Impact

- New: `deep_research_harness/src/deerflow_deep_research/domain/` (bundle path
  constants, typed state/transition/journal contracts, pure transition and detection
  functions) and `deep_research_harness/src/deerflow_deep_research/runtime/` (atomic
  file layer, CAS state writer, lease check, journal appender, action implementations);
  tests under `deep_research_harness/tests/unit/`.
- Modified: `deep_research_harness/Makefile` (verify becomes the unittest gate, install
  keeps its honest no-op), `deep_research_harness/AGENTS.md` (Verification section),
  `deep_research_harness/COMMANDS.md`, `deep_research_harness/docs/testing-and-evaluation.md`.
- No governance registration changes (the new code lives in already-declared layers; the
  manifest inventory needs no new entries), no CI workflow change, no new external
  dependencies, no `deerflow/` contact — ordinary downstream work neither modifies nor
  source-browses the `deerflow/` gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/domain/` — the bundle
  directory contract, the typed state machine facts, and the pure transition/detection
  rules are the semantic decision this change makes; runtime only materializes them.
- **Seam classification:** deterministic-guardrail — every changed behavior is a
  machine-checked deterministic rule (transition legality, CAS, lease, eviction,
  fail-loud openings); no model cognition is involved.
- **Question:** How does the run bundle substrate come into existence as pure
  deterministic code — directory contract, single-authority state machine with CAS and
  lease liveness, crash detection, bounded journal with protected anchors — such that
  the entry surface and embedded wiring can stand on it without rework, and every
  failure path fails loudly in human-readable terms?
- **Necessary adjacent/external contracts:** `src/deerflow_deep_research/runtime/` (answers: how the pure rules are materialized as
  atomic file operations without runtime importing the engine layer — the import policy
  pins pure rules in domain); `deep_research_harness/Makefile` + `docs/testing-and-evaluation.md` +
  `deep_research_harness/AGENTS.md` (answers: what the first test-bearing gate promises
  and how the lanes are divided); `openspec/governance/required-paths.toml` (answers: whether new
  source files need registration — they do not, the layers are already declared).
- **Evidence seam:** the harness unittest suite under `tests/unit/` run by `make verify`
  (stdlib, offline), with negative controls for CAS conflicts, lease mismatch, dead-PID
  transfer, anchor-surviving eviction, and illegal journal categories.
- **Not in scope:** validator/hash-chain ledger/gate admission machinery (bundle plan
  decision 4 — next change; journal reserves the `admission` category), CLI subcommands
  (entry plan), the embedded client and real checkpoint writes (wiring plan), HITL
  surfaces, checkpoint format wrapping, pytest/ruff as gate dependencies, and the
  proof-lanes file.
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| Run lifecycle authority is placed in the state machine over `state.json` as the single truth; no competing controller exists | Human judgment (bundle plan decision 2: plain state machine, single-authority state, v2 CAS+lease discipline kept) | Transition legality, CAS, and lease liveness are pure domain rules; the runtime layer is their only writer | non-bypassable | A state mutation that skips the CAS, lease, or legality check fails loudly naming the violation; `state.json` cannot be bypassed as the authority | v2's suspended/blocked states and HITL machinery are not carried; the O(n²) journal rewrite is replaced by append + compaction | Harness unittest suite via make verify; negative controls for CAS conflict, lease mismatch, dead-PID transfer |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| Owner PID dead while state says `active` | `status` action (liveness check) | `status` itself, bounded to one transfer per observation | `failed-resume` (fail-loud), journal `terminal` entry | `refine` (new generation) or `inspect` | Unit test: dead-PID fixture transfers and journals the reason |
| Clarification continuation exhausted (bound N=2) | Detection predicate (pure domain function) | The bounded continuation loop (state fields land here; client re-invocation lands with wiring) | `failed-resume`, unanswered question text preserved in diagnostics | `refine` with direction text | Unit test: predicate + exhaustion transition on the pure layer |
| Bundle directory replaced or moved under a writer | Lease check (`st_dev`, `st_ino`) before every write | Write refuses; no repair attempted | Write fails loudly naming the lease mismatch | Re-discover the bundle by scanning | Unit test: lease mismatch rejects the write |
| Journal tail corrupted | Journal reader (append + read path) | Reader fails loudly; never silently truncates | Error naming the corruption site | Repair is manual and visible (human-readable file) | Unit test: corrupted tail fails the read |
| Deleted bundle accessed afterwards | Directory scan (no registry) | None — deletion is permanent | Loud "permanently unavailable" report | Nothing (by design; no recovery path) | Unit test: post-deletion status reports unavailability |
