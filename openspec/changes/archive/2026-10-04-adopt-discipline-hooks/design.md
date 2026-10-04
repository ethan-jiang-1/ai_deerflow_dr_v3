# Design

## Context

The doctrine doc landed with the strategy/ladder/queue; A4's command-surface guard is the newest backing gate. The three philosophy items come from digest 04 (evidence over a green check) + 09 (no-cov); the crash idiom from 07.

## Decisions

1. Philosophy paragraphs live in the doctrine doc's new discipline subsections — each names its backing gate.
2. Dev-dep why-comments in pyproject (B4) — one line per dev dep.
3. The as-if-restarted idiom is documented as the crash-simulation pattern for run-engine tests (already used by the dead-PID test).

## Alternatives

Landing these inside the replay-model change — rejected: mixing guidance with machinery muddies both.

## Risks / Trade-offs

[Doctrine doc grows past attention span] — doc hygiene budgets the entry layer; the doctrine doc is docs-layer (link/encoding rules), size acceptable.

## Migration Plan

Doc + pyproject edits -> hygiene/closeout green -> receipts -> archive -> commit.

## Open Questions

(none)
