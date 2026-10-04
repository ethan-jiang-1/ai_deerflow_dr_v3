# Tasks

## 1. Red-first negative controls (self-test)

- [x] 1.1 Add to the doc-hygiene self-test a count-drift fixture: a tree whose root
  README declares counts differing from its computed inventory; assert the checker
  exits non-zero naming computed and declared values. Verify: the self-test reports
  the new control failing against the current checker (red), because the rule does
  not exist yet.
- [x] 1.2 Add a row-placement fixture: a ledger README whose archive row is separated
  from its table header block by a blank line and a fenced block (the B3/B5 shapes);
  assert non-zero naming the surface, the row, and the placement. Verify: red against
  the current checker for the same reason.

## 2. Checker rules (green)

- [x] 2.1 Implement the count-pinning rule: compute specs/archive counts from disk,
  structurally match the root README status line, fail loudly naming computed vs
  declared. Verify: self-test green including both new controls; real tree exits 0.
- [x] 2.2 Implement row-placement validation inside the ledger-consistency rule
  (contiguity with the row's table header block; blank line, prose, and fence
  separation all fail). Verify: self-test green; real tree exits 0.
- [x] 2.3 Correct the `MARKER_ALLOWLIST` justification path to
  `_backlog/_done/_closed_plans/2026-10-04-fresh-agent-doc-cleanup.md`. Verify:
  checker exit 0 on the real tree; the allowlist rule's own negative control still
  passes.

## 3. Ratchet and content declarations

- [x] 3.1 Lower `DOC_BUDGETS`: root `AGENTS.md` 2435 → 2425,
  `deep_research_harness/AGENTS.md` 6864 → 6863, with a comment noting the sweep
  measurement. Verify: checker exit 0 (both files measure 2425/6863).
- [x] 3.2 A5: add the one-line profile disambiguation to `CONTEXT-MAP.md` (root
  `profiles/` = local run profiles; `openspec/change-guidance/profiles/` = policy
  profiles). Verify: text present; doc-hygiene exit 0.
- [x] 3.3 C2: add the divergence declaration one-liner to harness `AGENTS.md`
  (budget-neutral or negative at 6863/6864) and to
  `openspec/change-guidance/profiles/node-agent/node-agent.md`: divergence allowed,
  harness version is the application authority. Verify: both lines present; harness
  AGENTS.md measures ≤ 6863; doc-hygiene exit 0.
- [x] 3.4 C3: record in this change's closing notes that the three overlapping
  routing tables are accepted as docs-as-contract (zero edits, per operator ruling).

## 4. Closeout

- [x] 4.1 Run the full gate from the repo root:
  `python3 openspec/governance/check_project_gate.py --phase closeout`; exit code
  read directly. Verify: exit 0.
- [x] 4.2 From `deep_research_harness/`, run `UV_OFFLINE=1 make verify`; from the repo
  root, run `openspec validate enforce-doc-recurrence-guards --strict` and
  `git diff HEAD --check`. Verify: all exit 0 read directly.
- [x] 4.3 Record scope/submodule evidence (`git status --porcelain=v1
  --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status --
  deerflow`, `git -C deerflow status --porcelain=v1 --untracked-files=all`): gitlink
  pointer unchanged from `ceebf97f`, nested worktree clean. Verify: outputs recorded
  in closing notes.

## Closing notes

- C3 (routing tables) recorded as accepted docs-as-contract per operator ruling — zero edits.
- Resident budgets after ratchet: root AGENTS.md 2425/2425 · harness AGENTS.md 6863/6863.
- Scope/submodule evidence: gitlink 160000 ceebf97f unchanged, nested worktree clean,
  `git -C deerflow status` empty; closeout gate, strict validation, `git diff HEAD --check`,
  and `UV_OFFLINE=1 make verify` all exit 0.
- Red-first receipts: both self-test controls were demonstrated red before the rules
  landed (count rule red twice over — NameError for the missing rule, then a real
  31-vs-32 drift on the tree; placement rule red via the fixture, then a real defect —
  this change's own CLS-013 ledger row — caught and fixed in the same session).
- Requirement-ID tracking is retired (1ee535a); the delta carries no `> req:` header.
