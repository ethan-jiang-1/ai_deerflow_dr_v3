# Proposal: Land Proof Lane Registry

## Why

`check_proof_receipts.py` (a closeout gate component, enforce mode) hard-codes
`deep_research_harness/proof-lanes.toml` as its lane registry, but that file has never
existed — a `ReceiptError` traceback is latent at the first selected-change closeout
that supplies an attestation. The delivery-lanes apparatus was described as landed
(the audited "half-landed device", finding B11 of
`_backlog/_done/_closed_plans/2026-10-04-fresh-agent-doc-cleanup.md`); this change
gives it its subject so the checker's failure mode becomes the designed loud,
lane-named report instead of a crash.

## What Changes

- Land `deep_research_harness/proof-lanes.toml` declaring two lanes over the harness's
  standing surfaces: `verify` (application unit gate) and `smoke` (integration lane),
  each with its command, sentinel, and surface globs.
- Declare the new file in the structural inventory (`required-paths.toml`).
- No checker code changes, no CI changes, no playbook behavior changes: with no
  attestation the checker stays dormant (exit 0) exactly as today; with an attestation
  it now reports unmet lanes by name with rerun hints instead of crashing. The receipt
  producer (`make proof LANE=…`) deliberately stays unbuilt until the
  selected-change attestation flow is actually adopted by an owning change.

## Capabilities

### New Capabilities

- `delivery-lanes`: the lane registry contract — the checked-in
  `proof-lanes.toml` declares the harness's standing proof lanes (name, command,
  surfaces, sentinel) that the proof-receipt checker evaluates against a
  selected-change attestation.

### Modified Capabilities

<!-- none: registering the new file in required-paths.toml is ordinary inventory
     operation under project-structure's existing manifest requirement. -->

## Impact

- New: `deep_research_harness/proof-lanes.toml`.
- Modified: `openspec/governance/required-paths.toml` (one entry).
- Not touched: `check_proof_receipts.py`, the gate inventory, CI, `Makefile`, the
  `deerflow/` gitlink (read-only).
- Operational posture: unchanged while no attestation exists; the first attestation
  flow will fail loudly naming missing receipts — that is the designed failure, and
  its producer lands with the change that adopts the flow.

## Change Focus

- **Primary module / causal owner:** the lane registry
  (`deep_research_harness/proof-lanes.toml`) — the only deliverable; the checker
  already owns all evaluation semantics and is unchanged.
- **Seam classification:** deterministic-guardrail — the file makes an existing
  deterministic checker total (no missing-registry crash) over the harness's standing
  surfaces.
- **Question:** Can the half-landed delivery-lanes device be completed by giving the
  existing checker its declared subject, such that every reachable failure is a named,
  actionable lane report rather than a registry crash?
- **Necessary adjacent/external contracts:** `check_proof_receipts.py` (answers: the
  exact registry schema — `version`, per-lane `name`/`command`/`cwd`/`tier`/`sentinel`/
  `surfaces` — and the evaluation order); `delivery-lanes` local guidance in
  `change-guidance/local/deep-research.md` (answers: which lanes are harness-owned
  today — verify and smoke); the structural manifest (answers: where the new file is
  declared).
- **Evidence seam:** the checker's own `--self-test` (red-first planted violations,
  unchanged and green against the new real registry); `check_project_gate.py --phase
  closeout` exit 0 with the file landed; `git grep` receipt proving no other live
  reference assumes a missing registry.
- **Not in scope:** a receipt producer (`make proof`), attestation generation,
  checker semantics, CI wiring, retiring or re-scoping the apparatus.
- **Triggered review policies:** change-admission
