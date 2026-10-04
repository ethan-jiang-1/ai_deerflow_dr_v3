> req: RLF-001

# release-face Specification

## Purpose

Owns the required behavior of the minimal release contract: the release face is exactly
the application tree plus the pinned DeerFlow gitlink, distribution is the source
repository via recursive clone, the sibling layout is an invariant, shipped code carries
no development-face dependencies, and a deterministic guard fails loudly on any
violation of these facts.

## ADDED Requirements

### Requirement: The release face is the two-piece set

The release face SHALL be exactly `deep_research_harness/` plus the `deerflow/`
gitlink at the commit pinned by the structural manifest. `openspec/`, `_backlog/`,
the root guides, session-private storage, `.env`, and runtime-regenerated state SHALL
be outside the release face. The release form SHALL be the source repository obtained
by a recursive clone; a built wheel SHALL NOT be treated as a release artifact because
the entry script, configuration, and runtime data directories are outside its packaged
set.

#### Scenario: The two-piece face runs end to end

- **WHEN** a fresh checkout containing only the release face is prepared
  (`git submodule update --init`), then `uv sync`, the unit gate, and a fixture-ladder
  run are executed in order
- **THEN** all three steps exit zero and the fixture run reports a completed state

#### Scenario: The wheel is not a release artifact

- **WHEN** the project's wheel target is built and inspected against the release face
- **THEN** the packaged set is missing the entry script and configuration directory,
  confirming the wheel cannot serve as the release form

### Requirement: The sibling layout and dependency targets stay inside the face

The application tree and the gitlink SHALL remain sibling directories, matching the
relative dependency source declared by the application's `[tool.uv.sources]`; every
dependency source path SHALL resolve inside the release face. Harness runtime and CLI
source files SHALL NOT reference OpenSpec content or `_backlog` material.

#### Scenario: Layout or dependency escape fails loudly

- **WHEN** the gitlink directory is missing or relocated, a dependency source resolves
  outside the release face, or harness runtime/CLI source gains a reference to
  OpenSpec or `_backlog` material
- **THEN** the release-face guard exits non-zero and names the violated fact

### Requirement: The cold-start guard is deterministic and red-reachable

The release-face guard SHALL be a deterministic checker in the governance suite that
validates the current tree against the two-piece face, the pinned commit, the sibling
layout, dependency-source containment, and the no-dev-face-reference rule. Each
violation class SHALL be reachable by a test fixture that turns the guard red, and the
guard SHALL exit zero on the current compliant tree. A slow full cold-start lane
(fresh two-piece checkout through sync, unit gate, and fixture run) SHALL be documented
as an on-demand release proof beside the fast lane, and SHALL be marked explicitly
when environment constraints prevent executing it.

#### Scenario: Guard is green on the compliant tree and red on every violation class

- **WHEN** the guard runs on the current tree, and again against fixtures that each
  introduce one violation class
- **THEN** the compliant run exits zero, and every violation fixture produces a
  non-zero exit naming that violation
