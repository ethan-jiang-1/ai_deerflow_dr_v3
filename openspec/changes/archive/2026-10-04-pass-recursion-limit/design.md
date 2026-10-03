# Design

## Context

client.py:293: `recursion_limit=overrides.get("recursion_limit", 100)` — the stream's
per-call overrides; the AppConfig key is not consumed by the embedded path (verified by
the failed re-run whose config edit never reached the stream). The guard makes the cap
loud; this change removes the cap. Policy routing: change-admission; skip_specs.

## Decisions

1. One seam: `make_stream_fn` in the binding builds every stream call and injects the
   limit; callers never hand-roll lambdas against the raw client.
2. 300 as a conservative start (framework max 1000); a still-capping run fails loudly
   under the guard and the number is adjusted on evidence.
3. The mirror notes the consumed stream kwarg (the constructor surface is unchanged).

## Alternatives

- Editing the framework — forbidden and unnecessary. - A global monkeypatch of the
  default — rejected: hidden mutation; the per-call seam is the framework's own knob.

## Risks / Trade-offs

[300 insufficient for heavier threads] → loud failure under the guard; adjust on
evidence (the limitation row tracks it).

## Migration Plan

Factory test red → factory + CLI swap green → live refine re-run completes → receipts
→ archive → commit.

## Open Questions

(none)
