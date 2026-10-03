> req: RUA-001

# Spec Delta

## MODIFIED Requirements

### Requirement: Dispositions are a closed three-way set with honest replay

The ledger SHALL record exactly the dispositions `admit`, `reject`, and `replay`;
anything else SHALL be rejected loudly. `admit` SHALL place the validated content into
the bundle's `evidence/` subtree and record its path and `content_hash`. `replay` SHALL
be recorded only when the submitted content's hash matches a previously `reject`-ed
entry's `content_hash` and the validator now renders `ok`; content matching an already
`admit`-ed entry SHALL be rejected as a duplicate.

#### Scenario: Admit places content and records it

- **WHEN** a valid, previously unseen proposal is submitted
- **THEN** the content is placed under `evidence/`, and an `admit` entry records the
  placement path and content hash

#### Scenario: Replay of reworked content is recorded honestly

- **WHEN** content whose hash matches a previously rejected entry is resubmitted and now
  validates
- **THEN** a `replay` entry references the rejected entry's sequence, and the reworked
  content is placed under `evidence/`

#### Scenario: An admitted final report lands in final/

- **WHEN** a valid final_report submission is admitted
- **THEN** the content is placed under `final/` and the ledger entry records that path