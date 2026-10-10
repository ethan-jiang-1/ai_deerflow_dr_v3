# Proposal: establish-lint-lane

## Why

`pyproject.toml` dev 组已配 ruff（>=0.14.11，select E/F/I/UP/B/ASYNC，line-length 120，
注释自认 "CI does not enforce it"），`change-practice.md` 曾要求 slice 收口
"run lint and tests"，但仓库不存在 lint 命令位（Makefile/COMMANDS 均无），基线实测
**108 违规**——lint 是一条被要求却不可执行的纪律。issue 卡
`_backlog/issues/2026-10-10-lint-lane-establishment.md` 在案；本次审计为守住"不交付
长红 lane"已把 change-practice 措辞临时对齐为 "run the tests"。

## What Changes

- 分级把 108 条 ruff 违规修绿：机械类（UP012/UP017/UP037/UP035、E501、E741、E731）
  逐批修复 + 红绿；敏感类逐条判定（F401 seam 保留 vs 真无用、F821 注解名导入、
  F841 刻意赋值、E402 sys.path 既定模式、I001 含注释 import 的重排损伤、B007）。
- `deep_research_harness/Makefile` 增 `make lint`（`ruff check src tests tools cli.py`，
  UV 约定同 smoke），`.PHONY` 同步。
- `deep_research_harness/COMMANDS.md` 测试 lane 增 `make lint` 行；
  `pyproject.toml` dev 组注释更新；`change-practice.md` 措辞恢复为
  "run lint and tests"。
- 不进 CI canonical 序列（`check_ci_governance.py` 声明面不动，pre-commit hook 不扩）。

## Capabilities

### New Capabilities

（无——dev 工具面无可观察产品行为，已声明 `skip_specs`；COMMANDS 菜单行由
agent-playbook 既有 "SHALL mirror the closed entry-surface vocabulary plus the declared
make targets" 条款覆盖。）

### Modified Capabilities

（无）

## Impact

- 影响：约 20 个 `deep_research_harness/` 下 src/tests/tools 文件（行为不变的重排、
  注解、行长改写）+ Makefile / COMMANDS / pyproject / change-practice 四个接线点。
- 风险：F401 中存在 seam 保留导入与 `test_entry_chain` 的 AST 锁链——每批以
  `make verify` 红绿验证；E402 是 sys.path 注入后的既定模式，以带理由的就地 noqa
  处置而非重排。
- 边界：不修改 `deerflow/`；不改任何运行时行为；不新增依赖、不改 ruff select 规则集。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/pyproject.toml`（ruff 配置
  与 dev 组声明）+ `deep_research_harness/Makefile`（命令位）——两者共同拥有"lint 是
  本仓纪律"这一决定；108 条修违规件是 payload，不是 owner。
- **Seam classification:** wiring — dev 工具接线与既有代码的 lint 合规；无运行时行为、
  无生命周期结果变更。
- **Question:** 能否让 "run lint" 成为可执行且绿的 slice 收口纪律，而不动任何运行时
  行为、不制造永久豁免面？
- **Necessary adjacent/external contracts:** `test_entry_chain` / `test_binding_doc_guard`
  （answers: AST 锁链与文档守卫在 import 重排后必须保持绿——批次红绿的判据）；
  agent-playbook spec（answers: COMMANDS 菜单与 declared make targets 的镜像条款允许
  新增行，无需 delta）；`_backlog/issues/2026-10-10-lint-lane-establishment.md`
  （answers: 缺陷出处、基线取证与关闭条件）。
- **Evidence seam:** `make lint` exit 0（全树）+ 每批后 `cd deep_research_harness &&
  UV_OFFLINE=1 make verify` exit 0 + 红演示（临时违例文件使 lint 红、移除后复绿）。
- **Not in scope:** CI canonical 序列扩员、pre-commit hook 扩员、ruff 版本升级、
  lint 规则集（select）变更、per-file-ignores 级整体豁免。
- **Triggered review policies:** change-admission, agent-information-map, local-context
