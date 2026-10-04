# Design: Ratify Agent Playbook and Minimal Release

## Context

The ratified decisions live in
`_backlog/plans/2026-10-04-agent-playbook-and-minimal-release.md` (operator model:
menu routes, playbook carries detail; release face probed as harness + gitlink). The
current tree already contains the seed: a PLAYBOOK section inside `COMMANDS.md`
(written ad hoc before this change, shape-conforming content but wrong location), a
fully implemented command surface owned by `entry-surface` (ENS-001), and a structural
manifest (`project-structure.toml` + `required-paths.toml`) that is the only
structural authority. Governance checkers are plain stdlib scripts under
`openspec/governance/` with tests under `openspec/tests/governance/`, driven by exit
codes.

## Goals / Non-Goals

- Goals: the menu/`playbook/` two-layer structure exists and is guard-checked; the
  release face is written down with a deterministic, red-reachable guard; the stale
  README claims are gone; the new structure is registered so the manifest stays exact.
- Non-Goals: no runtime code changes; no CI workflow edit in this change (the new
  checker's entry into the CI canonical sequence is an operator decision, tracked as
  an open question); no wheel work; no real-ladder credential changes; no `deerflow/`
  content work.

## Decisions

### D1. The guard is a static-lane governance checker, with the full cold-start as a documented slow lane

`check_release_face.py` validates what is checkable cheaply and deterministically on
the current tree: gitlink present and equal to the manifest's `[upstream_gitlink]`
commit; harness and gitlink are siblings; every `[tool.uv.sources]` path (resolving
the `../` form against `deep_research_harness/`) resolves inside the release face; no
harness runtime/CLI source file references OpenSpec or `_backlog` material; each
`COMMANDS.md` routing target exists under `playbook/`. The full cold-start lane (fresh
two-piece checkout → `uv sync` → `make verify` → `make create` on the fixture ladder)
is documented in `playbook/run-research.md` as the on-demand release proof.

- *Why static-first:* the cold-start lane pulls dependencies and runs a research
  journey — minutes, network-sensitive, and unusable as an always-on gate. The static
  lane is sub-second, offline, and covers every structural way development can
  silently break the face. Precedent: the architecture checker validates structure
  statically while the journey lives in the test lanes.
- *Alternatives:* (a) CI job running the full cold-start — rejected for this change:
  network-flaky, slow, and the CI-vs-local placement is an operator decision; (b) no
  guard, plan text only — rejected: the operator explicitly asked for a machine check
  so the contract cannot be forgotten.

### D2. Reference-scan rule: coupling shapes only, not prose

The scan covers `deep_research_harness/src/` and `cli.py` for coupling *shapes* to the
development face: import statements (`import openspec` / `from _backlog …`) and
string-literal path references (`"openspec/…"`, `'_backlog/…'`). Prose mentions inside
docstrings are deliberately green — the first real-tree run flagged
`engine/machines.py`, whose register docstring merely *describes* that the gate never
links OpenSpec content; that is documentation of independence, not coupling. The scan
therefore matches what a dependency would look like, not what a mention looks like.
Legitimate future coupling must go through a change that re-ratifies the face.

### D3. Menu routing is guard-checked, not convention

The one-line routing promise (menu → playbook) is enforced by the same checker: every
routing target named in `COMMANDS.md` must exist under `playbook/`. This turns the
content-discipline pair rule ("new scenario = one file + one line") into a checked
invariant instead of trust.

### D4. Registry operation follows the establish-entry-surface precedent

New requirement IDs (APB-001, RLF-001) are reserved in the delta specs and registered
in `req-registry.yaml` by an apply task; the playbook directory, seed file, guard, and
its test are registered in `required-paths.toml` under those IDs. No
`project-structure` spec delta: adding inventory entries is normal operation under
PRS-001's existing exact-authority requirement.

### D5. Seed migration is verbatim, then re-shaped minimally

The existing PLAYBOOK section moves into `playbook/run-research.md` as written
(preserving its receipts and gotchas), then gains only what the `agent-playbook`
spec demands: explicit completion criteria per step and the routing line back from the
menu. `COMMANDS.md` keeps the entry lists and gains one routing line; the HELP card is
retired into the menu framing (the menu itself answers "what can be handled"), since
its content was a subset of the entry lists plus reserve-area boundaries already
declared in the module guide.

## Risks / Trade-offs

- [Textual reference scan could false-positive on prose] → Resolved during apply: the
  scan matches coupling shapes (import statements, dev-face path strings), not bare
  tokens; the first real-tree run flagged `engine/machines.py`'s register docstring,
  which refined the rule instead of the shipped comment (see D2).
- [Routing check hard-codes `COMMANDS.md` filename knowledge into the checker] →
  Accepted: the file is the registered entry face under PRS-001's inventory; if the
  entry face moves, the manifest moves with it and the checker fails loudly in
  between — which is the contract working.
- [The full cold-start lane stays unexecuted in CI, so the fast lane could pass while
  the slow lane breaks (e.g., new undeclared runtime dep)] → Mitigated in depth: the
  unit gate is stdlib-only by construction, `uv sync` resolves from the locked
  `uv.lock`, and the plan's discipline requires a fresh cold-start receipt at release
  time; residual risk recorded rather than hidden.
- [Menu shrink breaks doc-hygiene link rules] → `COMMANDS.md` is not in the budgeted
  entry chain and the playbook files live outside `docs/`; `check_doc_hygiene.py`
  runs as part of the plan gate to confirm.

## Migration Plan

Apply order: register IDs → red-first guard test + checker (red on fixtures, green on
tree) → migrate seed into `playbook/run-research.md` → rewrite `COMMANDS.md` as menu →
correct README claims → run governance checks + `make verify` → record the cold-start
lane receipt. Rollback: single-commit revert; no data, schema, or runtime state is
touched, and the registry additions are removed by the same revert.

## Open Questions

- Whether `check_release_face.py` joins the CI canonical sequence now or stays
  local-only (the proposal's Not-in-scope defers this to the operator; the checker is
  written to be sequence-ready either way).
