# Proposal: Ratify Agent Playbook and Minimal Release

## Why

The operator summons the agent with one-line requests ("跑起来 / 跑一个研究"). Today the
knowledge needed to answer those summons lives in two wrong places: stale claims in
`deep_research_harness/README.md` (it still self-describes as a pre-implementation stub
while every lane is implemented), and session-private memory that does not travel with
the release. Meanwhile the release face itself has never been written down, so each
"what do we ship?" question is re-derived from scratch and can silently drift during
development. This change ratifies the operator-approved two-layer invocation structure
(entry menu + playbook subdirectory, planned in
`_backlog/plans/2026-10-04-agent-playbook-and-minimal-release.md`) and turns the
minimal-release answer from an opinion into a deterministic guard that goes red the
moment development violates it.

## What Changes

- **`deep_research_harness/COMMANDS.md` becomes the entry face**: every legal verb and
  make target stays one-line; procedural detail moves out; each procedure-carrying
  entry gains one routing line pointing at its playbook file; the entry face itself is
  the capability ("what can be handled") answer. The existing PLAYBOOK section is
  migrated verbatim as the seed of `playbook/run-research.md`.
- **New `deep_research_harness/playbook/` subdirectory**: one scenario per file, Markdown
  mixed with directly executable real commands, each file carrying exit-code-level
  completion criteria, its scenario's gotchas, and the receipt discipline (only report
  runs actually executed this session; stale facts fixed in the same turn they are
  discovered). Help content is served by the menu itself.
- **Release face defined and guarded**: the release face is exactly
  `deep_research_harness/` plus the pinned `deerflow/` gitlink (evidence-probed:
  `deerflow-harness` installs editable from `../deerflow/backend/packages/harness`;
  `cli.py _pin()` requires that directory; the harness has zero OpenSpec references).
  `openspec/`, `_backlog/`, root guides, `.agents/`, `.env`, and runtime-regenerated
  state stay outside the release face. Distribution form is the source repo via
  `git clone --recursive`; a wheel is explicitly not promised (the wheel target
  excludes `cli.py` and `config/`). The sibling-layout assumption in
  `[tool.uv.sources]` becomes a guarded invariant.
- **New deterministic cold-start guard** (`check_release_face.py` in the governance
  suite): a fast static lane that fails loudly when the release face is violated —
  missing/pin-drifted gitlink, broken sibling layout, `[tool.uv.sources]` pointing
  outside the release face, or harness runtime/CLI source referencing OpenSpec or
  `_backlog`. A full cold-start lane (fresh two-piece checkout: `uv sync` →
  `make verify` → `make create` on the fixture ladder, all exit codes zero) is a
  documented playbook command for on-demand release proof.
- **`deep_research_harness/README.md` status claims corrected**: the stale
  "pre-implementation stub" notice and the "Entry Surfaces: Not defined yet" section
  are rewritten to name the real entry surfaces and point at `COMMANDS.md`.
- **Structure registration**: the new playbook directory, its seed file, the guard, and
  its test are registered in `req-registry.yaml` and `required-paths.toml` under the
  new owning requirement IDs.

## Capabilities

### New Capabilities

- `agent-playbook`: the agent invocation surface — `COMMANDS.md` as a menu-plus-routing
  entry face, the `playbook/` subdirectory of MD-mixed-CLI scenario files with content
  and receipt discipline, and the rule that procedural detail lives only in playbook
  files.
- `release-face`: the minimal release contract — the two-piece release face
  (harness + pinned DeerFlow gitlink), the source-repo distribution posture, the
  sibling-layout invariant, the content-placement rules it induces, and the
  deterministic cold-start guard that fails loudly on violations.

### Modified Capabilities

<!-- none: the project-structure manifest update is normal registry operation under
     PRS-001's existing "exact structural authority" requirement (precedent: cli.py was
     registered under ENS-001 by establish-entry-surface without a project-structure
     delta); the README rewrite is documentation with no spec-level behavior change. -->

## Impact

- New: `deep_research_harness/playbook/` (seed `run-research.md`),
  `openspec/governance/check_release_face.py`, `openspec/tests/governance/test_release_face.py`.
- Modified: `deep_research_harness/COMMANDS.md` (menu + routing; PLAYBOOK section out),
  `deep_research_harness/README.md` (status claims corrected),
  `openspec/governance/req-registry.yaml` + `openspec/governance/required-paths.toml`
  (new requirement IDs and paths), `openspec/governance/README.md` (checker listed in
  the canonical sequence if the operator approves that placement).
- No runtime code changes: `src/deerflow_deep_research/`, `cli.py`, the Makefile
  targets, and the two-ladder configuration are untouched. No new external dependency.
