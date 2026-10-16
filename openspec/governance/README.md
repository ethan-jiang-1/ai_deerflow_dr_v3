# openspec/governance — OpenSpec 治理导航

> 项目级 OpenSpec 治理扩展（非 OpenSpec 原生）。技术栈为 **Python 标准库**（零外部依赖，
> 永远可跑）。本文件是目录导航：每份治理对象的权威细节由其自有文件拥有，这里只负责
> "何时读哪个"。

## 何时读

| 对象 | 读者问题 | 权威细节位于 |
|------|----------|--------------|
| `architecture-policy.md` | 什么算 active spec、结构权威如何分工？ | [architecture-policy.md](architecture-policy.md) |
| Project-structure manifest（`project-structure.toml` 契约 + `required-paths.toml` 清单） | 精确目录 / import 清单？ | [project-structure.toml](project-structure.toml) · [required-paths.toml](required-paths.toml) |
| `check_project_specs.py` | main spec 结构是否有效？归档 delta 的 ADDED requirement 是否钉进主 spec（delta-sync 完整性；豁免面 = 后续 REMOVED/RENAMED 正式退役 + 带理由 allowlist）？ | 脚本 docstring |
| `check_project_architecture.py` | 结构治理是否通过？ | 脚本 docstring |
| `check_change_guidance.py` | Change Guidance / policy 路由 / Focus Card（即 proposal 的 `## Change Focus` 记录）是否通过？ | 脚本 docstring |
| `check_harness_dependency_direction.py` | Harness 是否反向依赖 OpenSpec？验证回执（`verification-receipt.json`，结构识别：非空 `checks` 命令记录）是豁免证据，不是依赖 | 脚本 docstring（`@impl DEP-001`） |
| `check_ci_governance.py` | CI 工作流与本地 hook 的声明是否漂移（触发器、路径过滤、pinned 工具链、canonical 命令、hook 命令集）？ | 脚本 docstring（`@impl CIG-001`） |
| `check_doc_hygiene.py` | 文档层（ADR 索引↔目录、docs 层与测试/工具资产文档的相对链接与编码换行、docs 范围完整性、`_backlog` 的 `_` 目录约定与账本面一致性（名册互查 / 计数与 Next-ID / 户口与滞留检测）、入口层字符预算棘轮、陈旧叙事封闭清单、根 README 计数钉死——约十条机械规则）是否漂移？ | 脚本 docstring（standalone，非 gate 组件、非 `make verify` 目标；已进 CI canonical 序列；`@impl DOB-001`） |
| `check_code_budgets.py` | 治理脚本自身的体积是否越界（声明式行数上限 + 超长函数个数上限；只降不升的棘轮；自带种植负例）？ | 脚本 docstring（standalone，非 gate 组件；已进 CI canonical 序列与 pre-commit；`@impl DOB-001`） |
| `check_release_face.py` | 最小发布面是否完整（gitlink 在场且 pin 一致 / 兄弟布局与 `[tool.uv.sources]` 目标都在发布面内 / 随行源码零开发面耦合 / COMMANDS 路由目标存在）？ | 脚本 docstring（standalone，slow cold-start lane 见 playbook；`@impl RLF-001`） |
| `check_proof_receipts.py` | 选中 change 的回执/证据是否在案（proof receipts）？ | 脚本 docstring（gate 组件：经 `--mode enforce` 调用，但仅当环境变量 `PROOF_ATTESTATION` 提供 attestation 时才实查，否则报 no selected change 并按 0 通过；回执 producer `make proof` 尚未建立，见 harness `proof-lanes.toml`） |
| `selected-change-closeout.md` / `selected_change_closeout.py` | 选中 change 的 closeout 义务清单与执行？ | 文档+脚本（`@impl` 见文件头） |
| `change_guidance_kernel.py` | change-guidance 规则的共享内核（checker 复用）？ | 脚本 docstring |
| `portable_change_guidance_export.py` | 指导规则的可移植导出是否最新？ | 脚本 docstring |
| `test-evidence-policy.md` | 测试证据的 authority、lifecycle、synchronized-change？ | [test-evidence-policy.md](test-evidence-policy.md)；批准语义由测试证据的 owning main spec 拥有（随 v3 首批治理 change 建立） |
| `change-guidance/README.md` | 先按什么原则、再选哪个 policy？ | [change-guidance/README.md](../change-guidance/README.md) |

`governance/` is checker and registry navigation, not product documentation. For
Deep Research-specific orientation, leave this directory and read the
[product context](../product/README.md) reading map.

## Checker 命令

在 repo 根运行（默认扫当前目录；也可传 projectRoot 参数）：

```bash
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_change_guidance.py
python3 openspec/governance/check_harness_dependency_direction.py
python3 openspec/governance/check_ci_governance.py
python3 openspec/governance/check_proof_receipts.py
```

