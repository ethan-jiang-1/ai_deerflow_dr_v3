# Design

## Context

See proposal.md. The tracking system is normative in exactly one place
(`project-structure` spec, requirement "Registered requirements are owned by specs");
everything else is enforcement machinery: `check_project_specs.py` rules 4–5 plus the
title-embedded-ID rule, `check_project_reqs.py` (registry consistency),
`check_project_req_coverage.py` (evidence mapping by ID), the gate's
requirement-reservation plan phase and eight-component closeout, the architecture
checker's registry coupling, and the manifest's owner-ID grouping. CI's canonical
sequence (unittest suite → closeout gate → doc-hygiene → `make verify`) names none of
the removed pieces individually, so the workflow and hooks are untouched.

## Goals / Non-Goals

**Goals:**
- One coherent deletion: no live reference to the registry or `> req:` convention
  remains in governance, specs, or authoring rules.
- Every surviving guarantee keeps a red-first proof (self-test fixtures updated in the
  same commit as the rule changes they describe).
- The sibling change `catch-up-doc-truthfulness` stays apply-ready after the removal
  (its amendments are part of this change's tasks).

**Non-Goals:**
- Purging historical `@impl` annotations from code comments (inert history, unenforced).
- Restructuring requirement sections, scenario text, or evidence vocabulary.
- Touching the harness test lanes, CI workflow, or hooks.

## Decisions

1. **Manifest regrouping renames keys, not contents.** `[paths.PRS-001]` →
   `[paths.repo-skeleton]`, `DEW-001` → `deerflow-wiring`, `ENS-001` → `entry-surface`,
   `APB-001` → `agent-playbook`, `RLF-001` → `release-face`, `CIG-001` →
   `ci-governance` (group name = the feature family that owns the paths; a name is
   just a declared key, validated for existence and uniqueness, not against any
   registry). File lists are byte-identical, so the diff reviews as a rename plus
   header-comment rewrite. Alternative rejected: collapsing all groups into one list
   (loses the review-friendly family grouping).
2. **Deletion, not archival, for the registry and the two checkers.** Git history is
   the archive; keeping dead checkers would leave gate inventory ambiguity — the exact
   disease this change cures (three disagreeing counts). The architecture checker's
   `registry_missing` fail-closed check is deleted with its subject.
3. **The title-embedded-ID rule dies with the convention.** It existed to keep IDs on
   the `> req:` line; with IDs untracked the rule polices nothing. Requirement titles
   remain semantic anchors by the same wording, minus the ID clause.
4. **TDD per surface, enforcement-first ordering.** The two checkers have no self-test
   flags; their proof lives in `openspec/tests/governance/` unittest fixtures. Red:
   create `test_project_specs.py` for the specs surface, amend `test_split_manifest.py`
   (architecture/manifest) and `test_project_gate.py` (gate inventory + phases) to
   assert the new shapes → the governance unittest run fails under current code. Green:
   implement per surface in dependency order (specs checker → architecture checker +
   manifest → gate → deletions). New and deleted files are declared/deregistered in
   `required-paths.toml` in the same tasks, so the architecture checker never sees an
   undeclared path. Live-tree receipts recorded at each step.
5. **Sibling-change amendments ride in this change's tasks**, so the repo is never
   left with an apply-ready change that references deleted machinery.

## Risks / Trade-offs

- [External tooling or habits still cite req IDs] → `git grep` receipt task proves no
  live reference in governance/specs/config; historical references in archived changes
  and code comments are out of scope by design.
- [Losing the orphan-ID discipline hides unowned specs] → accepted: spec ownership is
  now carried by the specs themselves and the gate's structure/specs checks; the
  tracking added indirection, not guarantees, once the operator retired numbering.
- [Manifest rename breaks generated locator rendering] → the locator block renders
  from the manifest's structural fields, not group names; the architecture checker's
  locator test (kept) proves the render is unchanged.
- [Six-component count drifts again] → the gate's inventory tuple remains the single
  declarative source and its unittest pins the count.

## Migration Plan

Single apply, ordered per Decision 4; every deleted file has a `git grep` receipt
proving no live importer or invocation. Rollback is `git revert` of the change commit;
all deletions are re-addable from history.

## Open Questions

None.
