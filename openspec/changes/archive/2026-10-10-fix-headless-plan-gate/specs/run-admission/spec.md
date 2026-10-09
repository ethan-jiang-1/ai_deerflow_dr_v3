# Spec Delta

## Purpose

Owns the run-admission machinery: the validator hold point, the tamper-evident
disposition ledger, the closed disposition set with honest replay, the gate's
pass/blocked derivation, the closed admission vocabularies, and the quality
register's sync discipline.

## MODIFIED Requirements

### Requirement: Admission vocabularies are small closed sets

The artifact kinds (`evidence`, `final_report`), the validator result codes (`ok`,
`schema_malformed`, `missing_provenance`, `empty_content`, `duplicate_content`,
`report_structure_violation`), and the dispositions (`admit`, `reject`, `replay`)
SHALL be declared closed sets; a value outside its set SHALL be rejected loudly at
the boundary. A `final_report` submission whose content carries explicit plan
markers (`<research-plan>`) SHALL be rejected as `report_structure_violation`
naming that aspect — a proposed plan is not a report, whatever other structure it
mimics (BUG-001: a plan-shaped text passed the heading/Sources/envelope aspects and
was admitted).

#### Scenario: Unknown artifact kind is rejected

- **WHEN** a submission declares an artifact kind outside the closed set
- **THEN** the submission fails loudly naming the illegal kind

#### Scenario: A final report without the required structure is rejected

- **WHEN** a `final_report` submission is not valid UTF-8, or carries no Markdown
  heading, or carries no Sources-class section heading, or falls outside the
  declared character envelope, or carries explicit plan markers
- **THEN** the validator renders `report_structure_violation` naming the violated
  aspect, and no content is placed into the bundle
