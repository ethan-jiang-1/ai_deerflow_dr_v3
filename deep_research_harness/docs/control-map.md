# 控制地图：从研究问题到最终报告

> 本文件是应用唯一控制总图：主链、两种 loop、权威边界与"改什么找谁"路由。
> 运行事实的权威是 owning code / spec / test；本文是导航，不是第二套业务规则。
> 直接下钻：[Run Bundle 持久化](run-bundle.md) · [研究过程 / skill / 证据](research-process.md) ·
> [测试资产](../tests/README.md) · [本地操作](local-operations.md) · [车道策略](testing-and-evaluation.md)

## 1. 先给结论

当前项目不是写死的"搜索 → 分析 → 写报告"静态流水线，也不是已部署的 Web 服务：

```text
用户 / 操作者
    │  当前入口：cli.py → runtime/interaction/cli.py
    ▼
Harness 运行底座
    ├─ 创建和管理 Run Bundle（详见 Run Bundle 地图）
    ├─ 启动一次 DeerFlow 研究运行
    ├─ 记录 journal / checkpoint / diagnostics
    ├─ 处理取消、崩溃转移、有限澄清续答
    └─ 对最终报告做确定性准入
    │
    ▼
DeerFlow 宿主运行时
    ├─ lead agent（按需加载 skill、决定下一步）
    ├─ web_search / web_fetch 等工具
    ├─ 按需派生 subagent
    └─ LangGraph / checkpointer / middleware
    │
    ▼
模型与外部工具
    ├─ fixture：脚本模型和假搜索，零凭证
    └─ base：真实模型和真实 Web 工具，需凭证
```

**最重要的一句话：** 研究内容的动态过程由 DeerFlow 原生 agent 运行时驱动；本项目的
Harness 不决定每一步搜什么，而是把一次研究运行装进可追踪、可恢复判断、可检查、
可接纳的 Run Bundle 里。

## 2. 两种 loop：谁驱动什么

这是本项目最容易被误解的分界。**两种 loop 同时存在，职责不重叠：**

| | DeerFlow 宿主 agent loop | Harness run loop |
| --- | --- | --- |
| 驱动者 | lead agent（框架，随行 `deerflow/`） | [pump](../src/deerflow_deep_research/runtime/pump.py)（本应用） |
| 决定什么 | 查什么问题、用哪个工具、何时抓全文、是否派生 subagent、何时收束写报告 | 消费 stream 事件、有限自动续答（默认 ≤2 次）、取消/错误观察、终态判定、journal 投影、最终报告准入 |
| 不决定什么 | 不能越过 Harness 准入把产物当已接受事实写入 final/evidence | 不决定每步搜什么；不复制 agent loop；不重新发明 domain 终态规则 |
| 代码入口 | [client 绑定](../src/deerflow_deep_research/runtime/adapters/client.py)（`make_stream_fn` 是唯一 stream 缝，per-call recursion limit） | [pump](../src/deerflow_deep_research/runtime/pump.py) 消费 `_consume_turn` |
| 运行证据 | checkpoint.sqlite、assembly-snapshot、journal 里的 model/tool/subagent 事件 | state.json、journal.jsonl、admission ledger |

由此必须持续区分四件**不是同一件事**的事（当前 run engine 先写 terminal 再提交报告）：

```text
agent stream 结束  ≠  Harness state = completed  ≠  final report 被 admission  ≠  研究事实质量达标
```

"workflow"一词在本项目至少有三种含义，文档与讨论中应写明是哪一种：DeerFlow 动态
研究过程、Harness Run Bundle 生命周期、开发/测试质量车道。

## 3. 三层职责与目录

| 层 | 负责什么 | 位置 |
| --- | --- | --- |
| `domain` | 纯业务事实和规则：状态、生命周期、路径合同、journal 词汇 | `src/deerflow_deep_research/domain/` |
| `engine` | 确定性裁决：validator、admission gate、质量机器 | `src/deerflow_deep_research/engine/` |
| `agents` | 预留 Harness 自有 bounded model role；**当前为空**（空包不代表实现） | `src/deerflow_deep_research/agents/` |
| `runtime` | 装配、DeerFlow binding、运行控制、持久化、交互、诊断 | `src/deerflow_deep_research/runtime/` |
| 交互入口 | 稳定 launcher 转交七动词解析/输出；不承载状态规则 | `cli.py` → `runtime/interaction/cli.py` |
| 运行装配 | 配置、pin、Bundle 查找、前台 client/saver 装配 | `runtime/assembly.py` |

