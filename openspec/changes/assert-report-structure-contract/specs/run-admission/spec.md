## MODIFIED Requirements

### Requirement: Admission vocabularies are small closed sets

The artifact kinds (`evidence`, `final_report`), the validator result codes (`ok`,
`schema_malformed`, `missing_provenance`, `empty_content`, `duplicate_content`,
`report_structure_violation`), and the dispositions (`admit`, `reject`, `replay`)
SHALL be declared closed sets; a value outside its set SHALL be rejected loudly at
the boundary.

#### Scenario: Unknown artifact kind is rejected

- **WHEN** a submission declares an artifact kind outside the closed set
- **THEN** the submission fails loudly naming the illegal kind

#### Scenario: A final report without the required structure is rejected

- **WHEN** a `final_report` submission is not valid UTF-8, or carries no Markdown
  heading, or carries no Sources-class section heading, or falls outside the
  declared character envelope
- **THEN** the validator renders `report_structure_violation` naming the violated
  aspect, and no content is placed into the bundle
