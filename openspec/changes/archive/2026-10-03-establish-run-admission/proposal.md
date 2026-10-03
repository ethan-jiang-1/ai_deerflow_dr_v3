# Proposal

## Why

The run-bundle substrate (RUB-001) exists, but nothing yet decides what may enter it:
the bundle plan's quality mapping names this as the construction-quality hold point —
验收收口在提议进 Bundle 前, with the validator as 专检 (code, not the model, decides) and
the ledger as 质量追溯 (every disposition traceable in a tamper-evident chain). Decision
4 is the remaining half of the quality heart, and the journal already reserves the
`admission` anchor category waiting for it. Without it, `evidence/` is an unguarded
directory and "models propose, code disposes" is a slogan, not a machine.

## What Changes

- New `run-admission` capability (RUA-001), implemented across engine (pure policy) and
  runtime (materialization):
  - **Validator (engine, pure)**: every proposed artifact is validated before anything
    is placed — the hold point. Verdicts carry a small closed `ResultCode` set
    (`ok`, `schema_malformed`, `missing_provenance`, `empty_content`, `hash_mismatch`,
    `duplicate_content`) plus human-readable reasons. Malformed proposals are rejected,
    never repaired silently.
  - **Hash-chain ledger (runtime)**: `evidence/submissions.jsonl` is append-only JSONL
    with a sha256 hash chain (genesis `prev_hash` = 64 zeros; each entry commits to its
    predecessor and to the artifact's `content_hash`); reads verify the chain and fail
    loudly on tampering; a single writer owns commits. Three dispositions only:
    `admit` / `reject` / `replay` (closed set). `reject` places no artifact content into
    the bundle; `replay` re-validates content matching a previously rejected entry and
    records the rework honestly; a duplicate of already-admitted content is rejected.
  - **Gate (engine, pure)**: minimal derivation over declared requirements versus the
    ledger's admitted facts — `PhaseVerdict` is `pass` or `blocked` (v2's repair-budget
    machinery stays cut); `blocked` names the unmet requirements.
  - **Closed vocabularies** live in domain: artifact kinds (`evidence`, `final_report`)
    and the verdict vocabularies; anything outside a closed set is rejected loudly at
    the boundary.
  - **Quality register (RT10)**: one surface,
    `deep_research_harness/docs/quality-register.md`, listing every quality machine —
    validator, gate, ledger chain verification, the unittest gate, and the governance
    gates — with what each guarantees and its evidence seam; a unit test keeps the
    register in sync with the engine's declared machine list, so the register cannot
    silently rot. 接手者一眼看到「质量由哪些机器保证」.
- **Import-policy completion (deliberate, recorded)**: `runtime`'s internal allowance
  gains `engine` (`runtime = ["domain", "engine", "agents"]`), because runtime is the
  declared composition home and only the composing writer can enforce the hold point.
  The checker's non-weakenable `REQUIRED_INTERNAL_IMPORT_POLICY` and the manifest are
  updated together; no cycle is created (`engine` stays `{domain}`), and the direction
  guarantee survives: the manifest change is the exact-enumeration update the
  architecture policy prescribes for this case.
- `make verify` gains the engine and admission suites (same stdlib gate; no new
  dependencies).

## Capabilities

### New Capabilities

- `run-admission`: owns the required behavior of the acceptance closeout — the
  validator hold point, the tamper-evident disposition ledger, the minimal gate
  derivation, the closed admission vocabularies, and the quality register sync.

### Modified Capabilities

(none — the ledger lives inside the already-declared `evidence/` subtree; the import
policy change is the structural manifest's exact-enumeration update, not a
project-structure requirement change)

## Impact

- New: `deep_research_harness/src/deerflow_deep_research/engine/` (validator, gate,
  verdict vocabularies, machine list — the layer fills for the first time),
  `deep_research_harness/src/deerflow_deep_research/runtime/ledger.py` +
  `runtime/admission.py`, `deep_research_harness/src/deerflow_deep_research/domain/admission.py`
  (closed kinds), tests under `deep_research_harness/tests/unit/`,
  `deep_research_harness/docs/quality-register.md`.
