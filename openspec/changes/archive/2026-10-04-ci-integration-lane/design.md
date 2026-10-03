# Design

## Context

The checker pins CI declarations by markers; the gov unittest suite validates the pair
against the real files (and its own fixtures). The smoke lane is zero-credential.
skip_specs: the ci-governance spec's mechanism requirements are unchanged; only the
declared step list grows.

## Decisions

1. `make smoke` owns its environment: `uv sync` then `uv run --no-sync` (local warm
   cache, CI cold).
2. setup-uv pinned action; the smoke step follows the unit gate in the same job.
3. Markers move as a trio: workflow + checker required list + the gov test fixture.

## Alternatives

Separate workflow — rejected (single-job discipline). --no-sync only — rejected (cold CI).

## Risks / Trade-offs

[First pushed run may surface CI-only quirks] — UNVERIFIED-until-push, stated honestly.

## Migration Plan

Trio edit → gov suite + closeout green → receipts → archive → commit.

## Open Questions

(none)
