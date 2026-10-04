# Tasks

## 1. Registry reservation setup

- [x] 1.1 Register APB-001 (agent-playbook) and RLF-001 (release-face) in `openspec/governance/req-registry.yaml` with capability names and descriptions matching the delta specs; verify `python3 openspec/governance/check_project_reqs.py` exits 0

## 2. Cold-start guard, red-first

- [x] 2.1 Write `openspec/tests/governance/test_release_face.py` first with fixtures for each violation class (gitlink pin drift, broken sibling layout, `[tool.uv.sources]` escape, dev-face reference in harness runtime/CLI source, dangling menu routing target) asserting non-zero exit naming the violation, and a compliant-tree case asserting exit 0; verify it fails now (red) with `python3 -m unittest openspec.tests.governance.test_release_face -v` because the checker does not exist
- [x] 2.2 Implement `openspec/governance/check_release_face.py` (static lane per design D1–D3) and verify the test pair turns green: `python3 -m unittest openspec.tests.governance.test_release_face -v` exits 0, and `python3 openspec/governance/check_release_face.py` exits 0 on the current tree
- [x] 2.3 List the new checker in `openspec/governance/README.md`'s checker section with its one-line contract; verify the file renders and `python3 openspec/governance/check_doc_hygiene.py` exits 0

## 3. Two-layer invocation structure

- [x] 3.1 Create `deep_research_harness/playbook/run-research.md` by moving the existing PLAYBOOK section verbatim, then adding per-step exit-code-level completion criteria and the receipt-discipline statement (per APB-001); verify the file's fixture-ladder commands are the exact ones documented and that `make verify` exits 0 afterwards
- [x] 3.2 Rewrite `deep_research_harness/COMMANDS.md` as the entry face: keep the one-line entry lists, replace the PLAYBOOK section with one routing line to `playbook/run-research.md`, retire the HELP card into the menu framing; verify no ordered procedural sequence remains in the menu and the routing target resolves
- [x] 3.3 Confirm the menu's command set mirrors the closed six-verb vocabulary (ENS-001) and the make targets of `deep_research_harness/Makefile`; verify by diffing the menu entries against `cli.py`'s subparser set and the Makefile targets, exit code recorded
- [x] 3.4 Now that the files exist, declare them in `openspec/governance/required-paths.toml` under `[paths.APB-001]` (`deep_research_harness/playbook` directory + `run-research.md`) and `[paths.RLF-001]` (checker + test); verify `python3 openspec/governance/check_project_architecture.py` exits 0 with the new declarations

## 4. README status correction

- [x] 4.1 Correct `deep_research_harness/README.md`: remove the "pre-implementation stub" status notice and the "Entry Surfaces: Not defined yet" section; name the real entry surface (six verbs + make targets) and route to `COMMANDS.md`; verify `check_doc_hygiene.py` exits 0 and no budgeted document changed

## 5. Verification and evidence

- [x] 5.1 From the repository root run `python3 openspec/governance/check_project_gate.py --phase plan --change ratify-agent-playbook-and-minimal-release` and record the exit code; every reservation (APB-001, RLF-001) maps to task 1.1's registration
- [x] 5.2 From `deep_research_harness/` run `UV_OFFLINE=1 make verify` (exit 0, count recorded); run `make create PROBLEM="…"` on the fixture ladder once and record command, exit code, and the completed-state line as the fresh receipt copied into `playbook/run-research.md`
- [x] 5.3 Execute the full cold-start lane once against the real tree (fresh temp checkout: `git clone --recursive` → `git submodule update --init` → `uv sync` → `make verify` → `make create` fixture) and record every command and exit code in `playbook/run-research.md`; if the environment prevents any step, record the explicit UNVERIFIED marking per RLF-001 instead of a fabricated result
- [x] 5.4 Build the wheel target once (`uv build --wheel` from `deep_research_harness/`) and verify the packaged set excludes `cli.py` and `config/`, confirming RLF-001's wheel scenario with a recorded exit code
- [x] 5.5 From the repository root run `openspec validate ratify-agent-playbook-and-minimal-release --strict` and `git diff HEAD --check`; record both exit codes

## 6. Closeout obligations (control-placement)

- [x] 6.1 Plan-review obligation: the applying agent re-reads proposal → specs → design → tasks against the current tree, confirming the two-piece face, the static-lane guard scope, and the menu/playbook split are implemented as ratified with no scope drift; done when each artifact's claims have a named implementation fact or recorded exit code backing it
- [x] 6.2 Archive-closeout-review obligation: before archive, the applying agent runs `python3 openspec/governance/check_project_gate.py --phase closeout`, the recorded gitlink scope evidence (`git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status -- deerflow`, `git -C deerflow status --porcelain=v1 --untracked-files=all`, `git diff --submodule=short` — pointer unchanged at `ceebf97f`), and confirms `openspec --version` matches `.agents/skills/*/SKILL.md` `generatedBy` (read-only); done when all exit codes are 0 and the generation check shows no drift
