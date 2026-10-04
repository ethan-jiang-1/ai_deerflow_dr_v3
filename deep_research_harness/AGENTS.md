# Deep Research Coding Guide

This file is the self-contained code-change map for `deep_research_harness/`. The
application does not depend on the repository's development-governance framework.
`deerflow/` is a read-only upstream runtime framework: use its public API, never modify
or source-browse it for ordinary application work.

v3's research cognition engine is DeerFlow's native deep research capability (lead agent
+ `deep-research` skill + subagent delegation), and the harness keeps the deterministic,
inspectable parts. The `agents/` layer is the one still-empty owner (see Non-Model Work);
the other ownership boundaries are binding today.

## Application Focus

Select one primary causal owner. Start with its closest implementation and lowest
responsible test seam; widen only for a named interface, authority, compatibility, or
observed-failure question. A possible future use is not enough to expand scope.

| Changed decision | Primary application owner | Try first; escalate when |
| --- | --- | --- |
| Typed meaning, invariant, or pure data contract | `src/deerflow_deep_research/domain/` | A plain typed value first; escalate only when the typed contract itself must change |
| Deterministic validation, gate, or admission policy | `src/deerflow_deep_research/engine/` | A pure function at the owning layer first; escalate when the admission needs a kernel seam |
| Bounded model role, prompt, context, or candidate | `src/deerflow_deep_research/agents/` | The framework's own agent/skill configuration first; escalate when a harness-owned bounded policy is required |
| Composition, routing, or capability injection | `src/deerflow_deep_research/runtime/` | The framework's own assembly knobs first; escalate when a harness-owned composition seam must change |
| DeerFlow binding, trusted I/O, persistence, or lifecycle adapter | `src/deerflow_deep_research/runtime/` | A thin adapter at the framework's public boundary first; escalate when a trusted lifecycle seam must change |

## LLM-Node Authoring Gate

For a Coding Agent creating, changing, or reviewing an LLM-bearing node or direct
model branch, use this route before implementation navigation. Never infer the seam
from the first file found or from presence or absence of a model call.

This section is the complete application-owned cognition-versus-code contract: the
numbered route below plus the explicit Non-Model Work branch.

1. **Classify the surface** as `cognitive-program`, `deterministic-guardrail`,
   `human-decision`, or `wiring`. A model-bearing behavior symptom reaches cognition
   first unless rejected with a causal rationale; non-model work fabricates no prompt.
2. **Node Cognitive Control Contract and local capability**: read the owning contract;
   state the bounded cognitive responsibility, useful candidate,
   uncertainty/degradation posture, and what the model cannot decide.
3. **Prompt builder and model-visible context**: inspect the exact builder;
   distinguish trusted assignment and output-contract input from delimited untrusted
   content; name the requested method/tool posture and its runtime enforcer. A prompt
   cannot grant tools, permissions, writes, routes, retries, or result acceptance.
4. **Structured output, feedback, and repair**: trace candidate shape, feedback source
   and recipient, repair bound, and stop condition. Feedback is data, not authority to
   widen the task, select a route, or admit an effect.
5. **Focused proof and applicable cognitive evaluation**: use the lowest deterministic
   composition/admission proof, then state the cognitive evaluation and its limitation.
6. **Deterministic handoff owners**: only then inspect parser, evaluator/materializer,
   ledger, gate, and other owners that admit legal effects and choose observable
   behavior.

## Where These Decisions Live

| Question | Application-owned first read |
| --- | --- |
| What may a bounded cognitive role think about and return? | The owning contract in `src/deerflow_deep_research/agents/` |
| What proves composition/admission? | The closest unit/contract test for that owner |
| Who admits state, routes, and effects? | The `engine/` and `runtime/` owners behind it |

The bounded-role contracts live with their owning code as it lands; this table stays
layer-level and must not invent file paths that do not exist.

## Non-Model Work

For deterministic, human-decision, or wiring work without a causal model-bearing
symptom, begin at the actual typed/domain/control/adapter owner and record why
cognition is not causal. Do not invent a capability, prompt, or repair loop.

## Information Map

| Need | Read first |
| --- | --- |
| Product use, quick start, commands and targets | [`README.md`](README.md), [`COMMANDS.md`](COMMANDS.md), [`Makefile`](Makefile) |
| Runtime and authority boundaries | [`docs/runtime-architecture.md`](docs/runtime-architecture.md) |
| Local commands and profiles | [`docs/local-operations.md`](docs/local-operations.md) |
| How do I prove a change (lanes, receipts)? | [`docs/testing-and-evaluation.md`](docs/testing-and-evaluation.md) |
| Documentation index | [`docs/README.md`](docs/README.md) |

## Boundaries

- Keep current facts in owning code, typed contracts, tests, checkpoints, ledgers, or
  content authorities. A guide, summary, or diagnostic is not a second authority.
- Keep blocking I/O off the async event loop.
- Keep application tests and build commands independently runnable from this directory.
- Do not add nested `AGENTS.md` files or copy this guide into `CLAUDE.md`. The
  prohibition prevents subtree entries created for their own sake; a sublayer that
  accumulates three or more standing rules only that layer needs re-opens the
  subtree-entry question through its owning change.

## Verification

`make verify` is the application unit gate: the stdlib unittest suite under `tests/`
(`PYTHONPATH=src`, zero external dependencies, offline-safe). It exits non-zero on any
failure and never reads, imports, executes, or links OpenSpec content. Lane separation
is explicit: `tests/integration/` is exercised by `make smoke`, not by `make verify`.

## Structural Authority

The active `project-structure` spec owns structural requirements; exact inventory
lives in the structure registry. Do not edit the generated block below by hand;
update the owning change and registry, then re-render with the architecture checker.

<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->
## Canonical Structure Locator

Exact inventory: the structure registry declared by the owning `project-structure` spec.

- Source root: `deep_research_harness/src/deerflow_deep_research/`
- Test root: `deep_research_harness/tests/`
- Ownership layers: `runtime`, `domain`, `engine`, `agents`
- Validate: repository architecture governance (`check_project_architecture.py`)
<!-- END GENERATED: PROJECT-STRUCTURE -->
