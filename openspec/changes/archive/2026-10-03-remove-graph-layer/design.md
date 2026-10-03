# Design

## Context

Verified current state (this session, read directly — see proposal.md Why for motivation):

- `graph/` holds exactly two skeleton `__init__.py` files and `tests/graph/` one
  `.gitkeep`; no module, doc, or test consumes the `NODE_SPEC` grammar (repo-wide grep:
  the only mentions are the contract, the checker, the split-manifest test fixture, the
  generated locator, and hand-authored routing text).
- `check_project_architecture.py` hardcodes the vocabulary in four places:
  `INTERNAL_LAYERS` (six-layer set), `REQUIRED_INTERNAL_IMPORT_POLICY` (includes
  `graph`/`nodes` directions and `runtime → graph`), the `[imports]` six-key equality
  check in `load_manifest`, and the layer classification in `_source_owner` /
  `_target_owner` — plus the required `[node_packages]` parse block, the nodes-layer
  import exceptions inside `_validate_module_imports`, `_validate_node_packages` with its
  call site, and the node-grammar line in `render_guide_block`.
- `test_split_manifest.py`'s `CONTRACT` fixture carries the full grammar, so the checker's
  existing red/green unittest coverage is coupled to the removal.
- Pre-existing wrinkle on a surface this change touches: the
  `REQUIRED_INTERNAL_IMPORT_POLICY` comment says "owned by PRS-002", but
  `req-registry.yaml` has no PRS-002 — the policy is owned by PRS-001's requirement.

Decision source: digest boundary decision (outer orchestration = plain state machine;
cognition = DeerFlow native) landed by wiring-plan decision 3. Policy routing: the
config.yaml design rule fires on "graph/node" changes, but this surface has no
StateGraph transition/predicate, no model-bearing node, and no lifecycle projection —
the selected canonical policies are `control-placement` and `change-admission`
(reviewed in the proposal).

## Goals / Non-Goals

**Goals:**

- The grammar leaves all five surfaces at once (contract section, checker
  vocabulary + fixed policy, node validation, guide locator line, inventory entries) so
  the exact structural authority describes the real tree again.
- The return path is loud: closed-set manifest vocabulary, named violation for
  `[node_packages]`, negative controls proving each guard red.
- All hand-authored routing text points agents at the surviving layers.

**Non-Goals:**

- No retirement of the checker's v2-inherited fixture-package machinery
  (`fixture_root` / `fixture_imports` / `ResearchGraphRecipe`) or of the sibling
  checker-internal `tool` layer special case (a root `tool.py` v3 has no owner for,
  outside `ownership_layers` and the `[imports]` keys) — both are real dead vocabulary,
  and retiring them is a separate argued change (v3 fixtures ride config `use:` seams
  per the wiring plan decision 6).
- No new ownership layer, no `[imports]` allowance change beyond dropping `graph`, no
  CI workflow change, no `deerflow/` contact, no application code.

## Decisions

1. **Total removal, not deprecation.** A grammar that never existed in code has no
   consumer to migrate; leaving any of the five surfaces in place keeps the authority
   lying. Alternative (keep the section, mark unused) rejected — the manifest is the
   *exact* enumeration; "declared but unused" is precisely the drift it exists to
   prevent.
