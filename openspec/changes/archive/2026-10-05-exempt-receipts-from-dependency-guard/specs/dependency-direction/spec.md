# Spec Delta

## Purpose

Owns the required behavior of the harness→governance dependency guard: which
references count as a forbidden downstream dependency on the development-governance
face, which evidence artifacts are structurally exempt from that judgment, and how the
exemption stays locked against silent widening.

## ADDED Requirements

### Requirement: The harness tree must not depend on the governance face

A deterministic dependency-direction checker SHALL scan the harness tree
(`deep_research_harness/`) — every file on the filesystem, tracked or not, outside
the ignored parts `.venv`, `.pytest_cache`, `__pycache__`, and `.reports` — for the
forbidden tokens `openspec/`, `../openspec`, and `openspec.governance`. Any scanned
file carrying a forbidden token SHALL fail the checker loudly, naming the file and
the token; the checker exits 0 only when no scanned file carries one.

#### Scenario: Source or config reference fails loudly

- **WHEN** any scanned harness file other than a structurally recognized verification
  receipt contains a forbidden token
- **THEN** the checker exits non-zero and names the file and the token

#### Scenario: Untracked files are scanned, not just tracked ones

- **WHEN** a forbidden token sits in a harness file that git does not track and that
  is not a recognized verification receipt
- **THEN** the checker exits non-zero naming that file

#### Scenario: Clean tree passes

- **WHEN** no scanned harness file carries a forbidden token
- **THEN** the checker exits 0

### Requirement: Verification receipts are recognized evidence, not dependencies

The checker SHALL treat a harness-tree file as an exempt verification receipt only
when it is named exactly `verification-receipt.json` and parses as a JSON object
carrying a top-level non-empty `checks` list of command-record objects. Recognition
SHALL be structural, not nominal: a file that carries the name but not the shape
remains scanned. Negative controls in the governance unittest suite SHALL lock the
exemption, going red before it ships and staying in the suite afterwards.

#### Scenario: Recorded governance commands in a valid receipt pass

- **WHEN** a structurally valid verification receipt under the harness tree records
  governance command argv that contains a forbidden token
- **THEN** the checker does not flag that file and exits 0 if nothing else is flagged

#### Scenario: Nominal rename without receipt shape still fails

- **WHEN** a harness file named `verification-receipt.json` does not parse as a JSON
  object with a top-level non-empty `checks` list of command-record objects, and
  carries a forbidden token
- **THEN** the checker exits non-zero naming that file and the token

#### Scenario: The exemption stays locked by red-capable controls

- **WHEN** the governance unittest suite for the dependency guard runs its planted
  fixtures
- **THEN** a valid-receipt fixture yields no violation, while a source-reference
  fixture and a fake-receipt fixture both yield violations — and the suite fails if
  any planted violation stops being detected
