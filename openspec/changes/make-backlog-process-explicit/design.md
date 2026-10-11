# Design

## Context

The ledger institution was last consolidated by `adopt-issue-ledger-governance`
(2026-10-09, CLS-019): charter, two-track templates, hukou/residency word tables, the
triggers index, the methods library, and the checker's rule 7. The issue card
`2026-10-12-backlog-process-made-explicit` (borrowed from the same-lineage
`ai_dsh_loop_advisor`, 2026-10-12) re-audited that shape against the source card's seven
gaps; six hold here. Constraints that shape this design: the status line — not YAML
frontmatter — is the card's one home (刻意不借 N2); the checker's rule 7 anchors
vocabulary membership and residency; `DOC_BUDGETS` ceilings ratchet downward;
`ENTRY_DOCS` / `DOC_BUDGETS` are closed declaring lists whose expansion is itself a
visible change; zero active bug cards exist today; the only implementation channel is an
OpenSpec change with the owner's 拍板 at the propose admission boundary.

## Goals / Non-Goals

**Goals:**

- Every rule an agent must obey inside `_backlog/` is either machine-anchored or one
  pointer away from the doorplate.
- The bug walk carries its own authorization semantics (who may write the propose) and
  confirmation semantics (what proves fixed) without touching the propose-boundary law.
- Flip laws live in exactly one home (the charter); the machine anchors only what it can
  decide mechanically (vocabulary membership, residency fields, links, budgets).

**Non-Goals:**

- No new checker failure class: the per-state must-have-section family (验收在场性)
  stays under-pressure — recorded, not landed.
- No frontmatter, no `blocked` word, no graduation closed-head field, no card backfill.
- No change to the propose admission boundary, the numbering ritual, the suspended-pool
  semantics, or the one-at-a-time release discipline.

## Decisions

**D1 — The fix-ready authorization is propose-authority, not landing-authority.** The
source repo's ruling ("the fix-ready defect card carries its own fix authorization")
meets this repo's law that a card's status grants no implementation authority and that
every change stops at the propose boundary for the owner's 拍板. Local landing: the
`修就绪` flip authorizes **writing the propose** (planning artifacts) without a separate
owner green-light to start; the owner still rules at the admission boundary; the
exception set (P0 / contract / spec semantics / out-of-bounds-irreversible / a recorded
decision — the root REVIEW-节制 categories) does not even get propose-authority — it
routes through the owner or the issue path. Both laws stay intact instead of either
gaining a hole.

**D2 — One home per fact, on the status line.** The current phase lives in the 状态行
word (checker-anchored); history lives in card-body appends (verdict / destination /
retraction); coarse position lives in the directory (位置即状态). The flip laws are
charter tables — human discipline — because a flip's guard ("the next step is an owner
choice", "root cause confirmed with evidence") is a semantic judgment, and this repo has
already ruled semantic judgment is not mechanized (刻意不借: 触发器语义门禁化). The
machine keeps anchoring exactly what it anchored before: membership + residency + links
+ budgets.

**D3 — Vocabulary values move in one revision; the rename is migration-free.** The
checker table, both README word tables, and the charter tables land in the same
revision; zero active bug cards means no card carries the old `活跃` word, so the rename
cannot strand a card — a post-rename `活跃` card is out-of-vocabulary by design and
fails loudly (the self-test negative pins this). `待修` keeps its parked semantics
(suspended pool: diagnosed, unscheduled) and stays distinct from `修就绪` (ready AND
authorized, active zone).

**D4 — The doorplate is additive and budgeted.** `_backlog/AGENTS.md` states the
subdirectory positions, the two walks, the two ticket conditions, and the status
vocabularies at doorplate depth, pointing at the manual and methods for every fact — no
duplication, because the resident chain is the denominator of every prompt (the
platform's whole-chain budget drops broader files first). It joins `ENTRY_DOCS`
(link/newline coverage) and `DOC_BUDGETS` (a ceiling measured at adoption with a
justification comment). Root `AGENTS.md` routing stays unchanged — the doorplate reaches
agents through fs-touch injection, not through root routing churn.

**D5 — skip_specs.** All machine changes ride already-spec'd mechanisms:
doc-truthfulness owns vocabulary-membership hukou ("adding … a status vocabulary … to
management is a visible change to the declaring tables") and managed-surface links
("expanding the managed-surface list is a visible change to the declaring table");
doc-budgets owns the budget gate ("adding a file to management is a visible change to
the declaring table"). No requirement statement changes; inventing one to satisfy
validation is forbidden by the authoring route.

## Alternatives

- **README-only rules (no doorplate)** — rejected: rules that reach an agent only if the
  agent chooses to read are exactly the pull-only gap the audit named; the platform
  auto-injects nested AGENTS.md on fs touches, so a doorplate reaches agents that land
  in the area without a routing choice.
- **YAML frontmatter lifecycle (the source repo's carrier)** — rejected: 刻意不借 N2
  stands (two header conventions are pure cost); the status line is already the
  anchored home and the archive's vocabulary.
- **Per-fix issue RFC (every bug fix rides an issue deliberation first)** — rejected by
  the owner at the source: the bug card is the work item; this repo's propose boundary
  already carries the human gate.
- **Keep `活跃`** — rejected: it collides with "活跃区" once multiple active-zone words
  exist; the gerund (`调查中`) restores symmetry with `推敲中`; zero active bug cards
  make the rename free now and expensive later.
- **A `blocked` status word** — rejected: a card is reader-consumed and its dependencies
  ride in 修好判据 / 下一步; the platform's goal machine needs `blocked` because an
  autonomous loop must self-report an impasse — a ledger card does not.
- **Forward-only flips** — rejected: falsification (BUG-001's 初判修正 precedent) would
  churn cards; backward flips are lawful with guards.
- **Land the per-state must-have-section checker family now** — rejected: under-pressure
  per the upstream ruling and this repo's promote-on-recurrence philosophy; a `修就绪`
  card without 修好判据 is NOT flagged — recorded honestly as the deferred family.
- **A line↔frontmatter mirror cross-check (the source repo's gate honesty item)** —
  superseded by D2: with one home there is nothing to mirror.

## Risks / Trade-offs

- [Doorplate budget creep] → ceiling measured at adoption in `DOC_BUDGETS`; the ratchet
  only goes down; the doorplate owns positions and pointers, not facts.
- [Charter tables and checker table desync mid-apply] → all declaring surfaces land in
  one revision (D3); the hukou rule turns any desync red at the first card written per
  the stale surface.
- [Flip tables become a second truth home for process facts] → the charter IS the
  process law's home; READMEs point, never copy; the checker anchors values, not prose.
- [A `修就绪` card without 修好判据 passes the checker] → known and recorded (D5 /
  Alternatives): the acceptance-presence family is under-pressure; the ticket condition
  is charter discipline until recurrence promotes it.

## Migration Plan

Single revision: charter + both READMEs + doorplate + checker tables +
`required-paths.toml` land together. Red-first order inside the revision: the checker
self-test's new negatives are added and proved red against the old vocabulary, then the
vocabulary flips and the battery goes green. Rollback: single-commit revert; no data, no
runtime state, no card bodies touched.

## Deviation Register

none: no implementation deviations at design time; apply-time discoveries append here
with their ruling basis and landing place.
