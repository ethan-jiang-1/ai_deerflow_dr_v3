# Tasks

## 1. Import-policy completion (checker + manifest move together)

- [x] 1.1 Update `REQUIRED_INTERNAL_IMPORT_POLICY["runtime"]` in
      `openspec/governance/check_project_architecture.py` to `{domain, engine, agents}`
      (comment: runtime is the declared composition home; the chain deepens
      domain ← engine ← runtime, no cycle), and set
      `openspec/governance/project-structure.toml` `[imports]` `runtime =
      ["domain", "engine", "agents"]`. Update the split-manifest fixture's `runtime`
      line in `openspec/tests/governance/test_split_manifest.py` to match. Verify:
      `python3 -m unittest discover -s openspec/tests/governance -q` exits 0 and
      `python3 openspec/governance/check_project_architecture.py` exits 0.

## 2. Domain kinds + engine policy (red-before-green)

- [x] 2.1 Write `tests/unit/test_admission_engine.py` (stdlib unittest): closed sets
      (`ARTIFACT_KINDS` = evidence/final_report; result codes = the six-code closed set;
      dispositions = admit/reject/replay); validator verdicts with every result code
      reachable (unknown kind → `schema_malformed`; unsafe filename →
      `schema_malformed`; producer-less provenance → `missing_provenance`; empty
      content → `empty_content`; hash already admitted → `duplicate_content`; clean
      submission → `ok` with reasons empty); gate derivation (`pass` when covered,
      `blocked` naming exactly the unmet requirements); register sync (`docs/quality-register.md`
      names every machine in the engine-declared list). Verify: discovery exits 1 with
      import errors (red receipt).
- [x] 2.2 Implement `domain/admission.py` (`ARTIFACT_KINDS`), `engine/verdicts.py`
      (result codes, dispositions, `ValidatorVerdict`, `GateVerdict`), 
      `engine/validator.py` (ordered pure rules), `engine/gate.py` (pure derivation),
      `engine/machines.py` (declared machine list), and
      `deep_research_harness/docs/quality-register.md` (the RT10 surface: every machine
      with its invariant and evidence seam) — `@impl RUA-001` in module docstrings.
      Verify: discovery exits 0 (green receipt).

## 3. Runtime ledger and admission (red-before-green)

- [x] 3.1 Write `tests/unit/test_admission_runtime.py`: honest ledger round-trip with
      chain verification; a tampered entry field fails naming the first broken
      sequence; an inserted entry breaks linkage; an illegal disposition is rejected
      loudly; `reject` places no content anywhere in the bundle and records reasons;
      `admit` places content at `evidence/{kind}/{filename}` and records path + hash;
      duplicate content is rejected as `duplicate_content`; replay of reworked content
      (hash matches a prior reject, fresh verdict `ok`) records `replay` referencing the
      rejected sequence and places the content; a verdict-less commit is refused;
      `validation` journal entries accompany dispositions. Verify: discovery exits 1
      (red receipt).
- [x] 3.2 Implement `runtime/ledger.py` (genesis chain, canonical-JSON commit, chain
      verification on read, single-writer commit refusing verdict-less or
      verdict-contradicting records) and `runtime/admission.py` (`submit_artifact`
      composing validator → ledger → placement; `read_admitted_counts` for the gate),
      `@impl RUA-001` in module docstrings. Verify: discovery exits 0.

## 4. Governance wiring

- [x] 4.1 Register `RUA-001: run-admission — <description>` in
      `openspec/governance/req-registry.yaml`. Verify:
      `python3 openspec/governance/check_project_reqs.py` exits 0.
- [x] 4.2 Create the main spec `openspec/specs/run-admission/spec.md` during apply
      (`> req: RUA-001` header, Purpose, full requirement set). Verify:
      `python3 openspec/governance/check_project_req_coverage.py` exits 0 and
      `python3 openspec/governance/check_project_specs.py` exits 0.

## 5. Verification (every exit code measured directly, no pipes)

- [x] 5.1 From `deep_research_harness/`: `make verify` exits 0 (UV_OFFLINE=1 honored).
      From the repository root: the governance unittest suite exits 0, the architecture
      checker exits 0, `check_project_gate.py --phase closeout` exits 0,
      `openspec validate establish-run-admission --strict` exits 0, and
      `git diff HEAD --check` exits 0. Receipt: MAKE_VERIFY=0, UV_VERIFY=0, GOV_SUITE=0,
      ARCH=0, STRICT=0, DIFFCHECK=0; CLOSEOUT=1 → 0 after the dependency-direction
      checker caught the register naming a governance path (fixed by de-pathing the
      evidence-seam cell).
- [x] 5.2 Record scope/diff evidence: `git status --porcelain=v1
      --untracked-files=all`, `git ls-files --stage deerflow`,
      `git submodule status -- deerflow`,
      `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review
      `git diff --submodule=short`; confirm the gitlink pointer is unchanged. Confirm
      `openspec --version` equals the `generatedBy` frontmatter in
      `.agents/skills/*/SKILL.md`. Receipt: diff scope matches the updated proposal
      Impact exactly (5 engine + 2 runtime + 1 domain modules, 2 admission test files,
      quality register + docs index row, checker + manifest + split-manifest fixture +
      doc-hygiene scope, registry, change artifacts, main spec; no strays); gitlink
      stage-0 160000 at ceebf97f unchanged, nested worktree clean; openspec 1.13.1 ==
      generatedBy 1.13.1.

## 6. Closeout and archive

- [x] 6.1 Plan-review obligation (control-placement; owner: apply agent): re-read the
      proposal's Control Placement Review and the delta against the actual diff;
      confirm the hold point is enforced on the only commit path and the import-policy
      completion is exactly `runtime += engine` with no cycle. Done condition: the
      review record names the compared artifacts and the finding count. RECORD:
      compared proposal.md (Focus + both review tables + updated Impact), delta,
      design.md (with the two polish-pass repairs: closed entry field set, disposition
      selection ownership), tasks.md against the actual diff — `commit_entry` is the
      only ledger write path and refuses verdict-less/contradicting records; the
      manifest + checker policy + fixture moved together; directions deepen
      domain ← engine ← runtime with no cycle. Two Impact surfaces beyond the first
      draft (doc-hygiene scope registration, docs index row) are now declared in the
      proposal rather than absorbed silently. Actionable findings: 0.
- [x] 6.2 Closeout review (owner: archive agent): compare the Change Focus against the
      actual diff and evidence; confirm every negative control is green and the
      register matches the declared machines. Done condition: the review record exists
      and the gate in 5.1 is green on the final tree. RECORD: Change Focus coverage
      confirmed — engine owns validator/gate/machines (layer fills for the first
      time), runtime owns ledger/admission materialization, domain owns the closed
      kinds; negative controls green (tampered field names seq, inserted entry breaks
      linkage, verdict-less and verdict-contradicting commits refused, reject places
      nothing, duplicate rejected, replay references the rejected seq); register sync
      test green; 57/57 suite green; closeout gate green on the final tree.
      Actionable findings: 0.
- [x] 6.3 Archive via `openspec archive establish-run-admission --yes` (user
      pre-authorized autonomous full-pipeline execution on 2026-10-03); re-run the
      aggregate gate (exit 0); verify the main spec retains `> req: RUA-001`
      mechanically. Then commit the change and the ledger pointer per the standing
      commit discipline.
