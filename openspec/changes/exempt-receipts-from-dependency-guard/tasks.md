# Tasks

## 1. Red-first negative controls (governance unittest)

- [x] 1.1 Create `openspec/tests/governance/test_harness_dependency_direction.py`
  modeled on `test_release_face.py` (non-git temp fixture trees, the checker invoked
  as a subprocess with the fixture root passed as its `project_root` argument, exit
  codes read from `returncode` directly — never through a pipe) with three fixtures:
  (a) a structurally valid `verification-receipt.json` recording governance command
  argv that contains `openspec/`; (b) a harness `.py` file whose text carries
  `openspec/`; (c) a file named `verification-receipt.json` whose content is not
  receipt-shaped but carries `openspec/`, and a receipt-named JSON whose `checks`
  list is empty while the token hides in another field. Fixtures sit outside any git
  index, so a red fixture (a) and a red fixture (b) together evidence the
  untracked-file scan scenario. Also assert the real repository tree exits 0 with
  `REPO_ROOT` passed explicitly as the checker's `project_root` argument. Verify:
  fixture (a) and the real-tree assertion FAIL on the current checker with the
  forbidden-token message (red-first proof, captured in the verification receipt of
  task 4.2); the planted-violation fixtures already exit non-zero naming file and
  token.
- [x] 1.2 Run the full governance unittest suite
  (`python3 -m unittest discover -s openspec/tests/governance -q` from the repo
  root) and verify the only failures are the two receipt-exemption assertions —
  fixture (a) and the real-tree test, both naming the receipt false positive —
  proving the new controls bite and nothing else regressed.

## 2. Checker exemption (green)

- [x] 2.1 Implement the structural recognition predicate in
  `openspec/governance/check_harness_dependency_direction.py`: a file named exactly
  `verification-receipt.json` is exempt iff `json.loads` yields a dict whose
  top-level `checks` is a non-empty list of dicts each carrying a `command` key;
  anything else with that name, and every other file, is scanned as before. Update
  the docstring with the exemption rule and the `@impl DEP-001` marker. Verify:
  `python3 openspec/governance/check_harness_dependency_direction.py` exits 0 on the
  real tree (the skills receipt no longer trips), and the unittest suite from 1.2 is
  fully green — fixture (a) passes, (b) and (c) still detect their planted
  violations.

## 3. Evidence disposition (gitignore anchor, tracking, registration)

- [x] 3.1 Anchor the root `.gitignore` rule `skills/` to `/skills/` (keep the two
  `!.agents/skills/` negation lines unchanged). Verify with `git check-ignore`,
  reading each exit code directly: a path under
  `deep_research_harness/docs/skills/` is NOT ignored (non-zero, no match), and a
  hypothetical root `skills/x` still matches the anchored rule (zero).
- [x] 3.2 `git add` the existing
  `deep_research_harness/docs/skills/deep-research/verification-receipt.json`
  unchanged (no content edits), and register it in
  `openspec/governance/required-paths.toml` inside `[paths.repo-skeleton]` next to
  its sibling `provenance.json`; register the new test file in the same group next
  to the checker's existing entry. Verify: `git status` shows the receipt staged
  with no content change, and
  `python3 openspec/governance/check_project_architecture.py` exits 0 with both new
  paths present.
- [x] 3.3 Register `DEP-001` in the `openspec/governance/project-structure.toml`
  comment block (one line, following the CIG/DOB/RLF entries) and update the
  `openspec/governance/README.md` row for the dependency checker to name the
  structural receipt exemption and the `@impl DEP-001` marker. Verify:
  `python3 openspec/governance/check_doc_hygiene.py` exits 0 (budget/encoding
  intact) and the README table renders the updated row.

## 4. Closeout evidence

- [x] 4.1 Run the full closeout set from the repo root, reading every exit code
  directly (no pipes): the governance unittest suite, the dependency checker itself,
  `check_project_gate.py --phase closeout` (aggregate, must be 0 — the blocking red
  is gone), `check_doc_hygiene.py`, `check_project_architecture.py`,
  `make verify` in `deep_research_harness/`, `git check-ignore` both directions,
  `git diff --check`, and `git diff --exit-code HEAD -- deerflow`. All must exit 0,
  except `git check-ignore` on the docs/skills receipt path, which must exit 1 (no
  rule matches — the anchored rule no longer swallows it).
- [x] 4.2 Write this change's verification receipt into the change directory:
  fresh, runner-written, recording each command with its argv, cwd, actual exit
  code, stdout/stderr, the HEAD revision, the dirty-worktree status, and per-file
  digests of the surfaces this change touched; note as UNVERIFIED anything not
  executed (e.g., no CI run performed locally); record the `make smoke` status — no
  proof-lane surface is touched by this change, so state whether it ran and, if not,
  why it is not owed. Verify: the receipt is newer than the last code edit and every
  recorded exit code matches its documented expectation.