```text
deep_research_harness/
|-- cli.py                      稳定启动入口，转交交互实现
|-- config/                     模型、工具和框架配置（base / fixture 两梯）
|-- src/deerflow_deep_research/ 四个所有权层（见上表）
|   `-- runtime/scripted/       脚本梯 providers（ScriptedChatModel、假搜索）
|-- tests/                      unit / contract / integration / fixtures
|-- tools/                      显式录制等开发操作，不是测试
|-- docs/                       按问题查阅的地图（本文件是总图）
|   |-- skills/deep-research/   研究 SOP 原文快照（参考，不是运行时配置）
|   `-- playbook/               操作步骤与完成判据
`-- proof-lanes.toml            回执车道声明，不是测试 runner

runs/                           （仓库根）本地 Run Bundle 数据，gitignored，
                                应用子树之外；env DEEP_RESEARCH_RUNS_ROOT 可覆盖
```

仓库根还有：`deerflow/`（锁定上游，**只读**，普通工作不修改不深读其内部）、
`runs/`（每次研究的 Run Bundle 数据，gitignored）、
OpenSpec 开发工作区（规范、准入与治理 checker）、`_backlog/`（计划与任务账本）。
它们不属于发布运行时。本仓库的 coding agent 是**开发过程参与者**，不是产品运行
节点：不代替 lead agent 搜索、不把提示词当运行时权限、不修改上游框架来"修好"
产品行为。

## 4. 一次 create 的真实路径

入口链六环。本图是人读投影；**机械权威是锁链契约测试**
[test_entry_chain](../tests/contract/test_entry_chain.py)——任何一环被替换、绕过或
改名漏切，`make verify` 即红（离线 AST 断言，不锁行号，阶段内重构不误伤）：

```text
1. 稳定 launcher 转交七动词        cli.py → runtime/interaction/cli.py
2. 原子创建 Run Bundle             runtime/bundle/bundle_actions.py（+ domain/state_machine.py）
3. 前台装配                        runtime/assembly.py::run_foreground
                                   （读 pin、开 checkpointer、build_client、make_stream_fn）
