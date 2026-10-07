# entry-surface Delta

## ADDED Requirements

### Requirement: Create and refine route through the declared chain, locked offline

The `create` and `refine` journeys SHALL route through the declared chain: the stable
launcher delegates to the interaction surface; the verb handler SHALL create or extend
the bundle through the bundle actions owner and SHALL drive the run through the
foreground assembly owner; the foreground assembly SHALL open the bundle checkpointer,
build the bound client, and construct the stream callable through the DeerFlow binding;
the run engine SHALL reach its typed terminal state and SHALL submit the final report
through the admission owner. No journey stage SHALL bypass or duplicate an adjacent
stage's responsibility.

The chain's composition SHALL be locked by an offline contract test in the `contract`
test lane (entering `make verify`, stdlib-only, no framework import): the test SHALL
assert the declared call relationships between the chain's stages, SHALL fail naming
the broken link when a stage is replaced, bypassed, or its owning module renamed
without cutover, and SHALL NOT depend on line numbers or cosmetic formatting so that
behavior-preserving refactors inside a stage do not false-fail.

#### Scenario: The locked chain validates green

- **WHEN** the offline chain-lock contract test runs against a tree whose entry chain
  matches the declared composition
- **THEN** the test passes with every declared link asserted

#### Scenario: A broken or bypassed chain link fails loudly

- **WHEN** a journey stage is rewired to bypass or replace an adjacent stage's owner,
  or a chain module is renamed without cutting over its consumers
- **THEN** the offline chain-lock contract test fails naming the broken link

#### Scenario: Behavior-preserving refactor does not false-fail

- **WHEN** code inside a single chain stage is refactored without changing which owner
  performs each stage's responsibility
- **THEN** the offline chain-lock contract test still passes
