# Tasks

## 1. Gap D and the budget table

- [x] 1.1 Add the gap-D rationale to `deep_research_harness/AGENTS.md`'s boundary list:
      the nested-AGENTS.md prohibition exists to prevent entries created for their own
      sake; a sublayer that accumulates three or more standing rules only that layer
      needs re-opens the subtree-entry question through its owning change. Verify: the
      line exists and `python3 openspec/governance/check_doc_hygiene.py` still exits 0.
- [x] 1.2 Tighten and extend `DOC_BUDGETS` in `check_doc_hygiene.py`: root `AGENTS.md`
      2900 → 2500, `deep_research_harness/AGENTS.md` 8200 → 7000 (post-D measured
      baseline plus clean-hundred headroom), add `openspec/config.yaml` ≤ 12500 with a
      comment naming it the largest resident-injection layer; the two `CLAUDE.md` stubs
      stay at 400. Verify: `python3 openspec/governance/check_doc_hygiene.py` exits 0
      with the post-D tree under every ceiling (measure each file directly).

## 2. Defect fix and red proof (red-before-green)

- [x] 2.1 Fix the silent-skip defect in `_rule_doc_budgets`: a managed entry whose file
      is missing now fails loudly as a missing managed path (replacing the `continue`
      that assumed the link rule reports it — it does not cover the root instruction
      files). Red receipt: with the old code, deleting a managed file produced no
      budget violation; the self-test case in 2.2 proves the new red. Verify: the
      checker exits 0 on the real tree (all managed files present).
- [x] 2.2 Add two budget negative controls to the checker's `--self-test`: an
      over-limit fixture fails naming file/size/ceiling, and a missing managed file
      fails as a missing managed path. Verify:
      `python3 openspec/governance/check_doc_hygiene.py --self-test` exits 0 with the
      new cases included.

## 3. Governance wiring

- [x] 3.1 Register `DOB-001: doc-budgets — <description>` in
      `openspec/governance/req-registry.yaml` (apply writes the registry; planning only
      reserved). Verify: `python3 openspec/governance/check_project_reqs.py` exits 0.
- [x] 3.2 Update `openspec/governance/project-structure.toml` `requirement_ids` to add
      `DOB-001` with an accurate comment (no new structural paths, so
      `required-paths.toml` gains no section). Verify:
      `python3 openspec/governance/check_project_architecture.py` exits 0.
- [x] 3.3 Add `@impl DOB-001` to the `check_doc_hygiene.py` module docstring (the
      checker is the implementing owner). Verify:
      `python3 openspec/governance/check_project_req_coverage.py` exits 0.
- [x] 3.4 Create the main spec `openspec/specs/doc-budgets/spec.md` during apply (not
      by archive — native archive drops the `> req:` header line; the
      establish-project-structure lesson). Verify: `check_project_reqs.py` exits 0 with
      DOB-001 alive.
- [x] 3.5 Update `openspec/governance/README.md`: the doc-hygiene row gains the budget
      gate (managed resident files, character counts, ratchet). Verify: doc hygiene
      exits 0.

## 4. Verification (every exit code measured directly)

- [x] 4.1 Run the governance unittest suite, the aggregate closeout gate, doc hygiene
      (plain and `--self-test`), and `openspec validate add-doc-budget-gate --strict`
      plus `git diff HEAD --check` — all exit 0, measured directly.
- [x] 4.2 Record scope/diff evidence: `git status --porcelain=v1 --untracked-files=all`,
      `git ls-files --stage deerflow`, `git submodule status -- -- deerflow`, and
      review `git diff --submodule=short`; confirm the gitlink pointer is unchanged.

## 5. Closeout and archive

- [x] 5.1 Closeout review: compare the Change Focus against the actual diff and
      evidence; confirm the ceilings match the measured post-D baselines and the
      defect fix is covered by its red proof; every actionable finding becomes an
      unchecked task or an approved re-scope.
- [x] 5.2 After user approval, archive via `openspec archive add-doc-budget-gate`;
      re-run the aggregate gate (exit 0); mark gaps C and D absorbed in the DSH
      borrowing plan's landing table — completing A–F — and close the DSH plan per the
      three-README ledger ritual with the pointer handed off to the digest boundary
      plan.
