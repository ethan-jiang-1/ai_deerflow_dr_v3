# Design

## Context

The recursion arc: config-only fix did not reach the stream (per-call override at
client.py:293); the seam fix landed make_stream_fn; the smoke still hand-rolled its
own lambda. Policy routing: change-admission; skip_specs (conformance to the declared
terminal-honesty/lane requirements — no new normative behavior).

## Decisions

1. CONSUMED_STREAM_KWARGS pinned in the mirror (thread_id, recursion_limit) with the
   provenance comment (client.py:293).
2. The smoke's stream_fn comes from make_stream_fn — the single seam, behaviorally
   exercised by every smoke run.
3. A unit assertion pins the factory's injection (exists) + the mirror constant
   (new).

## Alternatives

Introspecting **kwargs — impossible (the limit rides kwargs); a signature change in
the framework — forbidden (upstream surface).

## Risks / Trade-offs

[The kwarg name drifts upstream] — the smoke fails loudly (the limit stops applying →
GraphRecursionError under the guard), naming the seam.

## Migration Plan

Mirror + smoke swap red-green; receipts; archive; commit.

## Open Questions

(none)
