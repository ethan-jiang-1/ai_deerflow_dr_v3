# Tasks

## 1. Domain contract and pure rules (red-before-green)

- [x] 1.1 Write `tests/unit/test_bundle_domain.py` (stdlib unittest): declared path
      constants resolve to the exact subtree set with no `synthesis/`/`review/`;
      transition rules (start/cancel/refine legality, refine generation+1, illegal
      transition rejected naming state/action/reason); clarification detection predicate
      (unanswered ask_clarification → continuation; exhaustion at bound → failed-resume
      with diagnostics routing); journal policy (closed eight-category set, eviction
      never touches `admission`, compaction preserves anchors + tail); composition
      closed set. Verify: `PYTHONPATH=src python3 -m unittest discover -s tests` exits 1
      with import errors (red receipt — the modules do not exist yet).
- [x] 1.2 Implement the domain modules: `domain/bundle.py` (path constants, bucket and
      bundle id forms), `domain/state_machine.py` (states, transition table, refine and
      cancellation rules), `domain/clarification.py` (detection predicate, bound rule),
      `domain/journal_policy.py` (category closed set, eviction priority, compaction
      selection) — pure functions, stdlib only, `@impl RUB-001` in the module
      docstrings. Verify: the unittest discovery exits 0 (green receipt).

## 2. Runtime materialization (red-before-green)

- [x] 2.1 Write `tests/unit/test_bundle_runtime.py`: staging-publish start materializes
      exactly the declared subtrees + `state.json` (and never a partial bundle on
      failure); CAS conflict rejected naming expected/actual revision; atomic replace
      leaves no torn read; lease mismatch (`st_dev`/`st_ino`) rejects the write; dead
      owner PID on `status` transfers to `failed-resume` with a `terminal` journal entry
      (probe uses a genuinely exited child process); journal append/eviction/compaction
      round-trip with anchors surviving; corrupted tail fails the read; deleted bundle
      reports permanent unavailability; illegal composition rejected at `start`. Verify:
      discovery exits 1 (red receipt).
- [x] 2.2 Implement the runtime modules: `runtime/atomic.py` (shared safe file layer:
      `O_EXCL` temp + `os.replace` + fsync + `O_NOFOLLOW` where applicable),
      `runtime/bundle_state.py` (state store: read/validate/reduce/write with revision
      CAS and lease re-check), `runtime/journal.py` (append, retention on write,
      compaction, corrupted-tail fail-loud), `runtime/bundle_actions.py` (`start`/
      `status`/`cancel`/`refine` composing domain rules with the stores; injectable
      liveness probe), `@impl RUB-001` in module docstrings. Verify: discovery exits 0.

## 3. The gate becomes real

- [x] 3.1 Replace the `verify` stub in `deep_research_harness/Makefile` with the
      unittest gate (`PYTHONPATH=src python3 -m unittest discover -s tests`) and align
      the `install` stub wording (no external dependencies exist to install; the
      deerflow-harness editable source lands with the wiring change). Red proof for the
      gate itself: temporarily break one test, observe `make verify` exit non-zero,
      restore, observe exit 0 — record both exits. Verify: `make verify` exits 0 from
      `deep_research_harness/`.
- [x] 3.2 Update `deep_research_harness/AGENTS.md` (Verification section: the gate now
      promises the unittest suite), `deep_research_harness/COMMANDS.md` (the verify
      command), and `deep_research_harness/docs/testing-and-evaluation.md` (lane
      division: unit suite = the application lane; governance checks stay
      governance-owned). Verify: `python3 openspec/governance/check_doc_hygiene.py`
      exits 0 plain and with `--self-test`.

## 4. Governance wiring

- [x] 4.1 Register `RUB-001: run-bundle — <description>` in
      `openspec/governance/req-registry.yaml` (apply writes the registry; planning only
      reserved). Verify: `python3 openspec/governance/check_project_reqs.py` exits 0.