- Ordinary downstream work continues to treat the `deerflow/` gitlink as read-only; this
  change reads only its already-owned public boundary facts (pin, path layout) and
  modifies nothing inside it.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/` checker suite (new
  `check_release_face.py`) — the only behavior-bearing deliverable is the deterministic
  release-face guard; the playbook and menu are content governed by content discipline,
  and the guard is the owner that admits or rejects the release face's structural facts.
- **Seam classification:** deterministic-guardrail — the changed behavior is a gate over
  structural facts (gitlink pin, layout, source references) that must fail loudly on
  violation; no model, prompt, or state machine is touched.
- **Question:** Can the minimal-release contract (two-piece release face, sibling
  layout, no dev-face dependencies in shipped code) be enforced by a checker whose red
  is demonstrably reachable, while the agent invocation knowledge moves into the release
  face itself (COMMANDS menu + playbook files) without duplicating environment-checkable
  facts?
- **Necessary adjacent/external contracts:** `openspec/governance/req-registry.yaml` +
  `required-paths.toml` (answers: where the new requirement IDs and paths are
  registered so the structural manifest stays the exact authority); `entry-surface`
  capability (answers: the menu's verb list must mirror ENS-001's closed six-verb set,
  not invent a second command vocabulary); the `deerflow/` gitlink pin recorded in
  `project-structure.toml` (answers: which commit the release face is pinned to);
  `_backlog/plans/2026-10-04-agent-playbook-and-minimal-release.md` (answers: where the
  ratified decisions come from).
- **Evidence seam:** the governance checker with a red-first test pair
  (`openspec/tests/governance/test_release_face.py`): green on the current tree, red on
  fixture violations (pin drift, sibling break, dev-face reference); `make verify`
  stays green; the full cold-start lane is executed once against the real tree and its
  command/exit-code receipt recorded in the playbook.
- **Not in scope:** wheel/package distribution, CI workflow edits (the canonical
  sequence placement of the new checker is an operator decision recorded as pending),
  real-ladder credential provisioning, `deerflow/` content changes, TUI or new CLI
  verbs, `_backlog/` process changes beyond closing the owning plan.
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| The release face is exactly harness + pinned gitlink; anything else is outside it | Human judgment (operator ratified the two-piece scope from the plan's evidence table) | `check_release_face.py` static lane: gitlink present and matching the manifest pin, sibling layout intact, `[tool.uv.sources]` targets inside the face, no dev-face references from harness runtime/CLI | non-bypassable | A release built from a red tree is refused and the guard is loud on drift; recovery is fixing the tree or re-ratifying the face through a change | No release-manifest DSL and no second inventory: the existing project-structure manifest + one checker carry the contract | Red-first checker test pair in `openspec/tests/governance/`; full cold-start lane receipt recorded in the playbook |
| Procedural invocation knowledge lives in release-face docs, not agent-private storage | Human judgment (operator model: menu routes, playbook carries detail) | Content discipline owned by the `agent-playbook` spec; environment-checkable facts referenced, not copied; staleness fixed in the discovery turn | bounded-repair | The menu cannot drift from ENS-001's six-verb set (checker + unit suite keep the surface closed); stale receipts are repaired in-turn, and the repair bound is the discovery turn | `.agents/skills/`-style private duplication is retired before it ships; no doc-budget pressure (COMMANDS.md is unbudgeted and gets smaller) | `make verify` green; menu text reviewed against the closed verb set during apply |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| Cold-start guard red (pin drift, broken sibling layout, dev-face reference, `tool.uv.sources` escape) | `check_release_face.py` static lane | Developer fixes the tree, or re-ratifies the face through a change; the guard never auto-repairs | Non-zero exit naming the violated release-face fact | Repair, then re-run the guard until green | Red-first test pair: each violation class has a fixture that turns the checker red |
| Playbook command fails at summon time (repo moved since the receipt) | The playbook's receipt discipline | The summoned agent diagnoses before re-running; playbook updated in the same turn the staleness is found | Fresh receipt (command + exit code) replaces the stale one | Proceed on the fresh receipt | Fixture-ladder journey (`make create` completion line) re-executed and recorded |
| Menu line points at a missing playbook file | Content discipline (routing pair rule) | Same-turn repair: restore the file or fix the route | Broken route is a content violation, not a silent dead end | Fix the pair | Guard's static lane also verifies each COMMANDS routing target exists under `playbook/` |
| Full cold-start lane cannot run (network/cache unavailable) | The documented playbook command | Explicit UNVERIFIED marking on the affected receipt; static lane still gates | Release proof withheld, not faked | Re-run when the environment allows | Playbook records the UNVERIFIED marking rule beside the command |
