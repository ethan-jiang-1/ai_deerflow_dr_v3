# Design

## Context

The stand-in ladder's level 2 per the digest: per-caller + normalized-input SHA-256
indexing (not turn-indexing — callers interleave), normalization stripping volatile
content, and the system prompt EXCLUDED from the key (a frequently-edited detail, not
the contract). The miss discipline: loud, with the known-hash list and an input
preview. v3 is single-caller single-thread — the caller dimension simplifies but the
mechanism stays general.

## Decisions

1. Key = sha256(canonical normalized messages) — messages minus system roles, minus
   volatile substrings (ISO dates, UUIDs, system-reminder blocks); output recorded
   verbatim.
2. Recording wrapper is composition (holds the real model), not inheritance — the
   real model comes from the framework's own resolve seam.
3. Misses raise ReplayMiss with the known-key list + an 800-char input preview;
   never silent.
4. The replay model serves content verbatim from the fixture — no synthesis.

## Alternatives

Turn-indexed replay — rejected (callers interleave; order is not the contract).
Hashing the system prompt — rejected (prompt edits would invalidate every fixture).

## Risks / Trade-offs

[Normalization misses a volatile source] — the miss list surfaces it immediately
(loud); rules extend on evidence. [Fixture bakes one model's phrasing] — accepted:
the fixture pins the recorded run; re-record via the committed recorder.

## Migration Plan

Unit tests red -> implementation green -> real recording run -> replay test green ->
receipts -> archive -> commit.

## Open Questions

(none)
