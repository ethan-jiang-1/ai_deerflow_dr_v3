# Proposal: Make Backlog Process Explicit

## Why

The ledger institution is mostly practiced here but partly unwritten. The issue card
`_backlog/issues/2026-10-12-backlog-process-made-explicit.md`（该卡已毕业为 **CLS-024**，现位于 `_backlog/_archived/_settled_issues/2026-10-12-backlog-process-made-explicit.md`——路径写于当时，毕业会改目录） (a borrowed deliberation from
the same-lineage sibling `ai_dsh_loop_advisor`, 2026-10-12) re-audited this repo against the
source card's seven gaps and found six holding: the defect fix flow has no written
authorization/confirmation semantics, the bug template lacks an acceptance field (BUG-001
improvised one inside its 修复关联 section — the measured cost of the missing format),
severity (`P0/P1/P2`) is recorded but consumed by no rule, the status flip rules are
scattered across three charter sections while the bug side is hollow (no word for fix-ready
or fix-landed, so "implementation is not acceptance" has no name), and the ledger's rules
reach an agent only if the agent chooses to read (pull-only). User ruling 2026-10-12
(「开始落地」): land the card's recommendation set — the three open card questions default
to their recommended sides (exception boundary anchored on the root REVIEW-节制 categories;
vocabulary extension with the `活跃`→`调查中` rename; doorplate adopted with budget
registration).

## What Changes

- **Charter (`_backlog/README.md`) gains a first-class bug walk 「一张 bug 怎么走」**:
  triage → `调查中` → `修就绪` (the ticket: root-cause evidence + fix approach + a written
  `## 修好判据`; for P1/P2 repair-type fixes the flip itself authorizes writing the
  propose) → channel (the fix lands through an OpenSpec change; the owner's 拍板 stays at
  the propose admission boundary — existing law, unchanged) → `已落修` (fix in tree,
  acceptance unproven) → confirmed (`修好判据` met with evidence recorded on the card) →
  archive → write-back. **Exception clause**: a P0 defect, or a fix touching a contract,
  spec semantics, an out-of-bounds/irreversible surface, or a recorded decision does not
  self-authorize — it routes through the owner (categories anchored on the root
  `AGENTS.md` REVIEW-节制 table). The trunk diagram's bug lane gains these
  authorization/confirmation semantics.
- **Dated iron-rule exception**: 「卡上的状态与建议不授予实施权限」 (four-doors step 4)
  gains the scoped, dated `修就绪` exception, stated in the charter so the new flow does
  not silently contradict the rule it rides.
- **Two flip-law tables in the charter**. Issues: four values unchanged, transitions
  written as a guarded table (including suspended-revival and the never-reopens law).
  Bugs: `活跃`→`调查中` rename plus `修就绪`/`已落修`/`等人拍板` with guarded transitions
  (backward flips lawful on falsification; exit words flip only inside the archiving
  change; `待修` parked semantics unchanged; a suspended-revival row). Shared laws:
  silence flips nothing; every flip is a guarded action with a record; `可关闭: 是` is the
  exit-guard flag that lands with the `git mv`.
- **Bug template gains `## 修好判据`** (acceptance criteria, evidence owner, and
  expressible ride-along dependencies — the field BUG-001 improvised becomes a template
  field); `bugs/README.md`'s word table lists the new vocabulary with flip-rule pointers;
  `issues/README.md`'s status section links the charter tables.
- **Checker vocabulary** (`openspec/governance/check_doc_hygiene.py`
  `BACKLOG_STATUS_VOCABULARY`): bugs becomes (`调查中`, `修就绪`, `已落修`, `等人拍板`,
  `待修`); self-test negatives extended red-first (a post-rename `活跃` card fails
  vocabulary; each new word passes; an out-of-vocabulary word fails). Zero active bug
  cards exist today, so the rename needs no card migration.
- **Agent doorplate `_backlog/AGENTS.md`**: thin — the subdirectory positions, the two
  walks, the two ticket conditions, the status vocabularies, pointers to the manual and
  methods; no fact duplication. Registered in `ENTRY_DOCS` (link/newline coverage) and
  `DOC_BUDGETS` (a character ceiling measured at adoption).
- **Live touchpoints synced in the same revision**: `openspec/governance/required-paths.toml`
  gains `_backlog/AGENTS.md`; the issue card's 落地关联 records this change's name (its
  body is otherwise untouched until ritual closeout).

## Capabilities

### New Capabilities

<!-- none: the bug walk, the exception clauses, and the two flip-law tables are charter
     content (成文标准, human-executed) — the same treatment the closure-conditions
     table and the trigger index received in adopt-issue-ledger-governance. -->

### Modified Capabilities

