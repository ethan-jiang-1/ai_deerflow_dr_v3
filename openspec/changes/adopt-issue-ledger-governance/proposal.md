# Proposal: Adopt Issue Ledger Governance

## Why

The `_backlog` active category is named `plans` but has always operated as an issue
ledger (推敲 → 结论 → 交接); the name is vaguer than the usage and the usage outgrew the
name. The same ledger institution, evolved further in the sibling repo
`ai_dsh_assitant` (same lineage; its borrow records cite this repo as one upstream),
shows four increments this repo lacks: a four-way closure ritual (do / later / never /
answered-elsewhere), a live trigger index that keeps deferred verdicts from sinking,
machine-anchorable card hukou (`状态`/`毕业门`), and a residency guard for cards that
declared graduation but never left the active zone. The sinking is already observed
here: CLS-010's Tier-C trigger table lives in a frozen card, and CLS-020 only noticed a
trigger condition had fired by deliberately rereading that card. User ruling
(2026-10-09): adopt the long-term-right shape — retire the `plans` category name and
make `issues` the first-class category.

## What Changes

- **BREAKING** ledger category rename (paths move, contents do not): `_backlog/plans/`
  → `_backlog/issues/`; `_backlog/_done/_closed_plans/` → `_backlog/_done/_settled_issues/`;
  `_backlog/_done/_suspended_plans/` → `_backlog/_done/_suspended_issues/`. The 19
  archived cards move by `git mv` with bodies untouched (same-depth move, relative links
  unaffected); the CLS-NNN identifier scheme is unchanged (Next = CLS-019). The two
  category count stays two: issues / bugs.
- **Issue card template + status vocabulary** in `issues/README.md`: status line carries
  `状态` (`推敲中` / `等人拍板`), `毕业门` (`未过` / `已过 → change`), `可关闭` (`是` / `否`),
  `类型` (`Feature` / `Task` / `未定`); archive-side words `已结` / `叫停`; bug vocabulary
  gains `待修`. Old cards are not backfilled.
- **Four-way closure-conditions table** in `_backlog/README.md`: 做 (→ Change Focus +
  change destination) / 以后做 (→ suspended pool or trigger row) / 不做 (→ reason + scope)
  / 结论已在别处 (→ pointer), plus a step→owner routing table (no `methods/` directory —
  the method owners already exist in `openspec/change-guidance/`, `governance/`, session
  skills) and a dated 刻意不借 register (negative knowledge: no `research/` card-migration
  lifecycle — `_reference/` stays a long-lived corpus; no YAML frontmatter; no `YYMMDD`
  card names; no 🔒 reserved-card discipline).
- **Live trigger index** `_backlog/triggers.md`: one row per deferred verdict that fails
  without it — object / ruling / one self-encountering observation / home; deferred
  verdicts do not auto-add rows; scan moments are change-archive closeout, the
  supersede-check before opening a new card, and stage closeouts. Seed harvest runs over
  the 19 archived cards under the admit bar (expected: 2–4 rows; "user names it" style
  triggers are rejected). The index is a pointer ledger, not a second truth home; the
  suspended-pool boundary is unchanged. It is NOT machine-gated for content semantics
  (borrowed ruling: semantic judgment is not mechanized); it IS covered by the existing
  relative-link rule via the checker's entry-chain scope.
- **Checker behavior** (`openspec/governance/check_doc_hygiene.py`, red-first per TDD):
  surface tables rename to the new paths; new hukou rule — every active card's first 12
  lines carry a `状态：` field whose word is in the declared per-zone vocabulary; new
  residency rule — an active card whose status line declares `毕业门：已过` or
  `可关闭：是` fails (anchored fields only; `等人拍板`/`未过`/`待触发` never match, so an
  honest awaiting-human card is never red-lined); `triggers.md` joins `ENTRY_DOCS` for
  link/newline coverage; self-test fixtures grow red-green pairs for both rules. The
  reverse roster direction (disk file must be indexed) is already enforced by the
  existing ledger rule and is deliberately not duplicated.
- **Live touchpoints synced in the same revision**: `required-paths.toml` (7 backlog
  path entries move; `_backlog/triggers.md` added), root `AGENTS.md` ledger cell
  (`plans / bugs` → `issues / bugs`, character-neutral against its 2425 ceiling),
  `openspec/README.md` step-1 label, `deep_research_harness/docs/control-map.md` (2
  links) and `testing-and-evaluation.md` (1 link) re-pointed to `_settled_issues/`.
