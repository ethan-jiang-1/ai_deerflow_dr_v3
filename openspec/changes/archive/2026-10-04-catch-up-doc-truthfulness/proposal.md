# Proposal: Catch Up Doc Truthfulness

## Why

The repo graduated from skeleton (9 capability specs, 28 archived changes, six-verb CLI,
112-test unit gate) but its skeleton-era narrative is still live: a fresh-context audit
(`_backlog/plans/2026-10-04-fresh-agent-doc-cleanup.md`, three parallel fresh-agent
passes, all line numbers verified at HEAD `9574298`) found 40 stale/contradictory claims
in exactly the files a fresh agent reads first — including commands that do not exist
(`make proof`), three mutually disagreeing checker counts, and index/ledger drift that
violates the ledger's own "三处一致" ritual. Narrative lag in the resident layer is the
denominator of every prompt: it misdirects every future session until it is caught up.

## What Changes

- **Narrative catch-up across the three doc layers** (root / `deep_research_harness/` /
  `openspec/`, plus `_backlog` ledger indexes): delete or rewrite stale future-tense and
  "骨架/占位/skeleton" claims to present-tense truth (A1-A10, B1-B10, B12-B16, C1-C13 of
  the audit plan); fix dead links and machine-local absolute paths; unify the two
  competing fresh-agent entry chains (root `AGENTS.md` routing table becomes the single
  front door; `CONTEXT-MAP.md` defers to it); rename "Entry Interface" → entry surface
  per the landed ENS-001 vocabulary.
- **Two new deterministic guards in the doc-hygiene checker** (`check_doc_hygiene.py`,
  red-first per TDD): (1) ledger index consistency — `_backlog/plans|bugs` active lists,
  the archived tables, and the authoritative `_done/*` tables must agree with disk and
  with each other (mechanizes the "编号、索引、计数三处一致" ritual); (2) stale-narrative
  markers — a declared closed list of resident/doc files must not contain declared
  skeleton-era markers, with a per-file justification allowlist (e.g. the genuinely
  empty `agents/` layer keeps its "(skeleton)" docstring until its owning change).
- **Ledger repair** (CLS-008/009 missing index rows, stale header dates, shattered
  markdown tables, lost `_reference/` consumption-status index) — both as content fixes
  and as the red-first fuel for guard (1).
- **`openspec/config.yaml` diet**: relocate the duplicated design-routing detail into
  the profile documents it already points at, lowering its resident budget usage
  (currently 12,237/12,500) before it forces a ceiling raise.
- **`governance/README.md` checker inventory corrected** to the real gate inventory
  (8 components, per `check_project_gate.py:41-51`; `check_release_face.py` is a
  standalone check, `check_proof_receipts.py` is a gate component absent from today's
  list).

## Capabilities

### New Capabilities

- `doc-truthfulness`: the declaration-layer truthfulness gate — ledger index
  consistency across the `_backlog` bookkeeping surfaces, and the declared closed-list
  stale-marker rule over resident and doc-layer files (including their justification
  allowlist), both enforced by the doc-hygiene checker's red-first rules.

### Modified Capabilities

<!-- none: every other edit is documentation content, code-comment text, or checker-
     internal rule addition under the new capability above. No existing requirement's
     observable behavior changes; the doc-budgets ceilings themselves are untouched
     (all edits shrink usage; ratcheting the declared numbers down is ordinary
     registry operation, not a requirement change). -->

## Impact

- Modified (docs/content): root `README.md`/`AGENTS.md`/`CONTEXT-MAP.md`;
  `deep_research_harness/` `README.md`/`AGENTS.md`/`COMMANDS.md`/`CONTEXT.md`/
  `docs/*.md`/`tests/README.md`/`Makefile` comments/`src/**/__init__.py` docstrings;
  `openspec/change-guidance/local/deep-research.md`, `openspec/governance/README.md`,
  `req-registry.yaml` (header comment), `selected-change-closeout.md`,
  `architecture-policy.md`, `required-paths.toml` (header comment),
  `check_project_gate.py` (comment only), `openspec/config.yaml`, `openspec/CONTEXT.md`;
  `_backlog` `plans/README.md`, `_done/*README.md`, `_closed_plans/README.md`,
  `_reference/README.md`, `deep_research_harness/docs/known-limitations.md`.
- New behavior: two rules + self-tests inside `openspec/governance/check_doc_hygiene.py`
  (its self-test harness grows; no new script, no new dependency).
- Not touched: `src/deerflow_deep_research/` behavior, `cli.py`, Makefile targets'
  semantics, all capability specs under `openspec/specs/`, CI workflow, and the
  `deerflow/` gitlink (read-only, never modified or source-browsed by this change).

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` — the
  only behavior-bearing deliverable is the checker's two new rules; all other edits are
  declaration-layer content that those rules (plus the existing gates) then hold in
  place.
- **Seam classification:** deterministic-guardrail — the changed behavior is two
  red-first rules over textual/ledger facts; no model, prompt, state machine, or
  lifecycle outcome is touched.
- **Question:** Can "the declaration layer matches the implemented reality" be held by
  machine (ledger consistency + declared stale-marker rule with justification
  allowlist) rather than by narrative discipline, while the 40 audited claims are
  caught up without breaching any resident budget ceiling?
- **Necessary adjacent/external contracts:** `doc-budgets` capability (answers: the
  character ceilings and ratchet discipline the catch-up edits must fit under);
  `_backlog/README.md` ledger ritual (answers: what the three-way ledger consistency
  invariant is, so the guard mechanizes an already-stated rule rather than inventing
  one); `entry-surface` / `agent-playbook` capabilities (answers: the six-verb command
  vocabulary and COMMANDS routing targets the corrected docs must mirror);
  `_backlog/plans/2026-10-04-fresh-agent-doc-cleanup.md` (answers: where the 40
  findings, their file:line evidence, and the deferred semantic decisions live).
- **Evidence seam:** red-first self-test pairs inside the doc-hygiene checker (green
  tree after fixes, red on seeded violations: a missing index row, a re-introduced
  marker); `check_doc_hygiene.py` + `check_project_gate.py --phase plan/closeout` +
  `check_release_face.py` + `make verify` all exit 0; `git grep` receipts showing each
  A-class claim's before/after text.
- **Not in scope:** the deferred semantic decisions recorded in the audit plan — the
  `start` ↔ `create` spec mapping (A11 — spec content change), the `mixed` composition's
  declared-but-unwired disposition (B4), the empty `agents/` layer's fate (its
  "(skeleton)" docstring stays under the guard's justification allowlist), and the
  Delivery Lanes apparatus land-or-retire decision (B11 — `check_proof_receipts.py`
  behavior unchanged; only the prose in `deep-research.md` is corrected to today's
  reality). Each enters its own change with an explicit user ruling.
- **Triggered review policies:** change-admission, authority-and-projections, local-context

## Impact on resident budgets

All edits shrink declared resident files first (root `AGENTS.md` 2323/2500, harness
`AGENTS.md` 6934/7000, `openspec/config.yaml` 12,237/12,500); where a routing line is
added (C2), an equal-or larger stale passage is removed in the same file. Declared
ceilings are ratcheted down to post-change measurements as ordinary registry operation;
no ceiling is raised.
