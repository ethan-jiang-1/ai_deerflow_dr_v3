# Tasks

## 1. Main spec and evidence anchor (red-before-green)

- [x] 1.1 Create the main spec `openspec/specs/project-structure/spec.md` carrying the delta's
      ADDED requirements into main-spec form: header lines `> req: PRS-001` plus exactly one
      `> structure: openspec/governance/project-structure.toml` before the first heading,
      the `## Purpose` section, and the three requirements with their scenarios. The main
      spec must be created during apply, not by archive: native archive copies Purpose and
      Requirements but drops the `> req:` and `> structure:` header lines, leaving the
      post-archive architecture and coverage checkers red (verified on a scratch copy;
      with the manual main spec, archive reports "already in sync" and changes nothing).
      Red is the already-measured state (this session's receipts:
      `check_project_architecture.py` exit 1 with `spec.reference_missing`). Verify green:
      `python3 openspec/governance/check_project_architecture.py` exits 0 with no
      `spec.reference_missing` error, and the main spec contains exactly one `> structure:`
      line, measured directly.
- [x] 1.2 Add the `@impl PRS-001` evidence annotation to the `check_project_architecture.py`
      module docstring (annotation only; no rule-semantics change). Verify green:
      `python3 openspec/governance/check_project_req_coverage.py` exits 0 (red was exit 1,
      same session receipts).
- [x] 1.3 Verify the append-only registry without editing it: the `PRS-001` entry description
      in `openspec/governance/req-registry.yaml` matches the established spec. Verify green:
      `python3 openspec/governance/check_project_reqs.py` exits 0 (red was exit 1, orphan
      PRS-001 reported).

## 2. Governance verification (every exit code measured directly, never through a pipe)

- [x] 2.1 Run the governance unittest suite `python3 -m unittest discover -s openspec/tests/governance -q`
      from the repository root and confirm it stays green (exit 0) — the checkers' existing
      negative controls keep proving the guards can fail.
- [x] 2.2 From `deep_research_harness/`, run `UV_OFFLINE=1 make verify` and confirm exit 0;
      the Harness gate neither reads, imports, executes, nor links OpenSpec content.
- [x] 2.3 Run the aggregate gate `python3 openspec/governance/check_project_gate.py --phase closeout`
      from the repository root and confirm exit 0 (all six component checkers green). Record
      the command and exit code as the closeout receipt. Separately run the standalone
      document-hygiene checker `python3 openspec/governance/check_doc_hygiene.py` (exit 0) —
      it is not part of the aggregate gate and is verified on its own.
- [x] 2.4 Run `openspec validate establish-project-structure --strict` (exit 0) and
      `git diff HEAD --check` (exit 0) from the repository root.

## 3. Scope, diff, and generation-alignment evidence

- [x] 3.1 Record the supplementary scope/diff evidence: `git status --porcelain=v1 --untracked-files=all`,
      `git ls-files --stage deerflow`, `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
      `git diff --submodule=short`; confirm the gitlink pointer still matches the declared
      `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7` and no pointer bump is proposed. This
      evidence is supplementary scope review; it approves no pointer bump and proves no
      upstream runtime compatibility.
- [x] 3.2 Confirm generation alignment: `openspec --version` equals the `generatedBy`
      frontmatter in `.agents/skills/*/SKILL.md` (frontmatter read-only; `.agents/skills/`
      is a user-reserved area). Any mismatch is recorded as drift and resolved or explicitly
      accepted before archive.

## 4. Vertical slice walkthrough (first journey through the change loop)

- [x] 4.1 Walk THIS change through the five-question slice and record the walkthrough with the
      closeout evidence: (a) the user-observable result stated in two lines (what a fresh
      agent gains, how to observe: gate exit codes); (b) owner reachability from the task
      description without the author's help; (c) where durable tradeoffs are recorded
      (design.md Decisions) and which were exempted as mechanical; (d) which evidence fails
      on the old behavior (the three red checker receipts, red-before-green); (e) per-step
      evidence state marked as file-pointable, verbally claimed, or absent.
- [x] 4.2 Produce the three lists from the walkthrough — links that do not open, owners that
      required guessing, claims without evidence — and backfill them into
      `_backlog/plans/2026-10-02-borrow-dsh-harness-gap-analysis.md` (item E).

## 5. Closeout and archive

- [x] 5.1 Closeout review: compare the proposal's Change Focus against the actual tasks,
      delivered diff, and evidence; every actionable finding becomes an unchecked task here
      or an explicitly approved re-scope; no silent narrowing of the approved outcome.
- [ ] 5.2 After explicit user approval, archive via `openspec archive establish-project-structure`;
      confirm archive reports the main spec as already in sync (no requirement duplication),
      then re-run `python3 openspec/governance/check_project_gate.py --phase closeout` (exit 0)
      and `openspec list --specs` reporting `project-structure`, and close the roadmap
      plan per its step 4 (git mv plus the three-README ledger ritual).