- Modified: `openspec/governance/check_project_architecture.py`
  (`REQUIRED_INTERNAL_IMPORT_POLICY["runtime"]` gains `engine`),
  `openspec/governance/project-structure.toml` (`[imports]` runtime value),
  `openspec/tests/governance/test_split_manifest.py` (fixture follows the manifest),
  `openspec/governance/check_doc_hygiene.py` (`DOC_LAYER_DOCS` registers the new
  docs-layer file), `deep_research_harness/docs/README.md` (index row for the register),
  `openspec/governance/req-registry.yaml` (RUA-001 registration in apply).
- No CI workflow change, no new external dependencies, no `deerflow/` contact —
  ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink;
  this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/engine/` — the
  validation and gate policies are the semantic decision (what may enter a bundle, and
  when a phase is done); runtime only materializes the verdicts into the ledger.
- **Seam classification:** deterministic-guardrail — every changed behavior is a
  machine-checked admission rule (hold point, hash chain, closed sets); no model
  cognition is involved.
- **Question:** How does the acceptance closeout become a machine — a hold point that
  admits nothing unvalidated, a tamper-evident three-disposition ledger, a minimal
  pass/blocked gate, and a quality register that cannot silently rot — without
  widening the import direction beyond what the composition role requires?
- **Necessary adjacent/external contracts:** `src/deerflow_deep_research/runtime/` (answers: how verdicts materialize as
  hash-chained ledger commits and evidence files, and why only the composing writer can
  enforce the hold point); `openspec/governance/check_project_architecture.py` + `openspec/governance/project-structure.toml` (answers: the exact manifest enumeration
  when runtime's internal allowance gains `engine`); `deep_research_harness/docs/quality-register.md` (answers: where the
  machine list lives and how its sync is tested); the run-bundle store (answers: which
  existing seams the ledger reuses — handle, lease, atomic layer, journal).
- **Evidence seam:** the harness unittest suite via `make verify` — validator verdict
  coverage (every result code reachable), chain-verification negative controls
  (tampered entry, broken linkage, illegal disposition), hold-point proof (reject
  places nothing), gate blocked/pass derivation, and register-sync drift.
- **Not in scope:** repair-budget mechanics (cut by the plan), HITL surfaces, pending
  or suspended states, the wiring-side producer that will call admission (its callers
  arrive with wiring), CLI surfaces, checkpoint writes.
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| Admission authority is placed in the engine validator as the bundle's hold point: nothing enters `evidence/` without a code-rendered verdict | Human judgment (bundle plan decision 4: 模型提议、代码裁决; repair budgets stay cut) | Pure validator functions with closed result codes; the runtime ledger records only validator-rendered dispositions | non-bypassable | A submission that skips validation cannot be recorded (the ledger writer refuses verdict-less commits); tampered ledger entries fail chain verification loudly | v2's repair-budget and pending-state machinery stay cut; the journal's reserved `admission` anchor category starts earning its keep | Harness unittest suite via make verify; negative controls for verdict-less commit, tampered chain, and hold-point placement |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| Validator rejects a proposal (malformed / missing provenance / empty / duplicate) | Engine validator (pure) | The producer may resubmit; the ledger records every `reject` with reasons | Rejection recorded; no artifact content placed (hold point) | Fix the proposal and resubmit (`replay` once it validates) | Unit test: reject places nothing, ledger entry exists with reasons |
| Ledger tampered or chain broken | Ledger reader (chain verification) | None — fail loud, never heal silently | Read fails naming the offending sequence | Manual, visible repair of the JSONL (human-readable file) | Unit test: tampered entry and broken linkage both fail verification |
| Gate blocked | Engine gate (pure derivation) | Producer supplies the missing admitted artifacts; bound is the declared requirement list itself | `blocked` naming the unmet requirements | Submit the missing artifacts; re-derive | Unit test: blocked names exactly the unmet requirements |
| Replay of previously rejected content | Validator + ledger (content-hash match against the rejected entry) | Validator must pass before the replay records | `replay` disposition recorded, artifact placed | Continue the phase | Unit test: replay without validation still rejects; replay after fix records |