共六个 component checker（closeout gate 的实装清单，见 `check_project_gate.py` 的
`CHECKER_NAMES`）。每个 checker 拥有自己规则的全部语义；它们只读、不写 registry，也不修改
任何文件。`check_doc_hygiene.py` 与 `check_release_face.py` 是 gate 之外的独立检查，不在
component 清单内。

本地 pre-commit hook（版本化于 `.githooks/pre-commit`，只跑便宜高置信检查：
staged 空白检查 + doc hygiene；测试/快照/类型分析/构建一律属于 CI）。一次性激活：

```bash
git config core.hooksPath .githooks
```

CI 门禁：`.github/workflows/governance.yml` 在 push / pull request（路径过滤
`openspec/**`、`deep_research_harness/**`、工作流与 hooks 自身）上单 job 运行
canonical 序列——治理 unittest 套件（`openspec/tests/governance/`，`python3 -m unittest
discover -s openspec/tests/governance -q`）、聚合 closeout gate、doc hygiene、harness
`make verify`（UV_OFFLINE=1）、setup-uv + harness `make smoke`（fixture 梯集成 lane）、
harness `make lint`（ruff，2026-10-10 起 promote-lint-to-ci 升入序列）；任何非零退出即失败。声明由
`check_ci_governance.py` 机器校验。**契约双端触发**是本形态的
结构事实：单 job 全序列使任一受治理面（应用面 / 框架绑定面 / spec / 治理自身）
变更都跑完整序列，无需路径分流——这是主仓"契约两侧任一变更都触发回放门禁"
原则（上游参考：DeerFlow 应用开发语料·卷二 05，钉定 v2.1.0）在本仓单 job
形态下的等价实现。

文档层卫生另有独立 checker（不属于六 component 聚合、不进 `make verify`）：
`python3 openspec/governance/check_doc_hygiene.py`（含 `--self-test` 负例控制）；
它同时校验 `_backlog/` 的 `_` 前缀目录命名约定（磁盘、声明、README 三者一致）。
负例电池本身住在 `openspec/governance/_battery.py`（单一事实家：30 条负例控制 +
9 条绿色控制），并由治理套件 `openspec/tests/governance/test_doc_hygiene.py`
逐例跑成独立用例——`--self-test` 只是同一注册表的薄委托入口，命令、stdout 与
退出码不变。
代码体积另有独立 checker（同样不属于六 component 聚合）：
`python3 openspec/governance/check_code_budgets.py`——声明式上限表只管治理脚本自身，
上限取采纳时实测值、只降不升；超限点名文件、实测值、上限与违规函数，并自带
`--self-test` 种植负例。它已进 CI 与 pre-commit（由 ci-governance 的声明表钉住）。
共享基础设施住同目录顶层：`gitio.py`（统一的 git subprocess 调用）与 `roots.py`
（统一的根解析规则）。

## Canonical aggregate gate

`openspec/governance/check_project_gate.py`（标准库、零外部依赖、在 repo 根运行）
只编排并聚合上述六个 component checker 的退出码，不拥有规则语义、
不复刻任何解析。（别名对齐：config.yaml 称 root governance gate、归档惯例称
closeout gate，皆指本脚本；CI workflow 的 "Governance Gate" 是另含 harness
lane 的超集序列。）命令：

```bash
python3 openspec/governance/check_project_gate.py --phase plan --change <name>
python3 openspec/governance/check_project_gate.py --phase closeout
```

- `--phase plan --change <name>`：只读 admission 检查。调用各语义 owner 的 scoped
  模式（Change Guidance 检查 Focus Card；specs checker 的 selected-change scope 检查
  delta header 与标题；reqs checker 的 planning scope 检查 reservation/冲突/retired
  reuse；native strict validation 检查 MODIFIED 场景保留）。合法的新 ID 输出为
  `reservation: <id> (capability)`——reservation 只是只读占号提示，非权威、不写文件；
  正式登记 registry 由 apply 任务完成。
- `--phase closeout`：运行六个 component checker 并聚合退出码；任一非零即整体非零，
  并点名失败的 checker（proof-receipts 组件无 attestation 时休眠通过，见上表）。
  归档 agent workflow 在非零时停止；这是仓内 workflow 的
  确定性门禁，不阻断、不改变直接调用 native `openspec archive`。

正常校验路径 `0` = PASS，`1` = 有违规。注意：stderr 也可能包含 non-failing warning
（仍返回 0）；argparse usage error 属于命令用法错误，不属于 0/1 contract。

**退出码必须直测**：普通管道如 `cmd | tail` 只返回最后一个命令的退出码，会掩盖上游
checker 的非零结果。验证时直接读取命令自身的 exit code（例如 `echo $?` 或脚本内
`subprocess.run(...).returncode`），不要用管道产物判断通过与否。

`config.yaml` 的 `rules.tasks` 把归档前门禁固化为每个 change 的硬性收尾 task。
