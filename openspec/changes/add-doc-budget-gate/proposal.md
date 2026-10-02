# Proposal

## Why

The entry layer's budget gate already half-exists: `check_doc_hygiene.py` carries a
`DOC_BUDGETS` table (inherited from v2) with character ceilings over four resident
instruction files — but it does not manage `openspec/config.yaml` (the largest
resident-injection layer, over twelve thousand characters), its ceilings are v2-era
numbers far above v3's measured sizes, a managed file that goes missing is silently
skipped instead of failing, the rule has no negative-control self-test, and the whole
behavior is unspec'd. The DSH borrowing analysis (gap C) prescribes completing the
gate: a machine-enforced, ratcheted, character-counted budget over the resident layer.

## What Changes

- Extend the `DOC_BUDGETS` table in `check_doc_hygiene.py`: add
  `openspec/config.yaml` ≤ 12500 (deliberately tight against its measured 12.2k to stop
  further growth); tighten the v2-era ceilings to v3's measured post-D baselines with
  clean-hundred headroom — root `AGENTS.md` 2900 → 2500 (measured 2323),
  `deep_research_harness/AGENTS.md` 8200 → 7000 (measured ~6.7k pre-D); the two
  `CLAUDE.md` stubs stay at 400.
- Fix the silent-skip defect: a `DOC_BUDGETS` entry whose file is missing now fails
  loudly as a missing managed path (previously skipped on the assumption the link rule
  would report it — it does not cover the root instruction files).
- Add budget negative controls to the checker's `--self-test` (over-limit fixture red;
  missing managed file red) — the rule has never had a red proof.
- Establish the `doc-budgets` capability (DOB-001): the delta spec owns the budget
  behavior that is currently unowned — declared ceilings over managed resident files,
  character counting, loud failure naming file/size/ceiling, missing-managed-path
  failure, and the ratchet discipline (ceilings only go down; raising one requires a
  one-line justification recorded next to the entry).
- Fold in gap D (its designated carrier: this change's diff touches
  `deep_research_harness/AGENTS.md`): the `Do not add nested AGENTS.md files` boundary
  gains its in-place rationale (prevents entries created for their own sake) and its
  escalation condition (a sublayer that accumulates three or more standing rules only
  that layer needs re-opens the subtree-entry question through its owning change).

## Capabilities

### New Capabilities

- `doc-budgets`: owns the required behavior of the entry-layer budget gate — declared
  character ceilings over managed resident instruction files, loud failure on
  over-limit and on missing managed paths, and the ratchet discipline for ceiling
  changes.

### Modified Capabilities

(none — the budget rule joins the existing doc-hygiene checker, whose other rules are
unchanged)

## Impact

- Modified: `openspec/governance/check_doc_hygiene.py` (budget table extension,
  ceiling tightening, missing-managed-path fix, self-test cases, `@impl DOB-001`),
  `deep_research_harness/AGENTS.md` (gap-D rationale line),
  `openspec/governance/req-registry.yaml` (DOB-001 registration in apply),
  `openspec/governance/project-structure.toml` (requirement IDs + comment),
  `openspec/governance/README.md` (doc-hygiene row gains the budget gate).
- New: the delta spec for `doc-budgets` (DOB-001); no new data files, no new checkers.
- No application code, no CI workflow change (doc hygiene is already in the CI
  canonical sequence, so the completed budget gate rides it), no harness runtime
  behavior.

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` — its `DOC_BUDGETS` table owns the ceilings and the managed-file list, and the checker is the enforcing surface.
- **Seam classification:** deterministic-guardrail — the changed observable behavior is a machine-checked budget validation (exit codes); no model cognition is involved.
- **Question:** How does the half-existing entry-layer budget gate get completed — the largest resident file managed, ceilings tightened to measured v3 baselines, the missing-managed-path defect closed, red proof added — and its behavior spec-owned?
- **Necessary adjacent/external contracts:** `openspec/governance/check_doc_hygiene.py`'s self-test harness (answers: how the budget rule gains negative controls in the checker's built-in mechanism); `openspec/governance/project-structure.toml` (answers: the owner-ID declaration per the architecture-policy protocol, with no new structural paths); `deep_research_harness/AGENTS.md` (answers: where the gap-D rationale lands and its effect on the measured baseline).
- **Evidence seam:** the extended checker's direct exit codes with built-in self-test negative controls (over-limit red, missing-managed-file red), the governance unittest suite staying green, and the aggregate gates passing.
- **Not in scope:** reducing any current ceiling below its starting point (a separate decision with its own change), machine enforcement of the no-raise ratchet via git history (review-level discipline, honestly stated), spec coverage of doc-hygiene's pre-existing checks, and any CI workflow change.
- **Triggered review policies:** change-admission
