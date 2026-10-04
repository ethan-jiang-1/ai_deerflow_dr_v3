# Tasks

## 1. Land the registry

- [x] 1.1 Write `deep_research_harness/proof-lanes.toml` with `version = 1` and two lanes (`verify`: surfaces `deep_research_harness/src/**` + `deep_research_harness/tests/**`, sentinel `[verify] harness unittest gate passed.`; `smoke`: surfaces `deep_research_harness/tests/integration/**` + `deep_research_harness/cli.py`, sentinel `OK`), each with command, cwd, tier; verify `python3 openspec/governance/check_proof_receipts.py --self-test` exit 0 and the checker with no attestation exits 0
- [x] 1.2 Declare the new path in `openspec/governance/required-paths.toml`; verify `python3 openspec/governance/check_project_architecture.py` exit 0

## 2. Closeout evidence

- [x] 2.1 Run and record receipts: `check_project_gate.py --phase closeout`, `check_doc_hygiene.py`, `check_release_face.py`, `UV_OFFLINE=1 make verify` — all exit 0; `git diff --check` clean
