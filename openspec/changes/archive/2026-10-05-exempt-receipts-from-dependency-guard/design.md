# Design

## Context

The dependency-direction checker (`openspec/governance/check_harness_dependency_direction.py`,
43 lines) scans every file under `deep_research_harness/` via `rglob` — tracked or not,
minus `IGNORED_PARTS` — for the literal tokens `openspec/`, `../openspec`,
`openspec.governance`. Its semantics currently live only in its docstring; unlike
`check_ci_governance.py` (CIG-001), `check_doc_hygiene.py` (DOB-001),
`check_release_face.py` (RLF-001), and `check_project_architecture.py` (PRS-001), it
has no capability spec and no `@impl` registration, and no test in the governance
unittest suite.

The false positive: `deep_research_harness/docs/skills/deep-research/verification-receipt.json`
records the governance command argv that verified the skills snapshot, and the argv
text contains `openspec/`. The file is invisible to git because the root `.gitignore`
rule `skills/` (comment: "Runtime-materialized profile root (configure.py writes the
public skill here)") is unanchored and matches any depth — but `configure.py` has not
existed since the v3 scaffold, and nothing writes a root `skills/` directory today.
The receipt convention across the repo (archive receipt, backlog receipt, skills
receipt) shares an invariant core: a top-level `checks` list of command records, with
`revision` and `completed_at` present. This red light is Phase 0 item 2 of
`_backlog/plans/2026-10-05-runtime-test-interaction-architecture.md` and blocks the
closeout gate on any machine holding such a receipt.

Operator ruling (this session): design A — structural checker exemption plus gitignore
narrowing, with the receipt becoming tracked evidence. Alternatives (receipt
relocation out of the harness tree; rewording receipt records to avoid the literal
token) were rejected — the first drops in-place evidence for the skills snapshot, the
second damages receipt honesty and recurs on every governance run.

## Goals / Non-Goals

**Goals:**

- The closeout gate is green on a tree that contains a valid harness-tree
  verification receipt — on every clone, not just ones without receipts.
- The exemption is structural and locked: recognition depends on what a file *is*
  (JSON receipt shape), not what it is *called*; planted violations in the governance
  unittest suite prove the guard still bites.
- The evidence file is tracked, registered, and its deletion fails architecture
  governance.

**Non-Goals:**

- No exemption for any other class (docs, prose, configs): a doc or config file that
  references `openspec/` still trips. `docs/runtime-map.md` today mentions `openspec`
  without a slash and passes; that distinction is preserved untouched.
- No changes to the forbidden-token set, the gate inventory, the CI workflow, other
  checkers, or the receipt format.
- No harness doc/runtime reorganization — those are later phases of the 2026-10-05
  plan, unblocked by this change.
- No machine-written receipt schema authority: receipts stay runner-written; the
  checker only recognizes the invariant shape they already share.

## Decisions

