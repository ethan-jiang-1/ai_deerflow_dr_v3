# Design

## Context

Read this session: the test-strategy digest (00 overview map with 四类22层 + per-layer 不证明什么; 01 doctrine — TDD mandatory / offline-first / live triple-gate / scar-tissue / docs-as-contract; 02 the four-level stand-in ladder with content-addressed replay; 03 anti-fake-green cross-stack replay; 04-09 skimmed). Our assets already match the doctrine's skeleton; the gaps are named below.

## Decisions

1. Doctrine lands in the existing app-side doc (not a new file) — it is the doc the config rules already route "怎么测" questions to.
2. The lane table gains 不证明什么 per lane (the digest's most informative pattern: a layer's value includes what it admits it does not prove).
3. The borrow queue is two changes, not five: replay (highest value — converts real-run evidence into permanent fixtures) and skill-testing surface (serves skill customization). Explicitly NOT borrowed yet: duration sharding (90 tests), Playwright tiers (no frontend), monocle (eval stack), and the framework's own journal/run-manager test patterns (our bundle owns those semantics).

## Alternatives

A new standalone doctrine file — rejected (doc proliferation; the config rules already route here). Verbal-only assessment without a durable doc — rejected (that is the 反复唠叨 the user named).

## Risks / Trade-offs

[Doctrine doc rots] — the doc is doc-hygiene-registered and the borrow queue lives in the ledger (both green-gated).

## Migration Plan

Doc upgrade → plan card → gates → receipts → archive → commit. The queued changes follow as separate changes.

## Open Questions

(none)
