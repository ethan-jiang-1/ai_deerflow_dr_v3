# delivery-lanes Specification

## Purpose

Owns the required behavior of the delivery-lane registry: the checked-in
`proof-lanes.toml` declares the harness's standing proof lanes so the proof-receipt
checker evaluates any selected-change attestation against named, actionable lanes
instead of failing on a missing registry.

## Requirements

### Requirement: Lane registry declares the standing proof lanes

The repository SHALL declare `deep_research_harness/proof-lanes.toml` as the lane
registry consumed by the proof-receipt checker: it SHALL declare at least the
application unit gate lane and the integration lane, each carrying a unique name, the
command that produces its receipt, its working directory, its tier, a sentinel string
that must appear in a valid receipt transcript, and the surface globs whose changes
make the lane required. The registry SHALL parse and satisfy the checker's schema; a
registry that is missing, unparseable, or lane-less SHALL fail the checker loudly. The
checker's evaluation semantics, the receipt format, and the gate inventory SHALL NOT be
changed by this registry's content.

#### Scenario: Registry present and parseable passes

- **WHEN** the proof-receipt checker runs with no attestation
- **THEN** it exits 0 reporting the dormant posture

#### Scenario: Lanes are evaluated, never crashed into

- **WHEN** an attestation is supplied and a touched surface matches a declared lane
- **THEN** the checker reports missing or stale receipts as named lane problems with
  rerun hints, and never fails with a registry error

#### Scenario: Structural inventory keeps the registry honest

- **WHEN** the architecture governance checker runs
- **THEN** the declared registry path exists and the tree validates clean
