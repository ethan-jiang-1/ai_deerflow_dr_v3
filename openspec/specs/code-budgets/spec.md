# code-budgets Specification

## Purpose
Owns the required behavior of the code-size budget gate for the repository's own
governance checker scripts: a declared table of per-file and per-function ceilings,
loud failure naming the offending file, its measured size, and its ceiling, and a
ratchet discipline under which ceilings fall as the tree improves and may only be
raised with a one-line justification recorded beside the entry.

## Requirements

### Requirement: Governance-script budgets are machine-checked

The project SHALL declare code-size budgets for its own governance checker scripts as a
declaring table owned by a code-budget checker, with each managed file carrying a
maximum (a) total line count and (b) count of functions above a declared length.
Adding a file to management SHALL be a visible change to the declaring table. The
checker SHALL measure each managed file and SHALL fail loudly, naming the file, the
measured value, the ceiling, and the offending function when a file exceeds its
declared line ceiling or holds more over-length functions than it declares. A managed
file missing from the tree SHALL fail as a missing managed path, and the checker SHALL
NOT enforce any budget for a file the table does not declare.

#### Scenario: Within budget passes

- **WHEN** the code-budget checker runs and every managed file exists with its line
  count and over-length function count at or under its declared ceilings
- **THEN** the checker exits 0

#### Scenario: Over-limit file fails loudly

- **WHEN** a managed file measures above its declared line ceiling, or holds more
  over-length functions than it declares
- **THEN** the checker exits non-zero and names the file, the measured value, the
  ceiling, and — for the function budget — the over-length function

#### Scenario: Missing managed file fails

- **WHEN** the declaring table manages a file that does not exist in the tree
- **THEN** the checker exits non-zero and reports the missing managed path

### Requirement: Ceilings ratchet downward through change

A declared ceiling SHALL only decrease in ordinary changes; raising one requires a
one-line justification recorded next to the entry in the declaring table. The ratchet
SHALL be review-level — the checker enforces the current bound, not the direction of
history — and the declaring table SHALL carry this discipline in its comment so every
editor reads it before touching a number.

#### Scenario: Lowering a ceiling is an ordinary edit

- **WHEN** a change lowers a declared ceiling and the managed file still fits
- **THEN** the checker passes and no additional ceremony is required

#### Scenario: Raising a ceiling demands its recorded justification

- **WHEN** a change raises a declared ceiling
- **THEN** the raise appears in the declaring-table diff for review together with the
  one-line justification the table comment demands

### Requirement: The budget gate proves it can fail

The code-budget checker SHALL carry a self-test that builds a temporary tree with a
planted over-limit file and a planted over-length function, and SHALL verify that each
planted defect is reported. A gate that cannot be shown failing SHALL NOT be treated as
evidence for the ceilings it declares.

#### Scenario: Planted over-limit file is reported

- **WHEN** the checker's self-test builds a temporary tree whose managed file exceeds
  its declared line ceiling
- **THEN** the self-test reports the planted defect rather than passing

#### Scenario: Planted over-length function is reported

- **WHEN** the checker's self-test builds a temporary tree whose managed file holds more
  over-length functions than declared
- **THEN** the self-test reports the planted defect rather than passing