2. **The return path is mechanically loud.** `ownership_layers` gains a closed-set check
   (exactly the four canonical layers), the `[imports]` key check narrows from six to
   four keys, and a present `[node_packages]` table raises a dedicated violation
   (`node.grammar_removed`) naming the removed grammar. This mechanicalizes what
   architecture-policy.md already states ("changing the grammar itself requires a
   `project-structure` spec change"): after this change, a manifest edit alone cannot
   re-enter the grammar — only a spec change can, and the checker fails until the spec
   is changed. Alternative (soft removal — the checker just stops knowing the layers)
   rejected: a re-declared manifest would partially validate and the guide would
   re-render the dead grammar; that is a silent re-entry path.
3. **`runtime`'s fixed allowance drops `graph`.**
   `REQUIRED_INTERNAL_IMPORT_POLICY["runtime"]` becomes `{domain, agents}`; the policy
   stays non-weakenable and comment-corrected to PRS-001 (the stale PRS-002 pointer is
   fixed in the same edit — the registry has no PRS-002).
4. **`langgraph` stays in the external-namespace whitelist.** The whitelist answers "is
   this namespace real", not "who imports it"; no layer declares it after this change,
   and a future `runtime` module may legitimately need it. Removing it would be
   speculative tightening.
5. **Composition/routing questions re-point to `runtime/`, no replacement layer.** The
   harness `AGENTS.md` decision table keeps the decision type with `runtime/` as owner
   (DeerFlow binding and assembly), and `local/deep-research.md`'s module map matches.
   Rationale: middleware 只配置 and the embedded client make runtime the assembly seam
   (wiring decisions 1/4); inventing a "composition" home would recreate the removed
   layer under another name.
6. **Negative controls live in the unittest suite, not a new `--self-test`.** The
   architecture checker has no self-test harness; its established red-proof home is
   `openspec/tests/governance/` fixtures (same seam the split-manifest tests already
   use). Three invalid-fixture cases: `[node_packages]` present → red; ownership layer
   beyond the canonical four → red; `[imports]` key beyond the four layers → red.
7. **Docs align in the same change.** `architecture-policy.md` (import-matrix counts,
   grammar paragraph), governance `README.md` (导航 row), `local/deep-research.md`
   (module map), harness `tests/README.md`, `README.md`, `docs/runtime-architecture.md`,
   and the hand-authored `AGENTS.md` rows stop claiming a graph layer. Two deliberate
   keep-decisions, recorded per the in-place-disagreement discipline: `openspec/config.yaml`
   keeps its "graph route"/StateGraph authoring vocabulary (DeerFlow-framework terms for
   *future* changes, not a claim that the harness owns a graph layer — editing it is a
   heavier governance action with zero enforcement delta here), and
   `test_terminology_rules.py` keeps its "full-fake graph" strings (they exercise the
   composition-alias terminology rule, not the layer).

## Alternatives

- **Soft removal (checker forgets the layers, no closed-set rejection)** — rejected:
  see decision 2; it leaves a silent re-entry path and lets the guide re-render the
  grammar.
- **Fold the removal into the first product change** — rejected: governance churn
  inside a product diff muddies both reviews; house practice keeps governance contract
  changes separate (add-ci-governance, add-doc-budget-gate precedent), and the wiring
  plan explicitly names this as its own 治理小改.
- **Keep the skeleton directories as future placeholders** — rejected: the inventory
  must stay exactly true (declared ⇔ present), and a placeholder with no owner is how
  the dead grammar accreted in the first place.
- **Also remove the fixture-package machinery** — deferred: genuinely dead under the
  config-`use:`-seam decision, but retiring it touches fixture semantics no other part
  of this change needs; it gets its own argued change instead of riding this one.

## Risks / Trade-offs

- [Checker edit loosens a surviving guard] → the governance unittest suite (including
  the untouched split-manifest green cases) plus a full real-tree checker run gate every
  verification step; the new negative controls prove the new guards red by construction.
- [Apply lands in an intermediate red state] → task order puts manifest, inventory,
  checker, tests, deletions, and guide re-render inside one coherent sequence, and the
  checker is invoked as evidence only after all of them; each task still carries a
  directly measurable Verify command.
- [Doc wording trips the terminology or doc-hygiene rules] → doc hygiene (plain and
  `--self-test`) runs in verification; every edit shrinks its file, so the budget
  ratchet is never stressed upward.
- [Archive merge drops the main spec's header lines] → the closeout tasks re-verify
  that `openspec/specs/project-structure/spec.md` retains `> req: PRS-001` and the
  `> structure:` marker; the checker's `spec.reference_*` violations enforce the marker
  mechanically (establish-project-structure lesson).

## Migration Plan

Single apply, dependency-ordered: checker vocabulary + fixed policy + closed-set guards;
unittest fixture + negative controls; contract + inventory edits + tree deletions;
guide re-render + hand-authored routing text; docs + registry description; then the
verification sequence (unittest suite, real-tree checker, doc hygiene, closeout gate,
`UV_OFFLINE=1 make verify`, `openspec validate remove-graph-layer --strict`,
`git diff HEAD --check` + scope/diff evidence). Rollback is reverting the edits; no
registry ID is added, so there is no retirement path to manage.

## Open Questions

(none — the removal surface was verified against the tree this session; no deferred
unknown remains that could change the specs, the approach, or the task breakdown)
