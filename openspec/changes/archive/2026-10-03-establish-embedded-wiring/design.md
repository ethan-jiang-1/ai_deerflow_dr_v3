# Design

## Context

Verified this session by reading the framework's public surface (this change explicitly
owns that boundary per the deerflow-downstream policy):

- `DeerFlowClient.__init__(config_path, checkpointer, *, model_name, thinking_enabled=
  True, subagent_enabled=False, plan_mode=False, agent_name=None, available_skills=None,
  middlewares=None, environment=None)` — ten parameters, exactly the wiring plan's
  decision 1 list. `available_skills` is `set[str] | None` (None = all scanned skills).
- `StreamEvent(type: StreamEventType, data: dict)` with the docstring-pinned event
  families `values` (title, messages, artifacts, summary_text — no todos, confirming the
  plan), `messages-tuple`, `end`.
- The sync checkpointer factory: `SqliteSaver.from_conn_string(conn_str)` + `setup()`
  inside the framework's own provider — the plan's ~90% confidence is now source-confirmed.
- The `use:` seam is a generic class-path loader on configuration models — and the
  framework ships **no fake models**: the fixture's fakes must be harness-owned.
- The harness package dependency tree is heavy (langchain family, langgraph, langfuse,
  kubernetes client, extension contract pin). The application unit gate stays stdlib
  because CI installs nothing.

Decisions already ruled: plan_mode=False, subagent_enabled=True, explicit config_path,
sync saver, middleware injection = insertion (lead chain #32 slot; no error isolation —
the snapshot hook must be self-defending), clarification via bounded continuation.

Policy routing: `control-placement`, `workflow-outcome-review`, `change-admission`; the
deerflow-downstream policy governs the reading boundary this change owns. No StateGraph
transition/predicate is authored here — the engine consumes the framework's.

## Goals / Non-Goals

**Goals:**

- The embedded binding exists and is proven by a zero-credential smoke: multi-turn
  conversation, readable `checkpoint.sqlite` in the bundle.
- Every borrowed surface is mirrored and drift-tested; nothing framework-owned is copied.
- The run engine is terminal-honest and reuses the RUB-001 rules rather than re-deciding.

**Non-Goals:**

- No CLI (entry plan), no admission producers, no Langfuse enablement (recorded, not
  depended on), no HITL, no CI wiring of the integration lane (recorded gap), no
  modification of the framework.

## Decisions

1. **The unit gate stays stdlib; the framework lane is explicit.** Framework-dependent
   tests live in `tests/integration/` (no `__init__.py`, so the stdlib discovery never
   collects them) guarded by `skipUnless(deerflow importable)`, runnable via
   `make smoke` through the uv environment. Alternative (framework tests inside
   `make verify`) rejected: CI installs nothing, so `UV_OFFLINE=1 make verify` would
   fail on a fresh checkout — the honest gate cannot promise what the environment
   lacks. The skip reason names the requirement; the smoke's own green run is recorded
   in the apply receipts.
2. **The contract mirror is hand-written typed declarations compared by test**, not
   generated: the surface is ten parameters and four event families — generation
   machinery would exceed the mirrored reality. The test reads the real signatures via
   `inspect` and compares parameter names/kinds and event-family names against the
   mirror constants; a framework bump that drifts fails naming the surface. The
   binding module imports the framework lazily (inside its construction function), so
   mirror-constant and config-resolution logic stay unit-testable without the
   framework — the import-policy-relevant module boundary is unaffected.
3. **Fakes are harness-owned, minimal, and honest**: a fake chat model implementing the
   framework's model interface with scripted responses, and a fake search provider
   returning canned documents — placed under `runtime/fixtures/` and referenced by
   `config/fixture.yaml`'s `use:` seams. They run the real agent loop (real middleware,
   real checkpointer, real event stream) so the smoke proves the wiring, not a mock of
   it.
4. **The run engine is a library function, not a CLI surface**: `run_research(handle,
   binding, problem)` iterates the stream once, feeds `model_tool`/`subagent` journal
   entries, applies the RUB-001 terminal rules, performs the bounded continuation
   (re-invoking the client on the same thread with a provenance-marked
   `[非交互模式·系统自动应答]` reply), writes the unanswered-question file on
   exhaustion, and returns the terminal state. The pump's terminal rendering is the
   entry plan's job.
5. **The assembly snapshot middleware is self-defending** (the injection slot has no
   error isolation): the hook captures the system prompt and visible tools on the first
   round and swallows-and-journals its own failures into a `diagnostics/` error note
   rather than breaking the run — with the capture failure itself journaled loudly. The
   snapshot writes once per run (first model call), satisfying the RT2/RT7 closure.
6. **Configuration shape/secret separation follows the framework's example template**:
   `models[].use` + `api_key: $VAR` in `config/base.yaml`; the fixture swaps `use:` to
   the fakes and keeps `$VAR` references that never resolve in the fixture path
   (the fake model never reads keys). `base.yaml` explicitly sets
   `summarization.enabled: true` (the plan's pinned inconsistency fix).
7. **New structural paths register at apply time**: `runtime/contracts/`,
   `runtime/fixtures/`, `config/base.yaml`, `config/fixture.yaml` enter
   `required-paths.toml` under PRS-001 (with `directories` entries where needed),
   keeping the manifest's exact-enumeration promise.

## Alternatives

- **Framework tests inside the stdlib unit gate** — rejected: see decision 1; the gate
  would promise an environment CI does not materialize.
- **Generated mirror from introspection at build time** — rejected: the mirror's value
  is being visible, reviewable source; a generated artifact hides the surface it
  claims to lock.
- **Framework-shipped fakes for the fixture** — impossible: verified absent; our fakes
  also prove the `use:` seam accepts harness-owned providers (decision 3).
- **Async saver** — rejected (already ruled): the embedded client is a synchronous
  driver; the smoke would have exposed any async-saver feasibility, but the source now
  confirms the sync factory directly.
- **Gateway transport instead of embedded** — rejected (digest ruling): embedded is the
  decided shape; the gateway would reintroduce the transport layer v2 died of.

## Risks / Trade-offs

- [The heavy dependency tree may not resolve in every environment] → the smoke is the
  pinned experiment; its skip-guard and the explicit `uv sync` requirement keep the
  unit gate green everywhere while the smoke proves the wiring where the environment
  allows. Apply records the actual sync result.
- [Middleware hook exceptions can break the agent chain (no isolation at the slot)] →
  the snapshot hook is self-defending and journals its own failures (decision 5).
- [Fixture fakes drift from the real model interface] → the smoke runs them through the
  real client chain; an interface drift fails the smoke, and the contract test pins the
  model interface shape the fakes implement.
- [Snapshot captures the prompt but not future per-round changes] → accepted: the
  assembly is once-per-run by ruled decision; per-round changes arrive with the
  compaction middleware's own records.

## Migration Plan

Single apply, red-before-green per group: mirror/config tests red → engine modules
green; run-engine rule tests red → run engine green; governance registration; then the
smoke (the pinned experiment) with its result recorded honestly; verification sequence;
reviews; archive; commit. Rollback is reverting the edits; DEW-001 takes a retirement
marker if abandoned post-registration.

## Open Questions

(none at planning time — the smoke is the change's own pinned experiment: apply either
proves the embedded path or surfaces the concrete blocker, both of which satisfy the
plan's uncertainty-closure goal)
