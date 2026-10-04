# Tasks

## 1. Red — new shapes fail under current code

- [x] 1.1 Create `openspec/tests/governance/test_project_specs.py` with red-first fixtures for the new shapes (delta spec without a `> req:` header validates clean; main spec without a header validates clean; requirement title containing an ID validates clean); declare the new file in `required-paths.toml`; verify the governance unittest run FAILS and record the red receipt
- [x] 1.2 Amend `test_split_manifest.py` fixtures to the new shapes (manifest without `requirement_ids`, tree without `req-registry.yaml`, `required-paths.toml` with a semantic group name all validate clean; seeded structural drift still fails); verify the governance unittest run FAILS and record the red receipt
- [x] 1.3 Amend `test_project_gate.py` expectations (closeout aggregates exactly six components: specs, architecture, change-guidance, dependency-direction, ci-governance, proof-receipts; plan phase has no requirement-reservation step); verify the governance unittest run FAILS and record the red receipt

## 2. Green — remove the enforcement

- [x] 2.1 `check_project_specs.py`: delete rules `missingReqHeader` / `missingDeltaReqHeader` and the title-embedded-ID rule with their helpers; update the file header rule list and messages; verify task 1.1's fixtures pass and the full governance unittest run is green for the specs surface
- [x] 2.2 `check_project_architecture.py` + manifests: delete registry coupling (`REGISTRY_RELATIVE`, `requirement_ids`, owner-ID validation, `REQ_HEADER_RE`); rename `required-paths.toml` groups to semantic family names with byte-identical file lists; drop `requirement_ids` from `project-structure.toml`; verify task 1.2's fixtures pass and the architecture checker exits 0 on the real tree
- [x] 2.3 `check_project_gate.py`: remove the requirement-reservation plan step and shrink the closeout inventory to six components; update the docstring; verify the governance unittest run exits 0
- [x] 2.4 Delete `req-registry.yaml`, `check_project_reqs.py`, `check_project_req_coverage.py` together with their `required-paths.toml` entries; verify `git grep -n "req-registry\|check_project_reqs\|check_project_req_coverage" openspec/governance openspec/specs .github .githooks` returns no live reference (historical mentions in `changes/archive/` are out of scope)

## 3. Declarations and navigation

- [x] 3.1 Strip the `> req:` header line from all nine main specs under `openspec/specs/`; verify `git grep -n "> req:" openspec/specs` is empty and the specs checker exits 0
- [x] 3.2 Delete the new-requirement-ID declaration rule from `openspec/config.yaml`; verify `check_doc_hygiene.py` exit 0 (config.yaml usage drops) and the authoring rules no longer reference the registry
- [x] 3.3 Correct `openspec/governance/README.md`: six gate components in the when-to-read table and command list, no registry rows, standalone checks (`check_doc_hygiene.py`, `check_release_face.py`) marked as such; verify the command list matches the gate inventory exactly

## 4. Sibling change amendments

- [x] 4.1 Amend `catch-up-doc-truthfulness`: drop the `> req:` lines from its delta spec, delete its registry-registration task (1.1) and renumber, drop the `@impl` annotation clause from its rule-implementation task, rewrite its checker-count finding (A10) to the six-component truth, and drop the two removed checkers from its closeout evidence task; verify `openspec validate catch-up-doc-truthfulness --strict` exit 0
- [x] 4.2 Verify the amended sibling change passes the plan gate; verify its remaining tasks reference only machinery that still exists

## 5. Closeout evidence

- [x] 5.1 Run and record receipts: governance unittest suite, `check_project_gate.py --phase closeout` (six components), `check_doc_hygiene.py`, `check_release_face.py`, `UV_OFFLINE=1 make verify` — all exit 0; `git diff --check` clean; red-first receipts from section 1 attached