- [x] 4.2 Create the main spec `openspec/specs/run-bundle/spec.md` during apply (never
      born from archive — the establish-project-structure lesson): `> req: RUB-001`
      header, Purpose, and the full requirement set from the delta. Verify:
      `python3 openspec/governance/check_project_req_coverage.py` exits 0 and
      `python3 openspec/governance/check_project_specs.py` exits 0.

## 5. Verification (every exit code measured directly, no pipes)

- [x] 5.1 From `deep_research_harness/`: `make verify` exits 0. From the repository
      root: `python3 -m unittest discover -s openspec/tests/governance -q` exits 0,
      `python3 openspec/governance/check_project_architecture.py` exits 0,
      `python3 openspec/governance/check_project_gate.py --phase closeout` exits 0,
      `openspec validate establish-run-bundle --strict` exits 0, and
      `git diff HEAD --check` exits 0. Receipt: MAKE_VERIFY=0, UV_OFFLINE_VERIFY=0,
      GOV_SUITE=0, ARCH=0, CLOSEOUT=0 (after the dependency-direction checker caught
      and the change fixed two harness docs naming the governance path), STRICT=0,
      DIFFCHECK=0.
- [x] 5.2 Record scope/diff evidence: `git status --porcelain=v1
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
      `git diff --submodule=short`; confirm the gitlink pointer is unchanged. Confirm
      `openspec --version` equals the `generatedBy` frontmatter in
      `.agents/skills/*/SKILL.md`. Receipt: diff scope matches proposal Impact exactly
      (4 domain + 4 runtime modules, 2 test files + 2 package markers, Makefile +
      3 docs, registry, change artifacts, main spec; no strays); gitlink stage-0 160000
      at ceebf97f unchanged, nested worktree clean; openspec 1.13.1 == generatedBy
      1.13.1.

## 6. Closeout and archive

- [x] 6.1 Plan-review obligation (control-placement; owner: apply agent): re-read the
      proposal's Control Placement Review and the delta against the actual diff;
      confirm `state.json` is the only state authority and no second controller was
      created; every actionable finding becomes an unchecked task or an approved
      re-scope. Done condition: the review record names the compared artifacts and the
      finding count. RECORD: compared proposal.md (Focus + both review tables), delta,
      design.md, tasks.md against the actual diff — the only state.json writer is
      `runtime/bundle_state.py` behind the CAS+lease store; the actions compose pure
      domain rules; no competing controller or parallel truth exists; the closed-set
      vocabularies (states, categories, compositions) live in domain. Actionable
      findings: 0.
- [x] 6.2 Closeout review (owner: archive agent): compare the Change Focus against the
      actual diff and evidence; confirm the negative controls are green and the pure
      rules / materialization boundary matches design decision 1. Done condition: the
      review record exists and the gate in 5.1 is green on the final tree. RECORD:
      Change Focus coverage confirmed — domain owns every pure rule (transition table,
      detection predicate, journal policy, closed vocabularies), runtime owns
      materialization only (atomic layer, CAS store, journal writer, actions), engine
      intentionally empty; all negative controls green (CAS conflict, lease mismatch,
      dead-PID transfer, anchor-surviving eviction, corrupted tail, illegal
      category/composition/transition/cancel); gate red proof recorded (0 → 2 → 0);
      closeout gate green on the final tree. Actionable findings: 0.
- [x] 6.3 Archive via `openspec archive establish-run-bundle --yes` (user pre-authorized
      autonomous full-pipeline execution on 2026-10-03; no separate approval pause);
      re-run the aggregate gate (exit 0); verify the main spec retains `> req: RUB-001`
      (it was created during apply, so archive only merges — re-check mechanically via
      `python3 openspec/governance/check_project_architecture.py` and
      `check_project_reqs.py` exit 0). Then commit the change and the ledger pointer
      per the standing commit discipline.
