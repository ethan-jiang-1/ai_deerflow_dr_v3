# Design

## Context

Verified this session: both checked-in configurations declare no `subagents` section at
all; the framework's native deep-research capability performs its own subagent
delegation through its scanned skills; the wiring plan's decision 5 pinned the
(b)-layer declaration location (config.yaml `subagents.*`) plus the depth self-check
(custom subagents must exclude the `task` tool — the framework schema does not enforce
it). The wiring change landed every other decision and the smoke proved the embedded
path. Policy routing: `change-admission` only — no control placement or failure-class
change.

## Goals / Non-Goals

**Goals:**

- Decision 5 lands as an explicit, guarded posture: the configurations say "no custom
  subagent types", and the `task`-exclusion self-check exists and is proven red-able.
- The last plan (wiring-structure) closes for a real reason, with the ledger ritual
  synced.

**Non-Goals:**

- No custom subagent type declarations (no consumer — the Context Expansion Gate
  applies), no runtime budget knobs, no framework-side change, no spec-level behavior
  change (hence `skip_specs: true`).

## Decisions

1. **Posture as comments in the configurations, not as an empty TOML-style section.**
   The frameworks's config loader treats unknown/empty sections as real input; a
   commented block records the decision without feeding the parser anything to
   misinterpret. The comment names the future path: an owning change declaring custom
   subagents must satisfy the depth self-check.
2. **The depth self-check is a unit guard over the checked-in files, not over the
   loader.** The test reads `config/base.yaml` and `config/fixture.yaml`, extracts any
   `custom_agents` declarations, and fails if any lacks `task` in its
   `disallowed_tools` (or lacks `disallowed_tools` entirely). Parsing is text-aware
   and dependency-free (the unit gate stays stdlib): a YAML parser is not guaranteed in
   the gate environment, so the guard matches the declared-block shape with a strict
   line scanner and — critically — proves itself via a negative control on a temp
   copy, not by trusting the happy path.
3. **The negative control is a committed test, not a one-off receipt**: a temp
   fixture writing a `custom_agents` entry without `disallowed_tools` must turn the
   guard red. This is the "a guard that cannot go red does not exist" discipline
   applied to a configuration guard.
4. **Plan closure rides the same change** (it is the change's purpose): after the guard
   lands, the wiring-structure plan's six decisions are all landed-or-dispositioned,
   so the plan moves to `_closed_plans/` as CLS-006 with the three-README ritual
   synced. The closure note records decision 5's disposition verbatim so a future
   reader sees why the knobs do not exist.

## Alternatives

- **Declare placeholder custom subagent types now** — rejected: a possible future use
  is not enough to expand scope (Context Expansion Gate); empty declarations would be
  structure with no consumer and would invite drift.
- **Declare nothing anywhere (skip the posture comments too)** — rejected: the silence
  is exactly what decision 5's self-check exists to prevent; an explicit posture keeps
  the next declarer on the guarded path.
- **A full OpenSpec change with a new capability for the posture** — rejected: no
  downstream behavior changes; `skip_specs: true` is the honest shape for a
  config-content + guard change, and inventing a requirement for it would violate the
  "do not invent a requirement" instruction.

## Risks / Trade-offs

- [The text scanner misreads a future hand-edited config format] → the guard fails
  closed (a parse surprise is a red, never a silent pass) and the negative control
  pins the failure mode; a YAML-syntax config change is an owning change anyway.
- [The posture comment rots away in an edit] → the guard test asserts the posture
  block's presence alongside the scan, so deleting the comment fails the suite.
- [Vacuous-true guard lulls a future declarer] → the negative control and the posture
  comment both name the exact future obligation; the guard's failure message repeats
  it.

## Migration Plan

Single apply: posture comments into both configs; guard + negative control into the
unit suite (red proven on a violating temp fixture, then green); run the verification
sequence; perform the ledger ritual (wiring-structure plan → `_closed_plans/` as
CLS-006, three READMEs synced); archive; commit. Rollback is reverting the edits; the
plan closure is reverted by moving the plan file back.

## Open Questions

(none — the disposition follows from the Context Expansion Gate applied to decision 5's
own declaration location)
