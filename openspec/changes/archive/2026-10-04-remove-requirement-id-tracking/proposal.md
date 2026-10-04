# Proposal: Remove Requirement ID Tracking

## Why

The requirement-ID tracking overlay (`> req:` spec headers, `req-registry.yaml`, gate
requirement reservations, and the two checkers that enforce them) has outlived its
use: the operator has retired requirement-number tracking for this project, and the
overlay is now pure ceremony with real costs — three disagreeing checker-count claims
in `governance/README.md`, a reservation phase every plan gate must satisfy, two
whole checkers whose only subject is the registry itself, and a structural manifest
grouped by owner ID whose IDs point at a file the tracking alone keeps alive. The
audible signal (requirement names in specs, deterministic structure validation) does
not need it; removing it simplifies the gate from eight components to six.

## What Changes

- **Remove the tracking requirement from the `project-structure` spec**: the
  requirement "Registered requirements are owned by specs" (registry membership,
  `> req:` ownership headers, orphan/retirement semantics) is deleted with migration.
- **Strip all `> req:` header lines** from the nine main specs and from active delta
  specs (requirement names and scenario structure stay untouched — they are the spec).
- **Deregister the machinery**: delete `openspec/governance/req-registry.yaml`,
  `check_project_reqs.py`, and `check_project_req_coverage.py`; remove the
  requirement-reservation phase from the plan gate and shrink the closeout gate
  inventory from eight components to six.
- **De-couple the structural manifest from owner IDs**: `required-paths.toml` groups
  are renamed from `[paths.<REQ-ID>]` to semantic family names;
  `project-structure.toml` drops its `requirement_ids` field; the architecture
  checker drops its registry-readability and owner-ID validation while keeping every
  structural validation it performs today.
- **Update the authoring context and governance navigation**: delete the
  new-requirement-ID declaration rule from `openspec/config.yaml`; correct
  `governance/README.md` (six gate components, no registry rows, standalone checks
  marked); update the governance unittest fixtures to the new shapes.
- **Amend the sibling active change** `catch-up-doc-truthfulness`: its delta spec drops
  the `> req:` header, its registry-registration task is deleted, and its closeout
  evidence list drops the two removed checkers (its audit findings B12/B16 are
  resolved by this deletion instead of by content edits).

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `project-structure`: REMOVES the requirement "Registered requirements are owned by
  specs" — requirement-ID ownership tracking (registry, `> req:` headers, orphan and
  retirement semantics) is retired entirely; the structural-manifest and gitlink
  requirements are unchanged.

## Impact

- Deleted: `openspec/governance/req-registry.yaml`,
  `openspec/governance/check_project_reqs.py`,
  `openspec/governance/check_project_req_coverage.py`.
- Modified (governance): `check_project_specs.py` (tracking rules out),
  `check_project_gate.py` (plan phase and six-component closeout),
  `check_project_architecture.py` (registry coupling out),
  `project-structure.toml`, `required-paths.toml` (group names),
  `governance/README.md`, `openspec/config.yaml` (one rule), governance unittest
  fixtures (`test_project_gate.py`, `test_split_manifest.py`, and the checkers'
  self-tests).
- Modified (specs): nine main specs lose their `> req:` header line only; the active
  change `catch-up-doc-truthfulness` loses its delta header and its registration task.
- Not touched: the `deerflow/` gitlink (read-only), CI workflow and hooks (the
  canonical sequence is the gate + doc-hygiene + verify, none of which is named away),
  harness code and its historical in-code `@impl` annotations (they become inert
  history, not enforced facts), every capability requirement's observable behavior.

## Change Focus

- **Primary module / causal owner:** the structural manifest contract
  (`openspec/governance/project-structure.toml` + `required-paths.toml`) — the deepest
  coupling is that the manifest's grouping and the architecture checker's validation
  are keyed by registry owner IDs; once the manifest is ID-less and self-validating,
  the registry and its two checkers have no subject left and delete cleanly.
- **Seam classification:** deterministic-guardrail — every touched surface is a
  deterministic checker, manifest, or declaration file; no model, prompt, state
  machine, or lifecycle outcome is involved.
- **Question:** Can requirement-ID tracking be removed end-to-end (spec headers,
  registry, reservations, two checkers, manifest owner-keying) while every surviving
  guarantee — structural validation, spec structure validation, the six-component
  closeout gate, CI's canonical sequence — keeps its red-first proof?
- **Necessary adjacent/external contracts:** `project-structure` capability (answers:
  which normative text is removed and what the manifest must still guarantee);
  `ci-governance` capability (answers: the canonical sequence is unchanged — the gate
  shrinks internally); the sibling change `catch-up-doc-truthfulness` (answers: which
  of its tasks and findings this deletion resolves); `openspec/config.yaml` authoring
  rules (answers: the ID-declaration rule that authoring agents read).
- **Evidence seam:** red-first unittest fixtures (a delta spec without a `> req:`
  header validates clean; a manifest without `requirement_ids` and a tree without the
  registry validate clean; seeded structural drift still fails); the six-component
  closeout gate and plan gate exit 0 on this change; `git grep` receipts proving no
  live reference to the deleted files remains.
- **Not in scope:** removing in-code `@impl` historical annotations anywhere in the
  tree; renaming or restructuring any requirement section in main specs; changes to
  the evidence policy (`test-evidence-policy.md`), the evidence vocabulary, or the
  harness test lanes; the sibling change's own doc-truthfulness content.
- **Triggered review policies:** change-admission, authority-and-projections