<!-- none: the checker's changed acceptance set stays entirely inside already-spec'd
     mechanisms. doc-truthfulness "Ledger bookkeeping surfaces are machine-consistent"
     owns vocabulary-membership hukou — the vocabulary itself is declaring-table data,
     not spec text. doc-budgets "Entry-layer budgets are machine-checked" owns the
     budget gate — its own requirement states "adding a file to management is a visible
     change to the declaring table". doc-truthfulness "Managed doc surfaces' relative
     links resolve" owns entry-chain coverage — "expanding the managed-surface list is a
     visible change to the declaring table". No new failure class, no changed
     requirement statement; skip_specs: true is declared in .openspec.yaml. -->

## Impact

- New: `_backlog/AGENTS.md`.
- Modified: `_backlog/README.md` (bug walk, exception clauses, two flip tables, trunk
  diagram, word-table rows); `_backlog/bugs/README.md` (template field, word table);
  `_backlog/issues/README.md` (status-section pointer);
  `openspec/governance/check_doc_hygiene.py` (vocabulary, `ENTRY_DOCS`, `DOC_BUDGETS`,
  self-test negatives — no new script, no new dependency);
  `openspec/governance/required-paths.toml` (one row);
  `_backlog/issues/2026-10-12-backlog-process-made-explicit.md`（该卡已毕业为 **CLS-024**，现位于 `_backlog/_archived/_settled_issues/2026-10-12-backlog-process-made-explicit.md`——路径写于当时，毕业会改目录） (落地关联 line only).
- Not touched: the `deerflow/` gitlink (read-only; ordinary downstream work neither
  modifies nor source-browses it and this change claims no boundary ownership);
  `deep_research_harness/` runtime code and tests (no runtime surface; no harness lane
  owed beyond the standing gates); CI workflow; the frozen bodies of archived cards; the
  suspended-pool semantics; the CLS/BUG numbering ritual; the one-change-at-a-time
  release discipline.

## Change Focus

- **Primary module / causal owner:** the `_backlog/` ledger charter (`_backlog/README.md`)
  — the semantic decision is the ledger's process law (walks, flip laws, exception
  boundary); its only behavior-bearing projection is
  `openspec/governance/check_doc_hygiene.py`'s rule-7 declaring tables.
- **Seam classification:** deterministic-guardrail — the changed machine behavior is
  declaring-table values behind the existing red-first hukou/link/budget rules over
  textual ledger facts; no model, prompt, state machine, or runtime lifecycle is touched.
- **Question:** Can the defect fix flow (who authorizes, which channel, what confirms
  fixed), the two status lifecycles, and an agent doorplate be written into the charter
  and its declaring tables so that every rule an agent must obey inside `_backlog/` is
  either machine-anchored or one pointer away — without creating a second truth home and
  without adding a new checker failure class?
- **Necessary adjacent/external contracts:** the `doc-truthfulness` capability (answers:
  the vocabulary-membership and managed-surface mechanisms the new declared values ride);
  the `doc-budgets` capability (answers: the budget-gate contract the doorplate's ceiling
  registration must satisfy — additions are visible declaring-table changes, not
  requirement changes); `openspec/governance/required-paths.toml` (answers: the
  structural inventory the doorplate joins); root `AGENTS.md` REVIEW-节制 (answers: the
  exception-boundary categories the defect-flow clause anchors to); the borrowing source
  `/Users/bowhead/ai_dsh_loop_advisor/_backlog/issues/2026-10-12-backlog-process-made-explicit.md`
  (answers: the upstream rulings and five supplements this change adapts); the issue card
  `_backlog/issues/2026-10-12-backlog-process-made-explicit.md`（该卡已毕业为 **CLS-024**，现位于 `_backlog/_archived/_settled_issues/2026-10-12-backlog-process-made-explicit.md`——路径写于当时，毕业会改目录） (answers: the local
  re-audit, the recommendation set, and the three defaulted rulings this change lands).
- **Evidence seam:** red-first self-test negatives inside the doc-hygiene checker (a
  seeded post-rename `活跃` bug card fails vocabulary; `调查中`/`修就绪`/`已落修` pass; an
  out-of-vocabulary word fails) plus live-run receipts: `check_doc_hygiene.py` (incl.
  `--self-test`), `check_project_gate.py --phase plan/closeout`, `openspec validate
  make-backlog-process-explicit --strict`, `UV_OFFLINE=1 make verify`, the governance
  unittest suite (`python3 -m unittest discover -s openspec/tests/governance -q`) — all
  exit 0. The owning typed fact for the changed lifecycle is the card's 状态行 word (the
  one home); the legal next action for any card is a guarded flip per the charter table.
- **Not in scope:** YAML frontmatter lifecycles (刻意不借 N2 stands); the per-state
  must-have-section checker family (验收在场性 — recorded under-pressure per the upstream
  ruling, not landed); mechanizing flip-law semantics (a human-discipline surface); a
  `blocked` status word; a graduation closed-head field (the four-way closure table plus
  the `毕业门: 已过 → change` pointer already cover it); backfilling old cards; changing
  the numbering ritual, the suspended-pool semantics, or the one-at-a-time discipline.
- **Triggered review policies:** change-admission, local-context
