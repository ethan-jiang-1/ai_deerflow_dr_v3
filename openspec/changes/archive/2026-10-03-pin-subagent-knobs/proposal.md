# Proposal

## Why

The wiring plan's decision 5 ruled that any research subagent type declaration lands in
the checked-in configurations (`subagents.*` sections) with a mandatory depth
self-check (a custom subagent must exclude the `task` tool, which the framework schema
does not enforce). The wiring change landed decisions 1/2/3/4/6/8 and the smoke proved
the embedded path; the one open item is decision 5's landing. Reality checked this
session: DeerFlow's native deep-research capability already owns subagent delegation,
and v3 declares no custom subagent types — so the honest landing is an explicit
posture plus a mechanical guard, not invented knobs.

## What Changes

- **Explicit posture in both checked-in configurations** (`config/base.yaml`,
  `config/fixture.yaml`): a commented `subagents:` block stating that v3 declares no
  custom subagent types (the framework's native delegation covers the research need),
  and that a future declaration must arrive through an owning change and satisfy the
  depth self-check.
- **The depth self-check as a guard test** (RUB-era discipline: every declared custom
  subagent must carry `task` in its `disallowed_tools`): the unit suite gains a test
  that reads the checked-in configurations and fails if any declared custom subagent
  lacks the exclusion — plus a negative control proving the guard goes red on a
  violating fixture. Today the check is vacuously true (no custom subagents exist);
  the guard's value is that it can never silently stop being true when one appears.
- **Plan closure**: the wiring-structure plan's six decisions are then fully landed or
  explicitly dispositioned, so the plan closes as CLS-006 per the ledger ritual (three
  READMEs synced). `_backlog/plans/` becomes empty — the whole digest-derived plan
  family is consumed.

## Capabilities

### New Capabilities

(none — this change declares the posture the wiring plan already ruled and adds a
config-content guard; no downstream behavior changes, so the change opts out of specs
via `skip_specs: true`)

### Modified Capabilities

(none)

## Impact

- Modified: `deep_research_harness/config/base.yaml` + `config/fixture.yaml` (commented
  posture block), `deep_research_harness/tests/unit/test_subagent_posture.py` (new
  guard + negative control).
- No application behavior change, no governance registration changes, no CI workflow
  change, no `deerflow/` contact.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/config/` — the checked-in
  configurations are where the wiring plan pinned the (b)-layer declaration; the
  posture is a fact about them.
- **Seam classification:** deterministic-guardrail — the guard is a machine check over
  configuration content; no model cognition is involved.
- **Question:** How does decision 5 land when the honest answer is "declare nothing" —
  such that the nothing is explicit, the future declaration path is guarded (the
  `task` exclusion cannot be forgotten), and the last plan closes for a real reason
  rather than by attrition?
- **Necessary adjacent/external contracts:** the unit suite (answers: where the depth
  self-check lives and how its negative control proves it red); the wiring plan's
  decision 5 + ledger ritual (answers: what the plan closure records and which three
  READMEs must agree).
- **Evidence seam:** the unit suite via `make verify` — the posture assertions and the
  guard's negative control (a violating temp fixture turns the check red).
- **Not in scope:** declaring any custom subagent type (no consumer exists — the
  Context Expansion Gate forbids future-use scope), subagent runtime budget knobs, any
  framework-side change.
- **Triggered review policies:** change-admission
