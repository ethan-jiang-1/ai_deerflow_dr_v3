# Design

## Context

See proposal.md. The checker (`check_proof_receipts.py`, unchanged) defines the exact
schema its own self-test uses: `version = 1`, `[[lane]]` with `name`, `command`, `cwd`,
`tier`, `sentinel`, `surfaces`; receipts are evaluated only when an attestation names a
selected committed range. Today no attestation flow exists, so the checker is dormant.

## Goals / Non-Goals

**Goals:** the checker's registry dependency is satisfied by a real, schema-correct
file; every reachable failure is a named lane report; the structural manifest declares
the new file.

**Non-Goals:** receipt producer (`make proof`), attestation generation, checker or gate
changes, CI changes.

## Decisions

1. **Two lanes, real standing surfaces.** `verify` covers `deep_research_harness/src/**`
   plus `deep_research_harness/tests/**` (the unit gate's subject); `smoke` covers
   `deep_research_harness/tests/integration/**` and `deep_research_harness/cli.py`
   (the integration journey's subject). Sentinels are the completion lines the playbook
   already defines (`[verify] harness unittest gate passed.` and the smoke suite's OK
   verdict), so a future receipt producer can be validated against real command output.
   Alternative rejected: one broad lane (loses the verify/smoke distinction the
   evidence policy draws).
2. **Commands mirror the canonical lanes.** `make verify` (cwd `deep_research_harness`)
   and `make smoke`; the registry records intent for a future producer, it executes
   nothing itself.
3. **No checker change.** The self-test already proves the schema; adding a real
   registry cannot invalidate it, and `evaluate()` is reachable only via attestation.

## Risks / Trade-offs

- [First attestation flow fails on missing receipts] → intended: loud, lane-named,
  with rerun hints; the producer lands with the change that adopts the flow.
- [Registry drifts from real lane semantics] → surfaces/sentinels are checked into
  the manifest-guarded tree; drift is a visible diff, and the owning spec owns semantics.

## Migration Plan

One file plus one inventory entry; rollback is revert.

## Open Questions

None.