- **Frozen history is not rewritten**: the ~30 `_backlog/plans/…` references inside
  `openspec/changes/archive/` stay as historical record; the 19 archived card bodies
  stay verbatim.

## Capabilities

### New Capabilities

<!-- none: the trigger index and the closure-conditions table are charter/process
     content (成文标准, human-executed), not machine behavior; the index's only machine
     surface is link resolution under the checker's existing entry-chain rule. -->

### Modified Capabilities

- `doc-truthfulness`: the "Ledger bookkeeping surfaces are machine-consistent"
  requirement is extended — surfaces rename (`issues/`, `_settled_issues/`,
  `_suspended_issues/`), and two new failure classes join the consistency surface:
  active cards without a vocabulary-checked `状态：` hukou, and active cards declaring
  `毕业门：已过` or `可关闭：是` (residency).

## Impact

- Moved (git mv, bodies unchanged): `_backlog/plans/` → `_backlog/issues/` (README only,
  plus the reborrow card migrates in at apply time); `_done/_closed_plans/` (19 cards) →
  `_done/_settled_issues/`; `_done/_suspended_plans/` → `_done/_suspended_issues/`.
- New: `_backlog/triggers.md`.
- Modified: `openspec/governance/check_doc_hygiene.py` (surface tables, two new rules,
  `ENTRY_DOCS`, self-test fixtures — no new script, no new dependency);
  `openspec/governance/required-paths.toml`; root `AGENTS.md` (one table cell);
  `openspec/README.md` (one label); `deep_research_harness/docs/control-map.md`,
  `deep_research_harness/docs/testing-and-evaluation.md` (link re-points);
  `_backlog/README.md`, `_backlog/issues/README.md`, `_backlog/bugs/README.md`,
  `_backlog/_done/README.md`, `_backlog/_done/_settled_issues/README.md`,
  `_backlog/_done/_suspended_issues/README.md`.
- Not touched: `deerflow/` gitlink (read-only, never modified or source-browsed by this
  change); `deep_research_harness/src/` behavior and tests; CI workflow; the archived
  change records under `openspec/changes/archive/`; the suspended-pool semantics
  (`_suspended_issues/` keeps its "explicit pause, needs a new ruling to revive" rules).

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` — the
  only behavior-bearing deliverable is the checker's renamed surface tables plus the two
  new red-first rules; every other edit is ledger bookkeeping and charter content that
  those rules (plus the existing gates) then hold in place.
- **Seam classification:** deterministic-guardrail — the changed behavior is red-first
  rules over textual/ledger facts; no model, prompt, state machine, or lifecycle outcome
  is touched.
- **Question:** Can the ledger's category name be made honest (`issues`) and the two
  observed failure classes — active cards without hukou, cards that declared graduation
  (`毕业门：已过` / `可关闭：是`) but never left the active zone, and deferred verdicts
  sinking without a visible surface — be held by machine and by charter, without
  creating a second truth home for deferred decisions?
- **Necessary adjacent/external contracts:** `doc-truthfulness` capability (answers: the
  ledger-consistency requirement this change extends); the project-structure manifest
  `required-paths.toml` (answers: the structural inventory the rename must keep green);
  the `_backlog/README.md` ritual (answers: the 编号/索引/计数三处一致 invariant the
  rename must preserve, and the closure-conditions table it gains); the borrowing-source
  records in `ai_dsh_assitant` (answers: which increments to adopt and which
  anti-patterns to refuse — "awaiting-human is not a completion word", "semantic
  judgment is not mechanized"); the issue card
  `_backlog/plans/2026-10-09-backlog-governance-reborrow.md` (answers: the full
  borrow/adapt/refuse decision record and the three user rulings).
- **Evidence seam:** red-first self-test pairs inside the doc-hygiene checker (residency
  red on a seeded `毕业门：已过` active card and a `可关闭：是` card; hukou red on a card
  missing `状态：` or using an out-of-vocabulary word; green on `等人拍板` and `未过`);
  rename receipts in the same revision (`git status` after the three moves, checker
  surface tables and `required-paths.toml` updated together); live-run receipts:
  `check_doc_hygiene.py` (incl. `--self-test`), `check_project_gate.py --phase
  plan/closeout`, `make verify` — all exit 0.
- **Not in scope:** a `methods/` directory (router table only); a card-migration
  lifecycle for `_reference/`; YAML frontmatter or `YYMMDD` card names; any 🔒
  reserved-card discipline; re-litigating the subjects of trigger rows (rows are
  pointers; owners unchanged); opening the work any trigger row points at.
- **Triggered review policies:** change-admission, local-context
