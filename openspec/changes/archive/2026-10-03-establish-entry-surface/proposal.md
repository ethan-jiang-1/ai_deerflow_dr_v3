# Proposal

## Why

The harness now has a complete deterministic interior — bundle substrate (RUB-001),
acceptance closeout (RUA-001), and the embedded DeerFlow binding (DEW-001, smoke-proven)
— but a human still cannot start, observe, or follow up a research run: there is no
command surface. The entry plan's debugger-first requirement makes this the moment the
three observation layers (live view, journal timeline, checkpoint replay) must become
usable by a person, with the two-ladder rehearsal (fixture first, real later) intact.

## What Changes

- **Six-subcommand CLI** (`deep_research_harness/cli.py`, standalone consumer script —
  `python cli.py <command>`; placement rationale recorded in design):
  - `create "研究问题…" [--config base|fixture]` — starts a bundle (fixture default:
    zero-credential safety) and drives the run engine in the foreground with the live
    human view (single pump; journal + terminal rules unchanged).
  - `status <bundle_id>` — state, journal tail summary, owner-PID liveness (crash
    transfer happens exactly as RUB-001 declares).
  - `watch <bundle_id>` — journal tail projection, near-real-time; exits when the run
    reaches a terminal state (the bounded tail).
  - `cancel <bundle_id>` — records the cancellation request via the state machine.
  - `refine <bundle_id> "方向文本"` — generation+1 re-run entry.
  - `inspect <bundle_id>` — journal timeline, admitted evidence (ledger), assembly
    snapshot, and (framework available) the checkpoint thread summary.
- **Shared human renderer** (`runtime/render.py`): one formatting vocabulary for both
  the live view and the journal projection (人话摘要; deterministic strings so the
  tests pin the exact human-readable output). The run engine gains an optional
  `on_event` hook — the renderer sink joins the existing three sinks without changing
  their rules.
- **Two-ladder selection**: `--config fixture` (default) runs the real chain over the
  scripted providers; `--config base` is the real run (credentials via `$VAR`).
- **EV2 evidence**: a CLI journey integration test (create → watch → status → refine →
  inspect over the fixture ladder) plus a recorded replay golden (the
  clarification-exhaustion run recorded as JSON, replayed through the renderer with
  shape-stable assertions).
- **`known-limitations.md` activates** (the reserved docs slot): first entry records the
  framework's LLM-error-fallback behavior surfaced by the wiring smoke — a product-level
  known limitation, honestly listed for the non-AI handover.

## Capabilities

### New Capabilities

- `entry-surface`: owns the required behavior of the human command surface — the six
  verbs' semantics, the shared human rendering, the bounded watch, the two-ladder
  selection, and the inspect view.

### Modified Capabilities

(none — the commands compose existing run-bundle/admission/wiring behaviors through
their public actions; no RUB/RUA/DEW requirement text changes)

## Impact

- New: `deep_research_harness/cli.py`, `runtime/render.py`, tests
  (`tests/unit/test_entry_surface.py`, `tests/integration/test_cli_journey.py`),
  the recorded golden (`tests/fixtures/recorded/clarification-exhaustion.json`),
  `deep_research_harness/docs/known-limitations.md`.
- Modified: `runtime/run_engine.py` (optional `on_event` hook — no rule changes),
  `deep_research_harness/Makefile` (convenience targets), `deep_research_harness/docs/testing-and-evaluation.md`
  (CLI lane), `docs/README.md` + `openspec/governance/check_doc_hygiene.py`
  (known-limitations registration), `openspec/governance/required-paths.toml`
  (cli.py under ENS-001).
- No CI workflow change, no new external dependencies, no `deerflow/` contact beyond
  the already-owned public-API reading boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/cli.py` — the command
  surface owns what a human can ask the harness to do and what they see back; every
  command delegates to existing runtime actions and adds no second authority.
- **Seam classification:** wiring — the changed behavior is composition and human
  I/O at the boundary; all semantics already live in domain/engine/runtime.
- **Question:** How does the six-verb command surface expose the existing substrate —
  one pump with the live view as the fourth sink, a bounded watch over the journal
  projection, and an inspect view over the recorded facts — while every command
  remains a thin delegation that cannot bypass the state machine or the hold point?
- **Necessary adjacent/external contracts:** `runtime/render.py` + the run engine's `on_event` hook (answers: how the live view and the journal
  projection share one rendering vocabulary without the CLI owning semantics);
  the run-bundle actions (answers: why the commands cannot bypass CAS/lease/hold-point
  discipline); `docs/known-limitations.md` (answers: where the
  handover-visible limitations live, starting with the wiring smoke's finding); `openspec/governance/required-paths.toml` (answers: the CLI file's registration).
- **Evidence seam:** the unit suite via `make verify` (renderer strings, command
  parsing, watch bounded-tail logic with negative controls) plus the integration
  journey (`make smoke` extended): the full create→watch→status→refine→inspect path
  over the fixture ladder, and the recorded golden replay.
- **Not in scope:** TUI, daemon/background workers (ruled out), checkpoint-write
  changes, admission producers, Langfuse enablement, output internationalization.
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| The human boundary is six thin verbs over the existing actions; the CLI owns presentation only and cannot mutate state outside the state machine | Human judgment (entry plan: minimal CLI, one verb one action) | Every command delegates to runtime actions; the journey test walks the real path; renderer strings are pinned by tests | non-bypassable | No command path skips CAS, lease, hold point, or terminal rules; unknown commands and unknown bundles fail loudly naming the reason | v2's twelve-command theater, TUI trio, and debugger workbench are not carried; one script, one renderer, zero new transport | Journey integration test + renderer unit tests via make verify; recorded golden replay |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| Command targets a missing/deleted bundle | Runtime actions (BundleUnavailable) | None — permanent by RUB-001 | Loud human-readable unavailability report | Start a new bundle | Unit test: deleted bundle reports permanent unavailability |
| `refine` on a non-terminal bundle | State machine rule | None — rejected at the rule | Rejection naming state/action/reason | Wait for a terminal state or `cancel` | Unit test: refine on active is refused |
| `watch` on an already-terminal run | Watch bounded tail | Exits after rendering the terminal entry | Renders history and exits cleanly | `inspect` for the full view | Unit test: watch exits on terminal entry |
| Live run's framework call fails (LLM-error fallback) | Framework (error-fallback message) + journal | Owner records the fallback as a known limitation; no silent repair | Run completes with the fallback message visible in the renderer/journal | `refine` or manual follow-up | Golden replay pins the rendered shape |
