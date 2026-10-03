> req: RUA-001

# run-admission Specification

## Purpose

Owns the required behavior of the acceptance closeout: a validator hold point that
admits nothing unvalidated into the bundle, a tamper-evident three-disposition hash-chain
ledger, a minimal pass/blocked gate derivation, closed admission vocabularies, and a
quality register that cannot silently rot.

## Requirements
### Requirement: The validator is the admission hold point

Every artifact submission SHALL be rendered a verdict by the pure validator before any
artifact content is placed into the bundle; a submission whose verdict is not `ok` SHALL
place no content anywhere in the bundle, and its rejection SHALL still be recorded in
the ledger with the validator's reasons. The ledger writer SHALL refuse to commit a
disposition that was not rendered by the validator — a verdict-less commit SHALL fail
loudly.

#### Scenario: Rejected submission places nothing

- **WHEN** a proposal fails validation (malformed shape, missing provenance, empty
  content, or duplicated admitted content)
- **THEN** no artifact content exists in the bundle, and the ledger records a `reject`
  entry carrying the validator's result code and reasons

#### Scenario: Verdict-less commit is refused

- **WHEN** a caller attempts to append a ledger disposition without a validator-rendered
  verdict for the submission
- **THEN** the commit fails loudly naming the missing verdict

### Requirement: The disposition ledger is a tamper-evident hash chain

The ledger SHALL live at `evidence/submissions.jsonl` as append-only JSONL. Each entry
SHALL commit to its predecessor via a sha256 chain (genesis `prev_hash` = 64 zeros) and
SHALL record the submission's `content_hash` (sha256 of the artifact bytes). Reading the
ledger SHALL verify the full chain and SHALL fail loudly, naming the offending sequence
number, when any entry's recorded or computed hash disagrees. Exactly one writer SHALL
own commits; entry sequences SHALL be strictly monotonic.

#### Scenario: Chain verification passes on an honest ledger

- **WHEN** the ledger contains only entries written by the single writer
- **THEN** reading verifies every link and returns the entries

#### Scenario: Tampering fails loudly

- **WHEN** a recorded field of any entry is edited after the fact, or an entry is
  inserted or removed
- **THEN** reading fails naming the first sequence whose chain linkage breaks

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

### Requirement: The gate derives pass or blocked from admitted facts

The gate SHALL be a pure derivation over declared requirements (closed artifact kinds
with minimum admitted counts) and the ledger's admitted facts. It SHALL render exactly
`pass` or `blocked`; `blocked` SHALL name every unmet requirement. There SHALL be no
repair-budget mechanism.

#### Scenario: Blocked names exactly the unmet requirements

- **WHEN** the declared requirements are not covered by admitted artifacts
- **THEN** the gate renders `blocked` naming each unmet requirement and no others

#### Scenario: Satisfied requirements pass

- **WHEN** every declared requirement's minimum is covered by admitted entries
- **THEN** the gate renders `pass`

### Requirement: Admission vocabularies are small closed sets

The artifact kinds (`evidence`, `final_report`), the validator result codes (`ok`,
`schema_malformed`, `missing_provenance`, `empty_content`, `hash_mismatch`,
`duplicate_content`), and the dispositions (`admit`, `reject`, `replay`) SHALL be
declared closed sets; a value outside its set SHALL be rejected loudly at the boundary.

#### Scenario: Unknown artifact kind is rejected

- **WHEN** a submission declares an artifact kind outside the closed set
- **THEN** the submission fails loudly naming the illegal kind

### Requirement: The quality register stays in sync with the machines

A single register surface (`deep_research_harness/docs/quality-register.md`) SHALL list
every declared quality machine — the validator, the gate, the ledger chain
verification, the application unit gate, and the repository governance gates — with the
invariant each guarantees and its evidence seam. The engine SHALL declare its machine
list in code, and a unit test SHALL fail when the register and the declared machine list
disagree.

#### Scenario: Register drift fails the suite

- **WHEN** a machine is added to or removed from the engine's declared list without the
  register naming it (or vice versa)
- **THEN** the unit suite fails naming the drift