4. DeerFlow 内部循环（动态）        lead agent + skill + tools + subagents
5. Harness 运行泵                  runtime/pump.py（消费事件、有限续答、计划闸、取消、终态）
6. 终态交付准入                     runtime/bundle/admission.py（validator 先裁决）→ final/
```

每个 Bundle 里持久化了什么、谁写的、能看出什么 → [Run Bundle 地图](run-bundle.md)。
研究认知侧（skill、模型、工具、委派）的实际证据 → [研究过程地图](research-process.md)。

## 5. 七个动词到底做什么

语义权威是 `entry-surface` spec 与 [COMMANDS](../COMMANDS.md)；这里是易误解点：

| 动词 | 做什么 | 不做什么 |
| --- | --- | --- |
| `create` | 创建 Bundle 并**前台**驱动运行 | 不是后台任务提交 |
| `watch` | 投影 journal，遇 terminal 退出 | 不驱动研究 |
| `status` | 读 state、journal 摘要、owner PID 存活 | 不证明质量 |
| `cancel` | **只记录**取消请求 | 由运行泵在下个检查点协作终止 |
| `refine` | 创建下一代并**前台跑完该代**（消息 = 该代方向文档，梯 = bundle 自声明延续） | 不是后台提交；耗时与 create 同级 |
| `inspect` | journal 时间线、已接纳产物、装配快照 | 是诊断投影，不是第二事实源 |
| `diagnose` | 终态分类（七类互斥）+ 断点环节 + 证据文件指针 | 只读投影，不改任何 Bundle 工件；不是生命周期权威 |

## 6. 配置两梯

| 梯 | 凭证 | 回答的问题 | 不回答 |
| --- | --- | --- | --- |
| `fixture`（默认） | 零凭证 | 发布面自足吗？接线/状态/事件/报告落盘能工作吗？ | 真实研究质量 |
| `base` | 需 `$DEEPSEEK_API_KEY` 等 | 当前模型、skill、工具下一次真实研究的行为与质量 | 统计意义上的稳定质量 |

配置文件是 [base.yaml](../config/base.yaml) / [fixture.yaml](../config/fixture.yaml)；
`mixed` 是尚未接线的枚举成员。模型/工具细节见研究过程地图。

## 7. 改什么，就找哪个 owner，先测哪里

合并自原 repo 地图与运行态总图的路由表。规则：先跑最小 seam 的测试变红/变绿，再
按风险扩大 lane；不要从 CLI 文案或端到端开始改规则。

| 对象 / 你要改变什么 | 直接入口 | 最小证据 |
| --- | --- | --- |
| Bundle 状态、generation、终态 | [state_machine](../src/deerflow_deep_research/domain/state_machine.py) | [test_bundle_domain](../tests/unit/domain/test_bundle_domain.py) |
| 澄清上限、journal 词汇、artifact 合同 | domain 的 clarification / journal_policy / admission | 同上、[test_admission_engine](../tests/unit/engine/test_admission_engine.py) |
| 创建、取消、refine、owner 存活 | [bundle_actions](../src/deerflow_deep_research/runtime/bundle/bundle_actions.py) | [test_bundle_runtime](../tests/unit/runtime/test_bundle_runtime.py) |
| state 读取 / revision / 目录 identity | [bundle_state](../src/deerflow_deep_research/runtime/bundle/bundle_state.py) | [test_state_read_diagnosis](../tests/unit/runtime/test_state_read_diagnosis.py) |
| 产物是否合法、阶段 admit 数量 | engine 的 validator / gate / verdicts | [test_admission_engine](../tests/unit/engine/test_admission_engine.py)（gate 不等于已接入四阶段图） |
| 准入落盘、账本、原子写入 | runtime 的 admission / ledger / atomic | [test_admission_runtime](../tests/unit/runtime/test_admission_runtime.py) |
| stream / 续答 / 错误 / 最终回答投影 | [pump](../src/deerflow_deep_research/runtime/pump.py)、[journal](../src/deerflow_deep_research/runtime/bundle/journal.py) | [test_run_engine](../tests/unit/runtime/test_run_engine.py)、[事件回放](../tests/unit/runtime/test_event_stream_replay.py) |
| checkout 定位与前台装配 | [entry](../src/deerflow_deep_research/runtime/assembly.py) | [test_entry_composition](../tests/unit/interaction/test_entry_composition.py) |
| CLI 解析、文案、直播/观察 | [interaction cli](../src/deerflow_deep_research/runtime/interaction/cli.py)、[render](../src/deerflow_deep_research/runtime/interaction/render.py) | [test_entry_surface](../tests/unit/interaction/test_entry_surface.py)、[CLI 旅程](../tests/integration/test_cli_journey.py) |
| client 装配 / checkpoint / 递归上限 | [client](../src/deerflow_deep_research/runtime/adapters/client.py)、[接口镜像](../src/deerflow_deep_research/runtime/adapters/contracts/client_surface.py) | [test_wiring_mirror](../tests/contract/test_wiring_mirror.py)、[smoke](../tests/integration/test_wiring_smoke.py) |
| prompt/tool 装配观测、委派声明 | [snapshot](../src/deerflow_deep_research/runtime/adapters/snapshot_middleware.py)、[posture](../src/deerflow_deep_research/runtime/adapters/subagent_posture.py) | smoke、[test_subagent_posture](../tests/unit/runtime/test_subagent_posture.py) |
| 搜索、模型、摘要策略 | [base](../config/base.yaml)、[fixture](../config/fixture.yaml) | 配置 smoke；真实研究质量另评审 |
| 质量机器登记、命令导航 | [machines](../src/deerflow_deep_research/engine/machines.py)、[quality register](quality-register.md)、[COMMANDS](../COMMANDS.md) | [test_admission_engine](../tests/unit/engine/test_admission_engine.py)、[test_command_surface](../tests/unit/interaction/test_command_surface.py) |
| 事件录制、样本来源/消费者 | [tools](../tools/README.md)、[fixtures](../tests/fixtures/README.md) | 显式录制 + 对应 replay 测试 |
| 未来 harness model role | [agents 包](../src/deerflow_deep_research/agents/__init__.py) | 先定义角色合同再放代码；空包不代表实现 |

## 8. 权威边界

- **研究认知引擎 = DeerFlow 原生能力**：lead agent 可读取 `deep-research` skill，
  按需派生 subagent；框架侧没有静态研究图。Harness 经
  [client 绑定](../src/deerflow_deep_research/runtime/adapters/client.py) 的公开面进入
  （embedded binding，由 establish-embedded-wiring 定案，受
  `check_harness_dependency_direction.py` 守护：应用不反向依赖治理面）。
- **Harness 保留**：Run Bundle 生命周期（七动词）、确定性控制边界（engine
  validator/gate + runtime admission/ledger）、journal 与 final 报告投影、
  显式组成记录（`fixture` / `all_real` / `mixed`，`mixed` 为声明未接线枚举）。
- **DeerFlow 是宿主运行时，不 import 本包**；本包也不 import 上游之外的治理面。
- **权威事实源**：Run Bundle 合同 = `run-bundle` spec；验收收口 = `run-admission`
  spec；入口面 = `entry-surface` spec；框架接线 = `deerflow-wiring` spec；
  结构清单 = project-structure manifest。边界决策的历史推敲见
  [`_backlog/_done/_closed_plans/`](../../_backlog/_done/_closed_plans/README.md)。

## 9. 发布形态与未实现清单

当前发布面**不是** wheel、Docker、Web 或 K8s 服务，而是一个递归 clone 的源码两件套：

```text
git clone --recursive <repo-url>     # deep_research_harness/ + deerflow/（锁定 submodule，兄弟布局）
cd deep_research_harness && uv sync && make verify
make create PROBLEM="研究问题"        # 默认 fixture，零凭证
make create PROBLEM="研究问题" CONFIG=base   # 真实模型，需凭证
```

当前运行态：**一个前台 `cli.py create` 进程，运行结束退出；Run Bundle 留在本地磁盘。**
单机、单操作者、显式命令运行。

当前代码**没有实现**（不能当现状，各自需独立立项）：

- HTTP / Web API、常驻 worker / job queue、多用户认证与租户隔离、多进程调度与
  owner 接管、外部数据库/对象存储、部署镜像（systemd/Compose/Helm）、备份与
  跨机器恢复、滚动升级协调；
- skill 强制加载（当前 `available_skills=None`，实际加载需证据判断）；
- 真实研究质量的自动化统计评估（引文真实性、充分性）；
- evidence 自动物化（搜索结果已物化到 `diagnostics/searches/` 可直读复核，但仍不自动进入 evidence/ 准入）。

对外发布前需要补齐的服务化决策清单见
[架构计划](../../_backlog/_done/_closed_plans/2026-10-05-runtime-test-interaction-architecture.md)（已验收关闭，Phase 5 裁决记录在案）。

## 10. 质量车道怎么选

不要每次从真实端到端开始。按问题选最小车道，再扩大：

```text
规则 / 状态 / 文件 / 准入问题      → make verify
DeerFlow 接线 / 事件 / checkpoint → make smoke
真实模型 / skill / 外部工具质量    → base 真实梯（显式 opt-in）
发布布局 / 新机器冷启动           → 冷启动 lane
代码结构 / 依赖方向 / 发布面       → governance checker
```

每条 lane 证明什么、不证明什么，三种质量对象（研究引擎 / Harness 控制 / 发布）
的划分 → [车道策略](testing-and-evaluation.md) 与 [测试资产地图](../tests/README.md)。

## 同轮维护

新增/搬迁/删除对象时更新 owning code/test、§7 路由表与结构 inventory；新增 docs
登记文档 scope 与索引行。地图不能补出未接线能力，也不复制
state/checkpoint/ledger 成第二事实源。AGENTS 保持短触发路由；操作旅程见
[playbook](playbook/run-research.md)。
