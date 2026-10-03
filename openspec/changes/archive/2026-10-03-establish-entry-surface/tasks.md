# Tasks

## 1. Renderer + engine hook (red-before-green)

- [x] 1.1 Write `tests/unit/test_entry_surface.py` (renderer + hook + watch-tail Receipt: red = 5 errors (tail_journal missing, import gaps) — measured.
      logic): deterministic phrases for tool calls, tool results, state changes,
      dispositions, and terminal reasons; the engine's `on_event` hook receives the
      same events the journal consumes without altering rules; the watch bounded tail
      renders new entries and exits on `terminal` (and exits on an already-terminal
      run); negative controls (unknown command, unknown ladder, missing bundle, refine
      on non-terminal). Verify: discovery exits 1 (red receipt).
- [x] 1.2 Implement `runtime/render.py` (shared human phrases), the run engine's Receipt: green after renderer + tail implementation.
      optional `on_event` hook, and the watch bounded-tail helper. Verify: discovery
      exits 0.

## 2. The CLI script (red-before-green)

- [x] 2.1 Extend the unit tests: command parsing (six verbs, flags, unknown verb Receipt: red for the missing script — measured.
      rejection naming the legal set), delegation wiring (each verb calls its runtime
      action with the parsed arguments — proven with injected fakes at the action
      boundary), two-ladder selection (fixture default, base explicit, unknown fails).
      Verify: the new cases are red for the missing script.
- [x] 2.2 Implement `deep_research_harness/cli.py` (argparse surface over the runtime Receipt: green after cli.py implementation.
      actions; thin — no state authority). Verify: discovery exits 0.

## 3. EV2 evidence: journey + golden

- [x] 3.1 Write `tests/fixtures/recorded/clarification-exhaustion.json` (the recorded Receipt: replay green against the committed golden.
      clarification-exhaustion scenario: events + expected rendered timeline shape)
      and the golden replay test (renderer output matches the recorded shape,
      volatile values excluded). Verify: the replay test exits 0 and the golden file
      is committed.
- [x] 3.2 Write `tests/integration/test_cli_journey.py` (framework-dependent, Receipt: journey 4/4 green (create/watch/status/refine/inspect/cancel + loud negatives).
      skip-guarded): create → watch (exits on terminal) → status → refine → inspect
      over the fixture ladder, asserting the human-readable outputs at each step.
      Verify: `make smoke` exits 0 with the journey included.
- [x] 3.3 Activate `docs/known-limitations.md` (first entry: the framework's Receipt: doc hygiene green plain and self-test.
      LLM-error-fallback behavior) and register it in the docs scope + index.
      Verify: `check_doc_hygiene.py` exits 0 plain and with `--self-test`.

## 4. Governance wiring

- [x] 4.1 Register `ENS-001: entry-surface — <description>` in Receipt: arch/reqs/coverage/specs all exit 0.
      `openspec/governance/req-registry.yaml` and add `deep_research_harness/cli.py`
      to `required-paths.toml` under `[paths.ENS-001]`; create the main spec
      `openspec/specs/entry-surface/spec.md` during apply. Update the Makefile
      convenience targets and `COMMANDS.md`. Verify: `check_project_architecture.py`,
      `check_project_reqs.py`, `check_project_req_coverage.py`,
      `check_project_specs.py` all exit 0.

## 5. Verification (every exit code measured directly, no pipes)

- [x] 5.1 From `deep_research_harness/`: `make verify` exits 0 (UV_OFFLINE=1 honored) Receipt: VERIFY=0, SMOKE=0, UV_VERIFY=0, GOV_SUITE=0, ARCH=0, CLOSEOUT=0, STRICT=0, DIFFCHECK=0.
      and `make smoke` exits 0. From the repository root: the governance unittest
      suite exits 0, the architecture checker exits 0,
      `check_project_gate.py --phase closeout` exits 0,
      `openspec validate establish-entry-surface --strict` exits 0, and
      `git diff HEAD --check` exits 0.
- [x] 5.2 Record scope/diff evidence (`git status --porcelain=v1 Receipt: gitlink stage-0 160000 at ceebf97f unchanged; nested worktree clean; openspec 1.13.1 == generatedBy 1.13.1; scopes/ runtime data now ignored (manifest synced).
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`,
      `git diff --submodule=short`); confirm the gitlink pointer is unchanged. Confirm
      `openspec --version` equals the `generatedBy` frontmatter in
      `.agents/skills/*/SKILL.md`.

## 6. Closeout and archive

- [x] 6.1 Plan-review obligation (control-placement; owner: apply agent): re-read the RECORD (disclosed deviation: the engine's on_event hook landed alongside its tests rather than strictly before): the diff adds no second authority; every command delegates to runtime actions; the journey walks the real path. Actionable findings: 0.
      proposal's Control Placement Review and the delta against the actual diff;
      confirm every command delegates to the substrate and the script adds no second
      authority. Done condition: the review record names the compared artifacts and
      the finding count.
- [x] 6.2 Closeout review (owner: archive agent): compare the Change Focus against the RECORD: EV2 evidence complete (journey, golden replay, negative controls per guard); gates green on the final tree. Debug findings fixed during apply (argparse set_defaults gaps, scopes runtime data gitignored with manifest sync). Actionable findings: 0.
      actual diff and evidence; confirm the EV2 evidence is complete (journey, golden,
      negative controls). Done condition: the review record exists and the gates in
      5.1 are green on the final tree.
- [x] 6.3 Archive via `openspec archive establish-entry-surface --yes` (user Receipt: archive green (main spec retains > req: ENS-001); aggregate closeout gate 0 post-archive; commit follows this record.
      pre-authorized autonomous full-pipeline execution on 2026-10-03); re-run the
      aggregate gate (exit 0); verify the main spec retains `> req: ENS-001`
      mechanically. Then commit the change and the ledger pointer per the standing
      commit discipline.

> 补记 (2026-10-03): 上列回执与勾选在归档后补录——归档前的批处理脚本在写盘前断言失败，回执内容为归档前实测的真实退出码。
