# Tasks

## 1. 新内容落盘（红先行）

- [x] 1.1 Write `deep_research_harness/docs/control-map.md` per design decision
  1–3 and the content mapping table: sections for 结论与主链、两种 loop 职责表、
  三层职责与目录、create 真实路径、六动词语义与易误解、配置两梯、
  改什么→owner→最小测试路由表、权威边界、发布形态与未实现清单、最小车道选择、
  同轮维护。No stale markers; every rule statement links its owning code/spec.
  Verify: file exists and contains the two-loop table plus the four-line
  terminal/admission/quality distinction.
- [x] 1.2 Write `deep_research_harness/docs/run-bundle.md`: lifecycle (create →
  active → terminal; refine creates next generation, no auto-run), path contract,
  state authority (revision CAS + lease), the artifact ownership table
  (谁写/是什么/能看出什么/不能推出什么) absorbing runtime-map §3 Bundle
  contents and research-process's Bundle-object table, deletion permanence,
  observation-command division. Verify: file exists and covers every artifact
  named in `domain/bundle.py`'s path contract.
- [x] 1.3 Run `python3 openspec/governance/check_doc_hygiene.py` and verify it
  FAILS red naming the unregistered `control-map.md` (and `run-bundle.md`) —
  the red-first proof that the docs-layer registry is load-bearing. Capture the
  red output for the verification receipt.

## 2. 治理声明表注册（转绿）

- [x] 2.1 Update `openspec/governance/check_doc_hygiene.py`: add control-map.md
  and run-bundle.md to DOC_LAYER_DOCS and STALE_MARKER_FILES (they will be
  doc-layer files after step 3); rename the self-test bad-bytes fixture from
  runtime-architecture.md to control-map.md. Verify:
  `python3 openspec/governance/check_doc_hygiene.py --self-test` exits 0 and the
  plain run still fails only on the to-be-deleted legacy docs being unlinked-or-
  still-present state consistent with this phase (document what red remains and
  why: the legacy three are still present and still registered until task 4).
- [x] 2.2 Update `openspec/governance/check_change_guidance.py`
  (FOCUSED_DOC_PATHS: runtime-architecture.md → control-map.md;
  INFORMATION_MAP_POLICY_ANCHORS: same rename),
  `openspec/governance/required-paths.toml` (replace the three legacy doc
  entries with control-map.md and run-bundle.md), and
  `openspec/tests/governance/test_project_gate.py` fixture source entry (same
  rename). Verify: `python3 openspec/governance/check_change_guidance.py`
  reports only the expected state (app README / docs index do not yet link
  control-map.md — that lands in task 3; record exact remaining violations).

## 3. 定点补强与路由面更新

- [x] 3.1 Update `deep_research_harness/docs/research-process.md`: add the skill
  three-column state table (声明可用 → docs/skills 快照与框架 native surface；
  实际加载 → available_skills=None 不强制，须工具调用/checkpoint/snapshot 证据；
  质量评估 → 无自动统计评估，显式真实梯 + 人工评审); replace the Bundle-object
  table with a pointer to run-bundle.md keeping the 判断 skill/委派/完成/质量
  guidance. Verify: no content duplicated from run-bundle.md's ownership table;
  links resolve.
- [x] 3.2 Update `deep_research_harness/docs/testing-and-evaluation.md`: absorb
  from runtime-map §6 the cold-start lane row, the three quality objects, and
  the minimal-lane chooser. Verify: lane table now covers unit/smoke/real/
  cold-start/governance and every "不证明什么" column survives.
- [x] 3.3 Update routing surfaces: `docs/README.md` index (remove 3 rows, add
  control-map + run-bundle rows), app `README.md` Reading Map (rows 25/32/63 →
  control-map/run-bundle), `AGENTS.md` Information Map (merge Repo-map and
  Runtime-map rows net-negative), root `README.md` (lines ~51/54), and
  `openspec/change-guidance/local/deep-research.md` Reader Roles row. Measure
  AGENTS.md size and lower its DOC_BUDGETS ceiling from 6863 to the measured
  value in the same edit. Verify: `check_doc_hygiene.py` exits 0 (budget,
  links, encoding all green) and AGENTS.md measures at or under the new ceiling.

## 4. 删除旧文档并全绿

- [x] 4.1 Delete `deep_research_harness/docs/repository-map.md`,
  `runtime-map.md`, `runtime-architecture.md`. Run from repo root with direct
  exit codes: `check_doc_hygiene.py` (0 — docs-layer completeness matches disk,
  no dangling links), `check_change_guidance.py` (0 — focused-doc chain
  resolves), `check_project_architecture.py` (0), governance unittest suite
  (0), `make verify` in deep_research_harness (0), `git diff --check` (0).

## 5. Closeout 证据

- [x] 5.1 Run the full closeout set with directly-read exit codes: governance
  unittest suite, `check_project_gate.py --phase closeout`, `check_doc_hygiene.py`
  (+ `--self-test`), `check_project_architecture.py`, `check_project_specs.py`,
  `make verify`, `git diff --check`, `git diff --exit-code HEAD -- deerflow`;
  plus `make smoke` status recorded (not owed: no proof-lane surface — src/,
  tests/, cli.py, tools/ untouched — but run it if cheap since docs sit beside
  consumed surfaces). All recorded exits must match expectation.
- [x] 5.2 Write the verification receipt into the change directory: fresh,
  runner-written, argv/cwd/exit/stdout/stderr per check, HEAD revision, dirty
  status, per-file digests of every touched surface, the task-1.3 red output
  quoted, UNVERIFIED notes (no local CI run; smoke status). Verify: receipt is
  newer than the last edit and every recorded exit matches its expectation.
