# Tasks

## 0. Alongside — ledger ritual maintenance (outside change scope, per plan routing)

- [x] 0.1 B3: move the CLS-012 row from after the card-template code fence into the
  "已归档" table in `_backlog/plans/README.md` (row content unchanged). Verify: the row
  sits inside the table (cell count 4 per row) and
  `python3 openspec/governance/check_doc_hygiene.py` exits 0.
- [x] 0.2 B4: update the `_backlog/README.md:3` "最后更新" header to reflect CLS-012
  (and this change's plan card, already recorded). Verify: header date/entry matches
  the newest ledger row; doc-hygiene checker exits 0.
- [x] 0.3 B5: remove the blank lines shattering the `_closed_plans/README.md` table
  (CLS-006..012 rows). Verify: every table row has 4 cells and renders as one table;
  doc-hygiene checker exits 0.
- [x] 0.4 B2: fix `_backlog/_done/_suspended_bugs/README.md:9`'s pointer to the
  nonexistent "Suspended" section in `_fixed_bugs/README.md` (repoint to the actual
  suspended-plans README or drop the sentence). Verify: `git grep -n "Suspended"`
  resolves to an existing section or is gone; doc-hygiene checker exits 0.

## 1. Root layer (`README.md`, root `AGENTS.md`)

- [x] 1.1 A2: correct `README.md:19` counts to measured reality (11 capability specs,
  31 archived changes) with an as-of note; keep "活跃为空". Verify: `ls
  openspec/specs | wc -l` = 11 and `ls openspec/changes/archive | wc -l` = 31 match the
  text; `git grep -n "29 个 changes"` returns nothing.
- [x] 1.2 B1: remove the nonexistent `scripts` from root `AGENTS.md:7`'s layer table.
  Verify: `git grep -n 'scripts' AGENTS.md` returns nothing; doc-hygiene checker exits
  0 and root AGENTS.md measures at or under 2435 chars.
- [x] 1.3 B8: rewrite `README.md:35`'s root-residents claim so `config.yaml`/`.env`
  read as prepared-on-demand (not present residents), and disambiguate from the
  existing `openspec/config.yaml`. Verify: text no longer asserts present existence;
  `test ! -f config.yaml` still true and consistent with the wording.

## 2. Harness doc layer

- [x] 2.1 A3: re-scope `docs/known-limitations.md` to genuinely ongoing items — move
  resolved rows (CI lane, recursion limit, checkpoint delta) and the landed-guard row
  into a "已处置" pointer line naming the owning archived changes; keep the two ongoing
  rows and the delta-patch caveat. Verify: every remaining table row names a live
  limitation; `git grep -c "已修\|已解决" docs/known-limitations.md` only matches the
  pointer line; make verify exits 0.
- [x] 2.2 B7: qualify the bare `client.py:293` references to the upstream path
  (`deerflow/backend/packages/harness/deerflow/client.py:293`) in
  `docs/known-limitations.md` and in the `src/.../runtime/client.py:18` comment
  (comment-only edit, zero behavior). Verify: `git grep -n "client.py:293"` shows the
  upstream-qualified form at both sites; `UV_OFFLINE=1 make verify` exits 0.
- [x] 2.3 C6: fix the duplicate "级 3" in `docs/testing-and-evaluation.md`'s surrogate
  ladder (行为断言 becomes 级 4). Verify: the table lists levels 1,2,3,4 exactly once
  each; `git grep -n "级 3" docs/testing-and-evaluation.md` matches one row only.
- [x] 2.4 C7: shrink closed-out history to pointers — the 借鉴队列 section in
  `docs/testing-and-evaluation.md` to one line pointing at plan card CLS-010, the
  playbook receipt-history block (`playbook/run-research.md:77-90`) to the receipt
  rule plus a pointer, and the archaeology numbers out of
  `docs/known-limitations.md` (kept in the owning archived changes). Verify:
  `git grep -n "106 tests\|23→86→209" deep_research_harness/` returns nothing; make
  verify and doc-hygiene checker exit 0.
- [x] 2.5 C4: consolidate the gotcha lists — `docs/local-operations.md:13-20` keeps at
  most one environment fact and points at `playbook/run-research.md`'s 坑 section as
  the holder; the playbook keeps the full list. Verify: the three duplicated gotchas
  (--config eaten, .env credentials, smoke traceback) appear in full in exactly one of
  the two files.
- [x] 2.6 B10: fix `README.md:45` (harness) — remove the live dangling phrase
  "+ the boundary plan above" (the only boundary mention in the file, with no such
  plan above it) and rename the "v3 direction note" link label to its real target
  (the AGENTS.md introduction). Verify: `git grep -n "boundary plan"
  deep_research_harness/` returns nothing; the label text matches content present at
  the link target.
- [x] 2.7 B6: turn the retired requirement-ID mentions into pointers —
  `COMMANDS.md:5` (ENS-001), `docs/quality-register.md:1` (RT10),
  `playbook/run-research.md:43` (RLF-001) each name the archived retiring change
  (`2026-10-04-remove-requirement-id-tracking`) as the trace. Verify: `git grep -n
  "ENS-001\|RT10\|RLF-001" deep_research_harness/` shows every hit co-located with the
  archive pointer.
- [x] 2.8 C1 (doc-layer surfaces): collapse the `make verify` recitals in harness
  `README.md:31`, `docs/local-operations.md:10`, `docs/testing-and-evaluation.md:13`,
  `docs/quality-register.md:14`, `playbook/run-research.md:11-17`, and the Makefile
  header comment to one keyword + pointer to `COMMANDS.md` (the semantic owner);
  COMMANDS.md itself is unchanged. Verify: the phrase "不读" / "neither reads" for
  OpenSpec-independence appears in full form only in COMMANDS.md within
  `deep_research_harness/`; command-surface guard stays green via the full gate.

## 3. openspec layer

- [x] 3.1 A1: correct `openspec/governance/README.md` — the command block lists the six
  real component checkers per `check_project_gate.py` `CHECKER_NAMES`
  (check_proof_receipts.py in, check_release_face.py moved to the standalone paragraph);
  the "何时读" table gains rows for `check_proof_receipts.py`,
  `selected-change-closeout.md/.py`, `change_guidance_kernel.py`,
  `portable_change_guidance_export.py`; the CI canonical-sequence sentence includes the
  setup-uv + `make smoke` step. Verify: the enumeration equals `CHECKER_NAMES` exactly;
  `python3 openspec/governance/check_project_gate.py --phase closeout` exits 0 and
  `python3 openspec/governance/check_ci_governance.py` exits 0.
- [x] 3.2 B9: repair `openspec/change-guidance/local/deep-research.md:12-19` —
  merge the truncated "Context Expansion Gate" fragment and the duplicated sentence
  into one section with one statement of the seam routing. Verify: the sentence "start
  from `domain/`" (and its Chinese-free English equivalents) appears exactly once in
  the file; doc-hygiene checker exits 0.
- [x] 3.3 C8: remove the untracked `.pi/tasks/` residue directory (and the `.pi` tree
  if empty). Verify: `test ! -d .pi` succeeds; `git status --porcelain=v1
  --untracked-files=all` shows no `.pi` entries.

## 4. v3 narrative consolidation (C5, cross-layer)

- [x] 4.1 Keep the full v3 telling in root `README.md` only; shrink the retellings in
  root `AGENTS.md` (table note), `_backlog/README.md:19` (§这个仓库是什么), harness
  `README.md:7-10`, and harness `AGENTS.md:8-10` to one sentence + pointer. Verify:
  the phrase "lead agent" appears in full narrative form only in root README.md among
  these five files; all five still route to the full telling.

## 5. Resident `AGENTS.md` edits (last — tightest budgets)

- [x] 5.1 A6: add the half-sentence reconciliation to harness `AGENTS.md:4`
  (runtime-independence vs structure-owned-by-governance). Verify: both claims remain
  and the reconciling clause connects them; file measures at or under 6864 chars;
  doc-hygiene checker exits 0.
- [x] 5.2 A7: add the one-line "when it is not ordinary work" criterion for upstream
  source-browsing (the LLM-Node gate's inspect-builder step qualifies) next to the
  read-only rule in harness `AGENTS.md:5-6`. Verify: the criterion sentence co-locates
  with the prohibition; marker rule stays green.
- [x] 5.3 A8: de-dangle the `agents/` first-read in harness `AGENTS.md:59` — annotate
  that the owning contracts do not exist yet (wording free of all seven declared
  markers, e.g. "空层；契约随 owning code 落地"). Verify: `git grep -n "agents/"
  deep_research_harness/AGENTS.md` shows the annotation; doc-hygiene checker exits 0
  (marker rule included).
- [x] 5.4 C1 (harness AGENTS.md): shrink the Verification section's verify recital to
  the seam facts + pointer to COMMANDS.md. Verify: file measures at or under 6864
  chars after all group-5 edits; doc-hygiene checker exits 0.

## 6. Closeout (per `openspec/config.yaml` rules.tasks)

- [x] 6.1 Collect A-class before/after receipts: for each of A1-A8, one `git grep`
  showing the old claim is gone and the corrected text present. Verify: eight pairs
  of receipts attached to the closing commit message or change notes.
- [x] 6.2 Measure resident budgets after all edits (root `AGENTS.md`, harness
  `AGENTS.md`, `openspec/config.yaml`, plus the other declared files) and record the
  numbers in the change's closing notes for the follow-up governance change's
  ratchet-down. Verify: every measured size at or under its declared ceiling; numbers
  recorded.
- [x] 6.3 Run the full gate from the repo root: `python3
  openspec/governance/check_project_gate.py --phase closeout`. Verify: exit code 0
  read directly (no pipe).
- [x] 6.4 From `deep_research_harness/`, run `UV_OFFLINE=1 make verify`. Verify: exit
  code 0 read directly.
- [x] 6.5 From the repo root, run `openspec validate doc-hygiene-second-sweep --strict`
  and `git diff HEAD --check`. Verify: both exit 0 read directly.
- [x] 6.6 Record scope/diff evidence: `git status --porcelain=v1
  --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status --
  deerflow`, `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
  `git diff --submodule=short`. Verify: outputs recorded in the closing notes;
  gitlink pointer unchanged from `ceebf97f`.
- [x] 6.7 Confirm generation alignment: `openspec --version` equals the `generatedBy`
  frontmatter in `.agents/skills/*/SKILL.md` (read-only check over the user-reserved
  area). Verify: versions equal, or the mismatch is recorded as drift for resolution
  before archive.
