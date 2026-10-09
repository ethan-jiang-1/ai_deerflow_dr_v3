# test-evidence Specification

## Purpose
Owns the semantics of the test-evidence layer: the honesty discipline of the evidence
ladder (every declared tier states what it does not prove), the behavior-assertion
(level-4) semantics — pure derivation from recorded real-run journals, observation never
admission, closed event vocabularies — and the provenance honesty of consumed retained
samples. This spec is the owning main spec named in the repository's governance records;
the policy document (`openspec/governance/test-evidence-policy.md`) and the ladder table
in the harness docs operate under it.

## Requirements

### Requirement: Every evidence tier declares what it does not prove

The declared evidence ladder (stunt-double tiers and proof lanes) SHALL carry, for each
tier, an explicit statement of what that tier does NOT prove. A tier whose declared
capabilities cannot be phrased as a negative scope (what it excludes) SHALL NOT be
declared. Adding or re-scoping a tier is an owning-change decision; the declaration lives
in the owning document, not in this spec's body.

#### Scenario: Honest tier declaration passes

- **WHEN** the ladder document declares a tier with its mechanism, use, and an explicit
  does-not-prove statement
- **THEN** the declaration stands and this spec's other requirements apply to its assets

#### Scenario: A tier accumulating an undeclared claim is out of scope

- **WHEN** an asset or document claims a tier proves something outside its declared
  negative-scoped boundary
- **THEN** the claim is a defect in the declaring document (caught by review), not a
  change to this spec

### Requirement: Behavior assertions derive purely from recorded real-run journals

Behavior assertions (ladder level 4) SHALL be pure functions over the recorded journal
(`diagnostics/journal.jsonl`) of a real run: tool-selection counts from `model_tool_call`
entries, event-kind composition, and wall-clock span from recorded timestamps. They SHALL
invoke no model, no network, and no run admission code path. Every pinned expectation
SHALL come from a fixture extracted verbatim from a real recorded run (local run storage
never enters the repository), and every assertion family SHALL carry a degenerate negative
that fails loudly naming the violated face.

#### Scenario: Pinned real-run profile passes

- **WHEN** the profile function runs over the real-run journal fixture and every declared
  expectation (per-tool counts, event composition, span) matches the recorded run
- **THEN** the assertion passes

#### Scenario: Tampered expectation fails loudly

- **WHEN** a declared expectation is altered (a count, a span, a kind) so it no longer
  matches the fixture
- **THEN** the test fails naming the mismatched field

#### Scenario: Degenerate research is named

- **WHEN** a journal records zero search/fetch tool calls (a research run that never
  researched)
- **THEN** the degenerate face is asserted and named, and the assertion fails on such a
  journal

### Requirement: Behavior assertion observes; it never admits

A behavior-profile machine and its results SHALL NOT render or feed run-admission
verdicts: its output is observational data (profiles and named violations of declared
expectations), never admission codes. The machine registers under the quality register's
sync requirement with an invariant stating this observation boundary.

#### Scenario: Register stays in sync with the machine list

- **WHEN** the declared machines list gains or loses the behavior-profile entry without
  the quality register following (or vice versa)
- **THEN** the drift test fails

#### Scenario: Profile output carries no admission vocabulary

- **WHEN** the profile's output type is inspected
- **THEN** it exposes profiles and violated-expectation names, and contains no admission
  result code or verdict

### Requirement: Consumed retained samples state their provenance limits

A test that consumes a retained real sample (recorded model output, recorded event
stream) SHALL state, at the point of consumption, the sample's provenance limits (what it
cannot independently verify about realness). A retained sample with no consumer stays
declared as such in the test-asset registry rather than being silently consumed.

#### Scenario: Consuming test states limits

- **WHEN** a test reads a retained real-model sample and asserts on its content
- **THEN** the test documents that the sample lacks the fields needed to independently
  verify its realness, and the assertion claims only replay fidelity

#### Scenario: Unconsumed sample stays declared

- **WHEN** a retained sample has no test consumer
- **THEN** the test-asset registry says so explicitly instead of implying coverage
