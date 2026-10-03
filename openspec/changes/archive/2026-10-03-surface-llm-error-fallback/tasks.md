# Tasks

## 1. Guard (red-before-green)

- [x] 1.1 Write the guard cases in `tests/unit/test_run_engine.py`: a scripted values Receipt: red = the two fallback-detection cases failing (the engine ignored the marker); the negative control passed as designed — measured.
      snapshot whose last AI message carries `deerflow_error_fallback` (+ `error_type`)
      transfers to `failed-resume` with a `terminal` journal entry naming the error
      type; the fallback branch takes precedence over a clean completion (a fallback
      run never reports `completed`); the negative control — a clean stream without the
      marker still completes with no behavior change. Verify: the new cases are red
      (the engine ignores the marker today — measured).
- [x] 1.2 Implement the guard in `runtime/run_engine.py`: the `values`-snapshot scan Receipt: green (90/90); the values snapshot carries the fallback fact; branch order is fallback-first; the unrealistic chunk-only test was reshaped to the real stream shape (disclosed in the test comment).
      captures the last AI message's `deerflow_error_fallback` marker and
      `error_type` from `additional_kwargs`; `run_research` transfers to
      `failed-resume` (journal `terminal` entry with `reason: llm_error_fallback`,
      `error_type`) before the clarification/stop-reason/completed branches when the
      marker is present. Verify: discovery exits 0.

## 2. Integration proof (the real chain)

- [x] 2.1 Extend `runtime/fixtures/__init__.py` with the `{"raise": "…"}` script Receipt: the raising scripted model drives the REAL framework fallback end-to-end → failed-resume with the terminal journal entry naming error_type RuntimeError; smoke 3/3.
      action (`_generate` raises the scripted error) and write the smoke scenario in
      `tests/integration/test_wiring_smoke.py`: a deliberately raising scripted model
      drives the framework's real error-fallback path, and the run lands
      `failed-resume` with the `terminal` journal entry. Verify: the scenario exits 0
      in the synced environment (`make smoke`).

## 3. Known-limitations disposition

- [x] 3.1 Update `deep_research_harness/docs/known-limitations.md`: the Receipt: the limitation row's disposition now names the landed guard; doc hygiene green plain and self-test.
      LLM-error-fallback row's disposition changes from "未修复" to guarded (this
      change), with the framework behavior itself remaining a fact. Verify:
      `check_doc_hygiene.py` exits 0 plain and with `--self-test`.

## 4. Verification (every exit code measured directly, no pipes)

- [x] 4.1 From `deep_research_harness/`: `make verify` exits 0 (UV_OFFLINE=1 honored) Receipt: VERIFY=0, SMOKE=0, UV_VERIFY=0, GOV_SUITE=0, ARCH=0, CLOSEOUT=0, STRICT=0, DIFFCHECK=0.
      and `make smoke` exits 0. From the repository root: the governance unittest
      suite exits 0, the architecture checker exits 0,
      `check_project_gate.py --phase closeout` exits 0,
      `openspec validate surface-llm-error-fallback --strict` exits 0, and
      `git diff HEAD --check` exits 0.
- [x] 4.2 Record scope/diff evidence (`git status --porcelain=v1 Receipt: gitlink stage-0 160000 at ceebf97f unchanged; nested worktree clean; openspec 1.13.1 == generatedBy 1.13.1; 10 changed paths within the declared surface.
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`,
      `git diff --submodule=short`); confirm the gitlink pointer is unchanged. Confirm
      `openspec --version` equals the `generatedBy` frontmatter in
      `.agents/skills/*/SKILL.md`.

## 5. Closeout and archive

- [x] 5.1 Plan-review obligation (owner: apply agent): re-read the Workflow Outcome RECORD: compared the Workflow Outcome Review against the diff — the guard adds zero behavior to clean runs (negative control green); branch order is fallback-first; no competing retry controller. Actionable findings: 0.
      Review against the actual diff; confirm the guard adds no behavior to clean runs
      and the branch order is fallback-first. Done condition: the review record names
      the compared artifacts and the finding count.
- [x] 5.2 Closeout review (owner: archive agent): confirm the unit negative control RECORD: the unit negative control, the integration proof (raising model → failed-resume end-to-end), and the known-limitations disposition are all green/updated. Actionable findings: 0.
      and the integration proof are green, and `known-limitations.md` states the new
      disposition. Done condition: the review record exists and the gates in 4.1 are
      green on the final tree.
- [x] 5.3 Archive via `openspec archive surface-llm-error-fallback --yes` (user Receipt: archive green (main spec retains > req: DEW-001 with the MODIFIED requirement merged); aggregate closeout gate 0 post-archive; commit follows this record.
      pre-authorized autonomous full-pipeline execution on 2026-10-03); re-run the
      aggregate gate (exit 0); verify the main spec retains `> req: DEW-001` and the
      MODIFIED requirement merged. Then commit per the standing commit discipline.
