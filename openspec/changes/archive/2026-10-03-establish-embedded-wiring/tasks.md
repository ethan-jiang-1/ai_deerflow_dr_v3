# Tasks

## 1. Mirror, config resolution, fakes (red-before-green, framework-free where possible)

- [x] 1.1 Write `tests/unit/test_wiring_mirror.py`: the mirror constants cover the ten
      constructor parameters and four event families; explicit config resolution
      (existing path honored, missing path fails naming the request, no default
      discovery); fixture `use:` seam targets resolve to harness-owned fakes;
      client-binding defaults (plan_mode False, subagent_enabled True,
      available_skills None) are asserted against the binding's declared constants.
      Verify: discovery exits 1 (red receipt).
- [x] 1.2 Implement `runtime/contracts/` (client surface, event families, checkpointer
      seam — typed declarations with drift-test support), `runtime/client.py`
      (explicit-path binding with the ruled defaults), `runtime/fixtures/`
      (fake chat model + fake search provider implementing the framework interfaces),
      `config/base.yaml`, `config/fixture.yaml` — `@impl DEW-001` in module
      docstrings. Verify: discovery exits 0 (green receipt).

## 2. Run engine (red-before-green)

- [x] 2.1 Write `tests/unit/test_run_engine.py` (pure-rule tests with fake stream
      events at the domain boundary): normal completion lands `completed`;
      stop-reason recognition; unanswered clarification within bound triggers the
      continuation reply (provenance mark present) and exhausts to `failed-resume`
      with the question file written; journal `model_tool`/`subagent` entries appear;
      the engine refuses to report a terminal state contradicting the state machine.
      Verify: discovery exits 1 (red receipt).
- [x] 2.2 Implement `runtime/run_engine.py` (single stream iteration feeding journal +
      terminal rules + bounded continuation loop) and the assembly-snapshot middleware
      (self-defending first-round hook writing the snapshot into `diagnostics/`),
      `@impl DEW-001`. Verify: discovery exits 0.

## 3. Governance wiring

- [x] 3.1 Add the new structural paths to `openspec/governance/required-paths.toml`
      (`runtime/contracts/`, `runtime/fixtures/`, `config/base.yaml`,
      `config/fixture.yaml`) and update `deep_research_harness/pyproject.toml`
      dependencies with `deerflow-harness`. Verify:
      `python3 openspec/governance/check_project_architecture.py` exits 0.
- [x] 3.2 Register `DEW-001: deerflow-wiring — <description>` in
      `openspec/governance/req-registry.yaml` and create the main spec
      `openspec/specs/deerflow-wiring/spec.md` during apply (`> req: DEW-001` header).
      Verify: `check_project_reqs.py`, `check_project_req_coverage.py`, and
      `check_project_specs.py` all exit 0.

## 4. The smoke (the pinned experiment)

- [x] 4.1 Materialize the environment (`uv sync`) and record the result honestly.
      Write `tests/integration/test_wiring_smoke.py` (framework-dependent, skip-guarded):
      embedded client + bundle sync saver, multi-turn conversation through the fixture
      configuration, `checkpoint.sqlite` present and readable with the thread state;
      assembly snapshot file present; a clarification scenario exercising the bounded
      continuation. Add the `make smoke` target. Verify: the smoke exits 0 in the
      synced environment (or the concrete blocker is recorded and the change reports
      it — either outcome closes the plan's uncertainty). Receipt: uv sync resolved the
      full heavy tree (exit 0, workspace-local UV_CACHE_DIR); smoke green — multi-turn
      + bounded continuation (auto_proceed_count 1) + readable checkpoint tables +
      assembly snapshot captured. Debug findings recorded: the framework's clarification
      tool self-answers with the question echo (excluded from the answered set); the
      framework's LLM-error fallback surfaces as a normal AI message (known-limitation
      candidate, not silently absorbed).
- [x] 4.2 Run the contract test (mirror versus real signatures) in the synced
      environment. Verify: exits 0 (or names the drift — which becomes the mirror
      update task with a red-green receipt). Receipt: contract test green — ten
      constructor parameters and four event families match the real surface
      (StreamEventType Literal verified).

## 5. Verification (every exit code measured directly, no pipes)

- [x] 5.1 From `deep_research_harness/`: `make verify` exits 0 (UV_OFFLINE=1 honored)
      and `make smoke` exits 0. From the repository root: the governance unittest
      suite exits 0, the architecture checker exits 0,
      `check_project_gate.py --phase closeout` exits 0,
      `openspec validate establish-embedded-wiring --strict` exits 0, and
      `git diff HEAD --check` exits 0. Receipt: VERIFY=0, SMOKE=0, UV_VERIFY=0,
      GOV_SUITE=0, ARCH=0 (after the checker surfaced the full borrowing surface:
      deerflow, langchain, langgraph, pydantic — all declared in the manifest),
      CLOSEOUT=0, STRICT=0, DIFFCHECK=0 (Makefile EOF newline fixed).
- [x] 5.2 Record scope/diff evidence: `git status --porcelain=v1
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
      `git diff --submodule=short`; confirm the gitlink pointer is unchanged and the
      nested worktree is clean. Confirm `openspec --version` equals the
      `generatedBy` frontmatter in `.agents/skills/*/SKILL.md`. Receipt: 28 changed
      paths, all within the declared surface (mirror + binding + run engine + snapshot
      middleware + fixtures + two configs + integration/unit tests + Makefile +
      pyproject + governance registrations + change artifacts + main spec + uv.lock);
      gitlink stage-0 160000 at ceebf97f unchanged, nested worktree clean; openspec
      1.13.1 == generatedBy 1.13.1.

## 6. Closeout and archive

- [x] 6.1 Plan-review obligation (control-placement; owner: apply agent): re-read the
      proposal's Control Placement Review and the delta against the actual diff;
      confirm no framework implementation was copied and the mirror is shape only;
      confirm the unit gate remained stdlib-only. Done condition: the review record
      names the compared artifacts and the finding count. RECORD: compared proposal.md
      (Focus + both review tables), delta, design.md, tasks.md against the actual diff
      — the mirror is declarations only (no framework code copied); the unit gate's
      discovery never collects the framework-dependent integration lane (no
      `__init__.py` in tests/integration); the run engine composes RUB-001 pure rules
      and imports no framework module. Actionable findings: 0.
- [x] 6.2 Closeout review (owner: archive agent): compare the Change Focus against the
      actual diff and evidence; confirm the smoke result is recorded honestly (green
      or concrete blocker) and every negative control is green. Done condition: the
      review record exists and the gate in 5.1 is green on the final tree. RECORD
      (corrected post-archive — the review was performed before archive; the checkbox
      edit failed to land on a wording mismatch): Change Focus coverage confirmed —
      explicit config resolution (auto-discovery pinned off via the framework's own
      DEER_FLOW_CONFIG_PATH seam), contract test green against the real surface,
      assembly snapshot captured per run, terminal honesty via RUB-001 rules, bounded
      continuation proven by the smoke (count 1, provenance-marked reply). Debug
      findings recorded in 4.1 (clarification echo self-answer; LLM-error fallback as
      normal AI message — flagged as a known-limitation candidate for the entry
      change). Actionable findings: 0.
- [x] 6.3 Archive via `openspec archive establish-embedded-wiring --yes` (user
      pre-authorized autonomous full-pipeline execution on 2026-10-03); re-run the
      aggregate gate (exit 0); verify the main spec retains `> req: DEW-001`
      mechanically. Then commit the change and the ledger pointer per the standing
      commit discipline.
