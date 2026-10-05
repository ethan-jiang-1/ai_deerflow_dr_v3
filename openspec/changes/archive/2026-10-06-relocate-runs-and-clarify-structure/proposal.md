# Proposal

## Why

The project's driver — and any fresh coding agent — cannot locate the runtime entry
chain, run-bundle state, or test assets without paying an exploration tax: ~1GB of
gitignored run-bundle data (`scopes/`) physically sits inside the application subtree
and dominates every directory listing; one concept carries three names (scope / bundle /
run bundle: concept docs say "Run Bundle", code lives in `runtime/bundle/`, data lands
in `scopes/`); and the repository root README routes to maps instead of showing one
map. The structure is mostly sound — it is illegible.

## What Changes

- **BREAKING** Run-bundle storage root moves out of the application subtree:
  `deep_research_harness/scopes/` → repository-root `runs/`
  (`runs/d_YYYYMMDD/<bundle-id>/`). Bundle-internal layout is unchanged.
- The runs root resolves from one place: `runtime/entry.py` consumes the single domain
  path constant (retiring the dead `SCOPE_ROOT` constant and the entry-side `"scopes"`
  literal that today violates the single-declaration discipline); a
  `DEEP_RESEARCH_RUNS_ROOT` environment variable overrides the root for tests and tools.
- Existing local bundle data is physically relocated (one-time move). `state.json`
  embeds no absolute paths (verified across existing bundles), so relocated bundles
  remain fully readable.
- Vocabulary unification: the `scope`/`scopes` name is retired from code, messages, and
  docs; one word for the concept — Run Bundle — one home — `runs/`.
- `deep_research_harness/playbook/` folds into `deep_research_harness/docs/playbook/`
  (one fewer top-level resident; docs stay in docs).
- `runtime/fixtures/` (the scripted-ladder providers: ScriptedChatModel,
  FakeWebSearchTool, replay model) renames to `runtime/scripted/`, ending the name
  collision with `tests/fixtures/` (sample data). The composition ladder name `fixture`
  is unchanged; config `use:` seams and the contract mirror are updated.
- The repository root README becomes a one-screen map: the entry chain, the directory
  table, and the run/debug/test lanes shown inline; the link routing list is demoted
  below it.
- Governance registry sync: `required-paths.toml` (moved/renamed paths),
  `project-structure.toml` ignored-paths (`scopes/` → root `runs/`),
  `deep_research_harness/.gitignore`, and the root `.gitignore`.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `run-bundle`: the bundle directory contract changes root and name — bundles live at
  `runs/{bucket}/{bundle_id}/` under the repository root, outside the application
  subtree, with the root overridable by environment for non-default checkouts; and the
  single-path-declaration discipline gains an enforced scenario (the runtime resolves
  the root directory name from the domain constant, not from a second literal).
- `agent-playbook`: playbook routing targets live under
  `deep_research_harness/docs/playbook/`.

## Impact

- Code: `domain/bundle.py` (root-name constant, `bundle_dir` naming, error text),
  `runtime/entry.py` (RUNS_ROOT + env override), `runtime/interaction/cli.py`
  (attribute rename), `runtime/fixtures/` → `runtime/scripted/`,
  `config/fixture.yaml` (`use:` seams), `tools/record_stream.py` (`--runs-root`).
- Tests: `test_bundle_domain.py`, `test_entry_composition.py`,
  `test_refine_foreground.py`, `test_status_delivery.py`, `test_wiring_mirror.py`,
  `test_cli_journey.py` (path and attribute references).
- Docs: root `README.md` (one-screen map), harness `README.md`, `COMMANDS.md`,
  `docs/control-map.md`, `docs/run-bundle.md`, `docs/testing-and-evaluation.md`,
  `docs/known-limitations.md`, `tests/README.md`, `tools/README.md`, `AGENTS.md`
  routing lines.
- Governance: `openspec/governance/required-paths.toml`,
  `openspec/governance/project-structure.toml`, `deep_research_harness/.gitignore`,
  root `.gitignore`.
- Local data: `deep_research_harness/scopes/` (~1GB, gitignored) physically moved to
  repository-root `runs/`; no state schema change; old bundles stay readable.

## Change Focus

- **Primary module / causal owner:** `domain/bundle.py` — owns the bundle path
  contract and the single path-declaration discipline; where run-bundle state lives
  is a path-contract decision owned there.
- **Seam classification:** wiring — the change relocates storage, renames a provider
  module, and reorganizes maps; it alters no state-machine, admission, or cognitive
  semantics.
- **Question:** Where must run-bundle state live and be named so that the human driver
  and a fresh coding agent can find the entry chain, runtime state, and test assets
  without an exploration tax?
- **Necessary adjacent/external contracts:** agent-playbook spec, entry-surface CLI wiring, deerflow-wiring fixture config, governance project-structure registry — each names the question it answers:
  - `agent-playbook` spec — under which directory may CLI routing targets live?
  - `entry-surface` — does the CLI consume the runs root from the runtime entry
    instead of re-declaring it?
  - `deerflow-wiring` fixture config — which module path do the `use:` seams point
    at after the rename, and does the mirror still lock the seam?
  - governance `project-structure` registry — do the inventory and ignored-path
    entries match the new layout exactly?
- **Evidence seam:** red-green first on
  `tests/unit/domain/test_bundle_domain.py` and
  `tests/unit/interaction/test_entry_composition.py`; then the contract mirror
  (`tests/contract/test_wiring_mirror.py`); `make verify` and the governance checkers
  green as the gate.
- **Not in scope:** run-engine behavior, admission/validator semantics, `state.json`
  schema, `deerflow/` (read-only), multi-operator semantics, `.agents/skills/` user
  area, research-quality evaluation.
- **Triggered review policies:** control-placement, agent-information-map

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| Run-bundle 存储根迁出应用子树（scopes/ → 仓库根 runs/） | Human judgment（驾驭者裁决：探索税是主诉；$HOME 方案被拒） | domain/bundle.py 的 RUNS_ROOT_NAME + entry.runs_root() 单点解析 | non-bypassable | 路径合同单点声明；state 记录无绝对路径（迁移前后可读） | 应用树不再被 1GB 运行数据污染；ls/find/glob 免税 | 红先行：test_bundle_domain + entry 组装测试（默认根在应用外、env 覆盖重定向、整体搬移仍可操作） |
| DEEP_RESEARCH_RUNS_ROOT 环境覆盖 | 无认知候选 | entry.runs_root() 读 env，缺省回落仓库根 | advisory | 未设 env 时默认解析不变（不改变既有 checkout 行为） | 测试/工具不再需要 monkeypatch 模块常量 | RunsRootResolutionTest 两条直测 |
| runtime/fixtures → runtime/scripted 改名 | 无认知候选 | config use: 缝指向新模块；contract mirror 锁定 | non-bypassable | fixture 梯（composition 值）不动；只改 provider 模块名 | 与 tests/fixtures（样本数据）的撞名消除 | mirror 断言新旧模块名（新名必须在、旧名不得存留） |
| playbook 并入 docs/playbook | Human judgment（文档归 docs，单一顶层居民原则） | agent-playbook 测试 + release-face 守卫校验路由目标存在 | non-bypassable | COMMANDS 仍是 routing-only 菜单，不嵌过程 | 顶层少一个目录；地图集中 | routing-target 存在性测试（test_agent_playbook） |
