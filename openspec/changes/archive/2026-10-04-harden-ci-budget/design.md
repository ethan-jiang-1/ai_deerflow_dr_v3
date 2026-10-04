# Design

## Context

The checker pins CI declarations by markers; the gov fixture is the third copy. The smoke lane extended runtime without a ceiling. Policy routing: change-admission; skip_specs.

## Decisions

1. Concurrency group per branch ref (cancel-in-progress) — superseded runs stop burning minutes.
2. timeout-minutes: 30 (current runtime 39s; 30 is a generous ceiling that still bounds a hang).
3. Markers move as the trio (workflow + checker + fixture) — the established pattern.

## Alternatives

Per-step timeouts — rejected (job-level is the declared budget; step-level adds noise).
No budget — rejected: an unbounded hung CI contradicts the fail-loud culture.

## Risks / Trade-offs

[Legitimately long future lanes hit the ceiling] — the budget is a declared contract; raising it is an owning change with evidence.

## Migration Plan

Trio edit → gov suite + closeout green → receipts → archive → commit.

## Open Questions

(none)
