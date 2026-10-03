# Tasks

## 1. Red proof and checker vocabulary (red-before-green)

- [x] 1.1 Add the removed-grammar negative controls to
      `openspec/tests/governance/test_split_manifest.py` (new `RemovedNodeGrammarTest`
      class, temp-dir fixtures like the existing ones): a manifest with a
      `[node_packages]` table fails with `node.grammar_removed`; a manifest whose
      `ownership_layers` includes `graph` (or any non-canonical layer) fails with
      `manifest.schema`; a manifest whose `[imports]` declares a fifth key fails with
      `manifest.schema`. Red receipt: run the module against the current checker —
      the cases go red because the old checker cannot produce the new rejections (it
      demands the six-key `[imports]` table and imposes no ownership-layer closed set,
      so a grammar-declaring manifest is accepted or rejected under the wrong code),
      which is exactly the silent-reentry path being closed. Verify:
      `python3 -m unittest openspec.tests.governance.test_split_manifest -q` exits 1
      with the new cases red (measured directly).
- [x] 1.2 Update `check_project_architecture.py`: `INTERNAL_LAYERS` → four layers;
      `REQUIRED_INTERNAL_IMPORT_POLICY` drops `graph`/`nodes` and `runtime → graph`,
      comment corrected to PRS-001 (stale PRS-002 pointer); `[imports]` key check →
      exactly the four canonical layers; `ownership_layers` closed-set check;
      `[node_packages]` presence → `node.grammar_removed` violation; delete the
      node-package parse block, `StructureManifest` node fields, nodes-layer import
      exceptions, `_validate_node_packages` and its call site, and the guide's
      node-grammar line; `_source_owner`/`_target_owner` lose the graph/nodes branches.
      Update the same file's `CONTRACT`-shaped expectations in
      `test_split_manifest.py` (fixture `CONTRACT` → four layers, four import keys, no
      `[node_packages]`). Verify:
      `python3 -m unittest openspec.tests.governance.test_split_manifest -q` exits 0
      (new cases now green, existing cases still green).

## 2. Manifest, inventory, and tree (one coherent sequence)

- [x] 2.1 Edit `openspec/governance/project-structure.toml`:
      `ownership_layers = ["runtime", "domain", "engine", "agents"]`; `[imports]` →
      `domain`/`engine`/`agents` unchanged, `runtime = ["domain", "agents"]`, `graph`
      and `nodes` keys deleted, `[node_packages]` section deleted, import-keys comment
      updated. Verify: `python3 -c "import tomllib; d = tomllib.load(open('openspec/governance/project-structure.toml','rb')); assert 'node_packages' not in d and set(d['imports']) == {'domain','engine','agents','runtime'}"` exits 0.
- [x] 2.2 Edit `openspec/governance/required-paths.toml` (PRS-001 files: drop the two
      graph `__init__.py` entries; CIG-001 directories: drop `graph/`, `graph/nodes/`,
      `tests/graph/`) and delete
      `deep_research_harness/src/deerflow_deep_research/graph/__init__.py`,
      `deep_research_harness/src/deerflow_deep_research/graph/nodes/__init__.py`,
      `deep_research_harness/tests/graph/.gitkeep` with their emptied directories.
      Verify: the three paths do not exist and both TOML files parse (tomllib) with no
      `graph` path entry remaining.
- [x] 2.3 Re-render the generated locator in `deep_research_harness/AGENTS.md` from the
      updated manifest (`python3 openspec/governance/check_project_architecture.py
      --render-guide`, replace the block between the markers — never by hand), and edit
      the hand-authored rows: the "Composition, routing, or capability injection" row
      re-points to `src/deerflow_deep_research/runtime/`, and the graph mentions in the
      LLM-Node route, "Where These Decisions Live", and Non-Model Work sections drop
      `graph`. Verify:
      `python3 openspec/governance/check_project_architecture.py` exits 0 on the real
      tree (first point where manifest + inventory + tree + guide are all consistent).

## 3. Routing text and registry description

- [x] 3.1 Update `openspec/governance/architecture-policy.md` (four import-boundary
      keys / four ownership layers, no nodes sub-layer sentence, grammar paragraph →
      "the node-package grammar has been removed; reintroducing it or any additional
      ownership layer requires a `project-structure` spec change", locator description
      loses "grammar") and `openspec/governance/README.md` (manifest row drops
      节点包). Verify: both files contain no `node-package grammar` claim;
      `python3 openspec/governance/check_doc_hygiene.py` exits 0.