1. **Recognition predicate (structural, at file level).** A harness-tree file is an
   exempt verification receipt iff: its name is exactly `verification-receipt.json`;
   `json.loads` succeeds and yields a dict; `checks` is a non-empty list; every item
   in `checks` is a dict carrying a `command` key. The non-empty conjunct closes the
   vacuous-truth hole — `{"checks": [], "notes": "... openspec/ ..."}` is not a
   receipt and stays scanned. A recognized receipt is skipped entirely — the whole
   file is a command record, so any text inside it is evidence, not dependency. A
   file that fails any conjunct is scanned normally.
   *Alternatives rejected:* filename-only exemption (nominal — a rename hides a real
   reference); requiring `schema_version` (the skills receipt doesn't carry it);
   directory-restricted exemption (too narrow for future receipts); exempting only
   text inside `checks[].command` (over-fit, and the file's other fields — digests,
   observations — are equally evidence).

2. **Fail-safe direction.** Recognition failure means *scanned*, never *exempt*: a
   malformed or fake receipt containing a forbidden token trips the checker exactly
   as before. The only behavior that changed is: structurally valid receipts stop
   being flagged.

3. **Order of filters unchanged.** `IGNORED_PARTS` first (cheap path-parts check),
   then receipt recognition (JSON parse) for files with the receipt name, then the
   token scan for everything else. The scan keeps covering untracked files — the
   guard's subject is the tree as it exists; a dependency smuggled via an untracked
   file is still a dependency (pinned as a spec scenario).

4. **gitignore anchoring.** `skills/` becomes `/skills/`: the rule keeps ignoring a
   repo-root runtime-materialized `skills/` directory (its original intent) and stops
   matching `deep_research_harness/docs/skills/`. The two `!.agents/skills/` negation
   lines stay unchanged — with the anchored pattern they are no-ops, kept as
   defensive documentation so the tracked skill set survives any future re-broadening
   of the pattern.
   *Alternative rejected:* deleting the rule outright — a future profile tool that
   materializes a root `skills/` would then pollute `git status`; anchoring preserves
   intent at zero cost.

5. **Receipt disposition: track + register, content untouched.** The existing file is
   added to git as-is (its `scope` and `unverified` fields already declare it
   historical evidence, not a current-behavior claim) and registered in
   `required-paths.toml` inside `[paths.repo-skeleton]` next to its siblings
   (`SKILL.md`, `provenance.json`, …). No group moves: groups carry existence
   semantics only, and minimal churn is a virtue. The new test file is registered in
   the same group, adjacent to the checker's existing entry.
   *Alternative rejected:* leaving it untracked-visible — permanent `git status`
   noise, losable evidence, and machine-dependent checker relevance.

6. **Test seam: governance unittest, fixture trees, subprocess exit codes.** New
   `openspec/tests/governance/test_harness_dependency_direction.py`, modeled on
   `test_release_face.py`: non-git temp fixture trees, the checker invoked as a
   subprocess with the fixture root passed as its `project_root` argument (the
   precedent's exact pattern), exit codes read from `returncode` directly — never
   through a pipe, per the governance README's own warning. Three fixtures:
   (a) valid receipt recording `openspec/` command argv → exit 0 (red on the current
   checker — the red-first proof);
   (b) a `.py` file carrying `openspec/` → exit 1 naming file and token;
   (c) a `verification-receipt.json` with non-receipt content carrying `openspec/` →
   exit 1 (locks decision 1 and 2), plus the empty-`checks` shape `{"checks": [],
   ...}` carrying a token → exit 1 (locks the non-empty conjunct).
   The suite also asserts the real repository tree exits 0, locking the closeout
   criterion into the standing suite (this assertion is red on the current checker
   too — the very false positive this change removes).
   *Alternative rejected:* a `--self-test` flag inside the checker (the
   `check_doc_hygiene.py` route) — one mechanism suffices; the unittest suite is
   already in the CI canonical sequence, so the controls run everywhere the gate's
   components run.

7. **Spec home and `@impl` marker.** The new `dependency-direction` capability owns
   the guard's behavior; the checker docstring gains `@impl DEP-001` and the
   `project-structure.toml` comment block registers the ID (following CIG/DOB/RLF/PRS
   — DEP is the 3-letter prefix for dependency-direction). The governance README row
   for the checker is updated to name the exemption and the marker, mirroring the
   doc-hygiene row's style.

## Risks / Trade-offs

- [A real dependency hides inside a crafted `{"checks": [...]}` file] → The negative
  control (fixture c) fails loudly on shape mismatch; nothing in the harness runtime
  reads receipts as configuration, so a fake receipt cannot execute anything — the
  realistic loss is scan coverage of one deliberately crafted file, visible in any
  diff as a new receipt-named file.
- [Exemption wording drifts from the actual receipt convention as receipts evolve] →
  The predicate pins the invariant core (`checks` command records) that all three
  existing receipts share; a future receipt shape that drops it fails safe (scanned),
  and the fix is a one-conjunct change with its own red fixture.
- [Anchoring `skills/` un-ignores a directory someone expected ignored] → Verified:
  the only on-disk `skills/` directories are `.agents/skills/` (tracked, negated),
  `deerflow/skills/` (inside the gitlink, outside this repo's index), and
  `deep_research_harness/docs/skills/` (tracked files + the receipt being tracked
  here). `git check-ignore` assertions cover both sides in the closeout receipt.
- [Doc-hygiene budget ratchet trips on the README row edit] → The row edit stays
  within the file's current measured size; `check_doc_hygiene.py` runs in closeout
  evidence before archive.

## Migration Plan

Single-forward cutover, no persisted runtime state:

1. Land the checker exemption + unittest (red-first: fixture (a) fails before the
   checker change, passes after).
2. Anchor the gitignore rule; `git add` the receipt (content unchanged); register
   both new paths in `required-paths.toml`; update the checker docstring marker,
   the `project-structure.toml` comment, and the governance README row.
3. Closeout evidence: governance unittest suite (includes the new file), the checker
   itself, the closeout gate, doc hygiene, architecture checker, `make verify`,
   `git check-ignore` both ways, `git diff --check` — all exit codes read directly,
   recorded fresh in the change's verification receipt.

Rollback: revert the file edits and `git rm --cached` the receipt; the tree returns
to the pre-change state (red on machines holding receipts — the known defect — and
green elsewhere). No data migration, no schema, no upstream contact.

## Open Questions

None material to the approach. One deferred nicety: whether future receipts should
carry a machine-declared `schema_version` is a receipt-format question owned by the
delivery-lanes closeout convention, not by this guard; the predicate deliberately
does not require it.
