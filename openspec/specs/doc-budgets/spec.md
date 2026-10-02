# doc-budgets Specification

> req: DOB-001

## Purpose

Owns the required behavior of the entry-layer budget gate: declared character-counted
ceilings over managed resident instruction files, loud failure on over-limit and on
missing managed paths, and a ratchet discipline for ceiling changes.

## Requirements

### Requirement: Entry-layer budgets are machine-checked

The project SHALL declare entry-layer size budgets for its managed resident instruction
files as a declaring table owned by the document-hygiene checker, with each managed
file carrying a maximum character count measured over the UTF-8 decoded text
(characters, never words — word counts under-count CJK text by an order of magnitude).
The document-hygiene checker SHALL validate every managed file: a file measuring above
its declared ceiling fails loudly, naming the file, its measured size, and its ceiling;
a managed file that is missing from the tree fails loudly as a missing managed path.
The checker SHALL NOT enforce any budget for files the table does not declare, and
adding a file to management is a visible change to the declaring table.

#### Scenario: Within budget passes

- **WHEN** the document-hygiene checker runs and every managed file exists and measures
  at or under its declared ceiling
- **THEN** the checker exits 0

#### Scenario: Over-limit file fails loudly

- **WHEN** a managed file measures above its declared ceiling
- **THEN** the checker exits non-zero and names the file, its measured size, and its
  ceiling

#### Scenario: Missing managed file fails

- **WHEN** the declaring table manages a file that does not exist in the tree
- **THEN** the checker exits non-zero and reports the missing managed path

### Requirement: Ceilings ratchet downward through change

A declared ceiling SHALL only decrease in ordinary changes; raising a ceiling requires
a one-line justification recorded next to the entry in the declaring table. This
ratchet discipline is review-level (a ceiling raise is visible in the diff of the
declaring table) — the checker enforces the current bound, not the direction of
history. The declaring table SHALL carry this discipline in its comment so every
editor reads it before touching a number.

#### Scenario: Lowering a ceiling is an ordinary edit

- **WHEN** a change lowers a declared ceiling and the managed file still fits
- **THEN** the checker passes and no additional ceremony is required

#### Scenario: Raising a ceiling demands its recorded justification

- **WHEN** a change raises a declared ceiling
- **THEN** the raise appears in the declaring-table diff for review together with the
  one-line justification the table comment demands
