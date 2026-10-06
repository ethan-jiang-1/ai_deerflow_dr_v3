# Spec Delta

## ADDED Requirements

### Requirement: The approved research plan is materialized as a request artifact

When a plan gate confirms or amends a proposed research plan, the engine SHALL
materialize the plan text atomically at `request/plan-gen1.md` before the research
turns begin — the user-confirmed scope contract is a durable request artifact, not
only a journal entry. A skipped, aborted, or degraded gate SHALL create no plan
file. The artifact follows the bundle's deletion semantics and joins the artifact
ownership map alongside `problem.txt` and the refine direction documents.

#### Scenario: Confirmed plan lands as a request artifact

- **WHEN** the plan hook returns a plan string (confirmed or user-amended)
- **THEN** `request/plan-gen1.md` exists with that text before the research turns,
  and the journal carries the proposal and decision events

#### Scenario: Skip and degradation write no plan file

- **WHEN** the plan hook returns None, the hook raises, or the first turn researches
  despite the framing
- **THEN** no `request/plan-gen1.md` is created, and the decision (or degradation) is
  journaled
