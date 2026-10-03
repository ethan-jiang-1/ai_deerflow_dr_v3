# Proposal

## Why

The harness has a deterministic substrate (RUB-001) and an acceptance closeout (RUA-001),
but no research capability: nothing has ever invoked DeerFlow. The wiring plan's decision
is to stop owning research cognition entirely — the embedded `DeerFlowClient` is the
research engine, and the harness becomes its deterministic wrapper. This change makes
that real and pins the last ~10% uncertainty the plan flagged: whether the embedded
client + sync `SqliteSaver` path actually works (multi-turn, checkpoint readable). It
also locks the borrowing risk the plan names: the framework drifts (submodules do),
so every surface we borrow gets a visible typed mirror plus a contract test.

## What Changes

- **Dependency becomes real**: `deerflow-harness` (editable path source already declared
  in `pyproject.toml`) enters `[project]` dependencies. The tree is heavy (langchain
  family, langgraph, langfuse, kubernetes client); the application unit gate stays
  stdlib-only — framework-dependent tests live in `tests/integration/` and run when the
  framework is importable, skipping loudly otherwise (the gate's `UV_OFFLINE=1` CI
  constraint is unchanged).
- **Contract mirror** (`runtime/contracts/`, plan decision 2): typed definitions of the
  surfaces we consume — client constructor parameters, `StreamEvent` shapes
  (`values` / `messages-tuple` / `custom` / `end`), and the checkpointer seam — plus a
  contract test comparing the mirror against the real signatures. The mirror is
  interface shape only; the implementation stays the framework's.
- **Client binding** (`runtime/client.py`): thin assembly of `DeerFlowClient` with
  explicit `config_path` (base or fixture, never framework auto-discovery),
  `checkpointer` = the bundle's sync `SqliteSaver` (framework's own sync factory,
  `from_conn_string` + `setup()`), `subagent_enabled=True`, `plan_mode=False`
  (plan-ruled), `available_skills=None` (full skill surface — transparency tenet;
  recorded as an autonomous call the user may veto), `middlewares=[assembly-snapshot]`.
- **Checked-in configuration** (plan decision 6): `config/base.yaml` (real run) and
  `config/fixture.yaml` (zero-credential rehearsal) with shape/secret separation
  (`api_key: $VAR`); the fixture's `use:` seams point at harness-owned fakes
  (verified: the framework ships no fake models — they must be ours) implementing the
  model/tool interfaces against the real client chain.
- **Run engine** (`runtime/run_engine.py`): the stream pump composing the three
  sinks — journal feed, terminal detection (dead-PID/clarification/stop-reason rules
  from RUB-001), and the bounded clarification auto-continue loop (client re-invocation
  on the same thread, bound N=2 from state.json, question text preserved to
  `diagnostics/`); terminates in the declared run-terminal outcomes.
- **Assembly snapshot** (plan decision 4's escape hatch, first use): a first-round
  middleware hook records the rendered system prompt and the visible tool list into
  `diagnostics/` once per run (the RT2/RT7 blind-spot closure).
- **Structural registration**: new paths (`runtime/contracts/`, `runtime/fixtures/`,
  `config/`) enter `required-paths.toml` per the architecture policy's synchronized-
  change protocol.

## Capabilities

### New Capabilities

- `deerflow-wiring`: owns the required behavior of the embedded binding — explicit
  config resolution, the contract mirror and its drift test, the assembly snapshot,
  and the run engine's terminal-honest stream consumption.

### Modified Capabilities

(none — the run engine composes existing run-bundle/admission behaviors; no RUB/RUA
requirement text changes)

## Impact

- New: `deep_research_harness/src/deerflow_deep_research/runtime/contracts/`,
  `runtime/client.py`, `runtime/fixtures/`, `runtime/run_engine.py`,
  `deep_research_harness/config/base.yaml`, `config/fixture.yaml`, tests under
  `tests/unit/` (mirror-only logic) and `tests/integration/` (framework-dependent).
- Modified: `deep_research_harness/pyproject.toml` (dependency), `Makefile` (a `smoke`
  target for the integration lane), `openspec/governance/required-paths.toml`
  (inventory entries), `openspec/governance/check_doc_hygiene.py` + docs index only if
  new docs-layer files appear.
- No CI workflow change (the integration lane is explicit, not CI-wired — recorded as
  the known gap it is), no spec-level project-structure change, no `deerflow/`
  modification — this change explicitly owns and approves source-reading the framework's
  public API surface for the contract mirror; it does not modify the gitlink.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/runtime/` — the
  client binding, contract mirror, and run engine are the semantic decision (how the
  harness is bound to DeerFlow and what it guarantees while consuming it).
- **Seam classification:** wiring — the changed behavior is composition and binding at
  the framework's public boundary; cognition itself is the framework's.
- **Question:** How does the harness bind to DeerFlow in-process — explicit config
  resolution, sync-saver checkpointing inside the bundle, a drift-locked contract
  mirror, and an honest terminal-state run engine — such that the smoke test proves
  multi-turn + readable checkpoints with zero credentials?
- **Necessary adjacent/external contracts:** the deerflow-downstream policy (answers: the boundary rules for reading the public
  API and pinning drift); the run-bundle store (answers: where the checkpointer,
  journal, and snapshot land and which liveness/CAS seams the run engine reuses);
  the admission validator (answers: what the run engine must NOT do — it produces
  proposals, it never admits); `required-paths.toml` (answers: the new structural
  paths' registration).
- **Evidence seam:** the unit suite via `make verify` (mirror logic, config resolution,
  run-engine rules with fakes at the domain boundary) plus the integration smoke
  (`make smoke`): embedded client + sync `SqliteSaver` multi-turn conversation with
  `checkpoint.sqlite` readable, zero credentials; the contract test comparing mirror
  versus real signatures.
- **Not in scope:** the six-subcommand CLI (entry plan), admission call-site wiring
  (producers arrive with entry/wiring consumers), Langfuse/tracing enablement
  (first version records it, does not depend on it), HITL, TUI.
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| Research cognition authority is delegated to the embedded DeerFlowClient; the harness owns only binding, observation, and terminal honesty | Human judgment (digest ruling: v2's hand-built research graph is retired; borrow the framework wholesale) | The contract test compares the mirror against the real signatures; the run engine's terminal rules are the RUB-001 pure functions | non-bypassable | A drifted framework surface fails the contract test naming the drift; the run engine cannot report a live-seeming terminal state (RUB-001 rules) | v2's hand-built graph, node adapters, and gateway transport are not carried; zero new transport mechanisms (journal is the only medium) | Contract test + integration smoke + unit suite via make verify |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| Framework surface drifted (signature/event shape changed) | Contract test | None — fail loud | Test fails naming the drifted surface | Update the mirror consciously via an owning change | Contract test comparing mirror versus real client |
| Run ends with an unanswered clarification beyond bound N=2 | RUB-001 detection predicate + state rule | Bounded continuation loop (client re-invocation, same thread) | `failed-resume`, question text preserved in `diagnostics/` | `refine` with direction text | Integration smoke: clarification scenario exercises the bound |
| Config mis-resolution (auto-discovery picks the wrong file) | Client binding (explicit `config_path`) | None — fail loud at construction | Error naming the missing/ambiguous config | Pass the intended path explicitly | Unit test: explicit path honored, default resolution refused |
| Framework import unavailable in an environment | Integration lane guard (`skipUnless` importable) | Skip loudly with the reason | Suite skips the smoke, naming the requirement | `uv sync` to materialize the environment | Skip reason recorded; smoke runs green in a synced environment |
