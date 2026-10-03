# Tasks

## 1. Posture + guard (red-before-green)

- [x] 1.1 Write `tests/unit/test_subagent_posture.py`: both checked-in configurations Receipt: red = the posture assertions failing (blocks absent) — measured.
      declare the no-custom-subagents posture block; the depth self-check fails for any
      declared custom subagent lacking `task` in its `disallowed_tools` (negative
      control on a temp copy: a violating declaration turns the check red, restoring
      turns it green); the guard is dependency-free (stdlib text scanning). Verify:
      discovery exits 1 with the posture assertions red (the configs do not declare the
      posture yet — measured).
- [x] 1.2 Add the posture block (commented `subagents:` section with the decision and Receipt: green (87/87); the negative control proves the guard red on a violating declaration naming config/offender/remedy.
      the future path) to `config/base.yaml` and `config/fixture.yaml`. Verify:
      discovery exits 0 (green receipt) and the negative control still proves red
      against a violating temp fixture.

## 2. Ledger ritual: close the wiring plan

- [x] 2.1 `git mv _backlog/plans/2026-10-02-wiring-structure.md Receipt: wiring plan moved as CLS-006; three READMEs synced; no stale plans/ links; doc hygiene green.
      _backlog/_done/_closed_plans/` and sync the three READMEs (CLS-006 row with the
      decision-5 disposition verbatim, Next ID CLS-007, counts and stamps; stale
      `plans/` links updated). Verify:
      `grep -rn "plans/2026-10-02-wiring-structure" _backlog/` returns no active-plan
      links and `python3 openspec/governance/check_doc_hygiene.py` exits 0.

## 3. Verification (every exit code measured directly, no pipes)

- [x] 3.1 From `deep_research_harness/`: `make verify` exits 0 (UV_OFFLINE=1 honored). Receipt: VERIFY=0, UV_VERIFY=0, GOV_SUITE=0, ARCH=0, CLOSEOUT=0, STRICT=0, DIFFCHECK=0.
      From the repository root: the governance unittest suite exits 0, the architecture
      checker exits 0, `check_project_gate.py --phase closeout` exits 0,
      `openspec validate pin-subagent-knobs --strict` exits 0, and
      `git diff HEAD --check` exits 0.
- [x] 3.2 Record scope/diff evidence (`git status --porcelain=v1 Receipt: gitlink stage-0 160000 at ceebf97f unchanged; nested worktree clean; openspec 1.13.1 == generatedBy 1.13.1; 15 changed paths all within the declared surface.
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`,
      `git diff --submodule=short`); confirm the gitlink pointer is unchanged. Confirm
      `openspec --version` equals the `generatedBy` frontmatter in
      `.agents/skills/*/SKILL.md`.

## 4. Closeout and archive

- [x] 4.1 Plan-review obligation (owner: apply agent): re-read the proposal's Change RECORD: compared Change Focus against the diff — no subagent types invented; the guard's negative control proves it cannot pass a violating config; the posture block is present in both configs. Actionable findings: 0.
      Focus against the actual diff; confirm the change invents no subagent types and
      the guard cannot pass on a violating config. Done condition: the review record
      names the compared artifacts and the finding count.
- [x] 4.2 Closeout review (owner: archive agent): confirm the posture block exists in RECORD: EV2 scope n/a (skip_specs); the plan closure's three READMEs agree; gates green on the final tree. Actionable findings: 0.
      both configs, the negative control is committed, and the plan closure's three
      READMEs agree. Done condition: the review record exists and the gates in 3.1 are
      green on the final tree.
- [x] 4.3 Archive via `openspec archive pin-subagent-knobs --yes` (user pre-authorized Receipt: archive green; aggregate closeout gate 0 post-archive; commit follows this record.
      autonomous full-pipeline execution on 2026-10-03); re-run the aggregate gate
      (exit 0). Then commit the change and the ledger closure per the standing commit
      discipline.