- [x] 3.2 Update `openspec/change-guidance/local/deep-research.md` (module map:
      composition routes to `runtime/`; human-decision seam drops "graph authority"),
      `deep_research_harness/tests/README.md` (drop `graph/` from the directory
      classification), `deep_research_harness/README.md` (graph wording → workflow;
      deterministic-owner list drops `graph`), and
      `deep_research_harness/docs/runtime-architecture.md` (boundary list drops
      `graph`). Verify:
      `python3 openspec/governance/check_doc_hygiene.py` exits 0 plain and with
      `--self-test`.
- [x] 3.3 Update `openspec/governance/req-registry.yaml` PRS-001 description: drop
      "节点语法" (IDs and the append-only discipline untouched). Verify:
      `python3 openspec/governance/check_project_reqs.py` exits 0.

## 4. Verification (every exit code measured directly, no pipes)

- [x] 4.1 `python3 -m unittest discover -s openspec/tests/governance -q` exits 0;
      `python3 openspec/governance/check_project_architecture.py` exits 0 (full mode,
      real tree). Receipt: SUITE_EXIT=0, ARCH_EXIT=0.
- [x] 4.2 `python3 openspec/governance/check_project_gate.py --phase closeout` exits 0;
      from `deep_research_harness/`, `UV_OFFLINE=1 make verify` exits 0; from the
      repository root, `openspec validate remove-graph-layer --strict` exits 0 and
      `git diff HEAD --check` exits 0. Receipt: GATE_EXIT=0, MAKE_VERIFY_EXIT=0,
      STRICT_EXIT=0, diff-check clean.
- [x] 4.3 Record scope/diff evidence: `git status --porcelain=v1
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
      `git diff --submodule=short`; confirm the gitlink pointer is unchanged. Confirm
      `openspec --version` equals the `generatedBy` frontmatter in
      `.agents/skills/*/SKILL.md` (read-only check; record any drift). Receipt:
      diff scope matches proposal Impact exactly (12 modified + 3 deleted + 5 change
      artifacts, no strays); gitlink stage-0 160000 at ceebf97f unchanged, nested
      worktree clean; openspec 1.13.1 == generatedBy 1.13.1 (no drift).

## 5. Closeout and archive

- [x] 5.1 Plan-review obligation (control-placement; owner: apply agent): re-read the
      proposal's Control Placement Review and the delta against the actual diff;
      confirm no new control layer was created and the composition row really re-points
      to `runtime/`; every actionable finding becomes an unchecked task or an approved
      re-scope. Done condition: the review record names the compared artifacts and the
      finding count. RECORD: compared proposal.md (Focus + Control Placement Review),
      specs delta, design.md, tasks.md against `git status`/`git diff HEAD` — the diff
      adds no code and no control layer; the AGENTS.md composition row re-points to
      `runtime/` (verified in diff); the three loud-failure guards + their negative
      controls implement the new delta scenario. Actionable findings: 0.
- [x] 5.2 Closeout review (owner: archive agent): compare the Change Focus against the
      actual diff and evidence; confirm the three negative controls are green and the
      five removal surfaces are all covered by the diff. Done condition: the review
      record exists and the gate in 4.2 is green on the final tree. RECORD: Change
      Focus diff coverage confirmed — primary owner manifest edited, checker
      vocabulary + fixed policy + closed-set guards in, inventory entries released,
      guide re-rendered (generated block in diff), routing text aligned, registry
      description updated; all five removal surfaces present in the diff; red receipt
      (exit 1, three named cases) and green receipt (exit 0, 15 tests) recorded under
      1.1/1.2; full verification set green on the final tree (see 4.1-4.3).
      Actionable findings: 0.
- [x] 5.3 After user approval, archive via `openspec archive remove-graph-layer`;
      re-run the aggregate gate (exit 0); verify
      `openspec/specs/project-structure/spec.md` retains `> req: PRS-001` and the
      `> structure:` marker with the modified requirement text merged (the
      establish-project-structure lesson: archive may drop header lines — re-check
      mechanically via `python3 openspec/governance/check_project_architecture.py`
      exit 0). Receipt: user approved 2026-10-02; archive executed, closeout gate
      re-run green, main-spec headers verified intact post-archive.
