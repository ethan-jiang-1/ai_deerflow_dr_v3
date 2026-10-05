# 运行态总图：Deep Research、发布与质量保障

> 这份文档回答一个核心问题：从提出研究问题到得到结果，究竟是谁在驱动什么。
>
> 文档刻意区分三种事实：
>
> - **当前已实现**：代码和现有测试已经证明的行为。
> - **开发 / 测试用途**：帮助修改和验证系统的逻辑，不属于产品运行主链。
> - **发布前待补齐**：当前仓库还没有实现，不能把它当成现状。
>
> 运行时事实的最终权威仍然是代码、配置、测试和 OpenSpec；本文是给人和 coding agent 使用的导航图，不是第二套业务规则。

直接找对象：[Repo 目录地图](repository-map.md) · [研究过程 / skill / 绑定 / 证据](research-process.md) · [测试资产地图](../tests/README.md)。

## 1. 先给结论

当前项目不是一条写死的“搜索 → 分析 → 写报告”静态流水线，也不是已经部署好的 Web 服务。

它目前是：

```text
用户 / 操作者
    │
    │ 当前入口：cli.py → runtime/interaction/cli.py
    ▼
Harness 运行底座
    ├─ 创建和管理 Run Bundle
    ├─ 启动一次 DeerFlow 研究运行
    ├─ 记录 journal / checkpoint / diagnostics
    ├─ 处理取消、崩溃转移、有限澄清续答
    └─ 对最终报告做确定性准入
    │
    ▼
DeerFlow 宿主运行时
    ├─ lead agent
    ├─ deep-research skill 方法论
    ├─ web_search / web_fetch 等工具
    ├─ 按需派生 subagent
    └─ LangGraph / checkpointer / middleware
    │
    ▼
模型与外部工具
    ├─ fixture：脚本模型和假搜索，不需要凭证
    └─ base：真实模型和真实 Web 工具，需要凭证
```

**最重要的一句话：**研究内容的动态过程由 DeerFlow 原生 agent 运行时驱动；本项目的 Harness 不决定每一步搜什么，而是负责把一次研究运行装进可追踪、可恢复判断、可检查、可接纳的 Run Bundle 里。

## 2. 三层职责

### 2.1 产品代码：`deep_research_harness/`

这是我们自己的应用，今后产品行为主要在这里演进。

| 层 | 负责什么 | 主要位置 |
| --- | --- | --- |
| `domain` | 纯业务事实和规则：状态、生命周期、路径、journal 词汇 | `src/deerflow_deep_research/domain/` |
| `engine` | 确定性裁决：validator、admission gate、质量机器 | `src/deerflow_deep_research/engine/` |
| `runtime` | 把规则接到文件、SQLite、DeerFlow 和运行过程 | `src/deerflow_deep_research/runtime/` |
| `agents` | 预留给 Harness 自己拥有的 bounded model role；当前基本为空 | `src/deerflow_deep_research/agents/` |
| 交互入口 | 稳定 launcher 转交六动词解析/输出；不承载状态规则 | `cli.py` → `runtime/interaction/cli.py` |
| 运行装配 | 配置、pin、Bundle 查找、前台 client/saver 装配 | `runtime/entry.py` |
| `config/` | DeerFlow 运行配置：模型、工具、递归上限、checkpoint 策略 | `deep_research_harness/config/` |

`deerflow/` 是随行的上游框架，不是我们要在日常需求里修改的产品代码。它提供真正的 agent、skill、工具和运行时。

### 2.2 DeerFlow：研究认知引擎

DeerFlow v2.1.0 没有一张固定的 Deep Research StateGraph。它把研究能力组合成：

1. [deep-research skill 本地原文快照](skills/deep-research/SKILL.md)：提示词形式的方法论，规定广度探索、深入追查、多样性验证和综合检查；[本地阅读入口](skills/deep-research/README.md) 说明来源与调整边界，运行时仍使用框架加载。
2. lead agent：按需加载可用 skill，在运行时决定下一步；当前 binding 不强制每次加载 deep-research。
3. subagent 委派系统：lead agent 可以按需用 `task` 派生研究子代理。
4. 宿主工具和运行时：搜索、抓取、沙箱、middleware、LangGraph、checkpoint。

因此，下面这些动作**不是由 Harness 中一个固定的 `workflow.py` 决定的**：

- 搜索几个问题；
- 先搜哪个角度；
- 何时抓全文；
- 是否派生 subagent；
- subagent 各自研究什么；
- 何时认为内容已经足够并开始写报告。

这些行为由 skill、模型判断、工具可用性、上下文和框架治理参数共同产生。模型可以提出候选动作，但不能越过 Harness 的确定性准入规则直接把产物当成已接受事实。

### 2.3 Coding agent：开发者，不是产品运行角色

本仓库里的 Codex、Claude Code 等 coding agent 是**开发过程的参与者**，不是用户提交研究问题之后的产品运行节点。

Coding agent 负责：

- 读取 `AGENTS.md`、`COMMANDS.md`、运行态文档和 owning code；
- 修改产品代码、配置、测试和文档；
- 按质量车道验证修改；
- 在 OpenSpec / backlog 规则下提交变更。

Coding agent 不负责：

- 代替 lead agent 做每次研究搜索；
- 决定发布后的业务 workflow；
- 把一段提示词当成运行时权限；
- 直接修改 `deerflow/` 上游框架来“修好”产品行为。

当前 `agents/` 目录为空，这意味着 Harness 还没有自有的研究 agent role 合同。现在的研究 agent 主要属于 DeerFlow。今后如果我们要拥有“证据审查 agent”“报告编辑 agent”等产品角色，应先明确它们的职责、输入、输出、不能决定什么，再放进 `agents/`，不能只加一段 prompt 就算完成架构扩展。

## 3. 一次研究真正怎么跑

以下是当前 `cli.py create` 的真实路径，不是计划中的理想流程。

```text
1. 读取问题和 --config
   │  runtime/interaction/cli.py
   ▼
2. 读取 DeerFlow git pin
   │  runtime/entry.py::read_pin()
   ▼
3. 创建临时目录并原子发布 Run Bundle
   │  runtime/bundle_actions.py::start
   │  domain/state_machine.py::rule_start
   ▼
4. 打开该 Bundle 的 SQLite checkpointer
   │  runtime/client.py::bundle_checkpointer
   ▼
5. 解析 checked-in 配置，构造 DeerFlowClient
   │  runtime/entry.py::run_foreground → runtime/client.py::build_client
   │  config/base.yaml 或 config/fixture.yaml
   ▼
6. 以一个 thread 启动 DeerFlow agent stream
   │  runtime/client.py::make_stream_fn
   ▼
7. DeerFlow 内部循环
   │  lead agent + deep-research skill + tools + subagents
   │  这一段是动态的，不是 Harness 写死的节点图
   ▼
8. Harness 消费事件
   │  runtime/run_engine.py::_consume_turn
   ├─ 记录 model/tool/subagent 事件到 diagnostics/journal.jsonl
   ├─ 从最终 values snapshot 判断当前 turn 的完整结果
   ├─ 识别未回答的 ask_clarification
   └─ 观察取消请求、模型 fallback、stop reason
   ▼
9. 需要时有限自动续答
   │  默认最多 2 次，不进入新的状态
   ▼
10. 得到终态
    ├─ completed
    ├─ cancelled
    └─ failed-resume
   │  domain/state_machine.py::rule_run_terminal
   ▼
11. 完成时提交 final_report
    │  runtime/admission.py::submit_artifact
    ├─ engine/validator.py 先裁决
    ├─ 通过后写入 final/report-genN.md
    ├─ 写入 evidence/submissions.jsonl 哈希链
    └─ 记录 validation journal
```

### Run Bundle 保存什么

每个运行在 `deep_research_harness/scopes/d_YYYYMMDD/<bundle-id>/` 下拥有独立目录：

```text
state.json                         # 当前运行状态的唯一权威
request/problem.txt                # 原始问题
request/refine-N.txt               # 后续 generation 的方向
checkpoint.sqlite                  # DeerFlow / LangGraph 的运行上下文
work/                              # 工作区
evidence/                          # 通过准入的证据和 submissions 哈希链
final/report-genN.md               # 通过准入的最终报告
diagnostics/journal.jsonl          # 事件时间线
diagnostics/assembly-snapshot.json # 装配快照
```

`scopes/` 被 gitignore，属于运行数据，不应提交到代码仓库。删除一个 Bundle 是永久删除，不会让 Harness 停止，也不会自动恢复该运行。

### 当前几个容易误解的动作

- `watch` 只是读取 journal，直到看到 terminal 事件；它不驱动研究。
- `status` 读取状态并检查 owner PID；发现 active 但 owner 已死时，会转为 `failed-resume`。
- `cancel` 只记录取消请求；正在运行的 pump 在下一次合适的检查点观察它。
- 当前 `refine` 命令只创建下一代、写入方向并置为 active；它本身没有在 `cmd_refine` 中继续调用 `run_engine`。因此“generation+1 started”不等于“generation+1 已经跑完”。
- `inspect` 是诊断投影：读 journal、准入统计和 assembly snapshot，不是第二个事实源。

## 4. 配置如何改变运行

### `fixture` 梯：发布自证和开发回归

`config/fixture.yaml` 把模型和搜索工具指向 Harness 自己的 fixture：

- `ScriptedChatModel` 按脚本返回固定消息；
- `fake_web_search` 返回固定结果；
- 使用真实 DeerFlow client、middleware、agent loop 和 SQLite checkpointer；
- 不需要 API key，也不代表真实研究质量。

它回答的是：“发布面自足吗？接线、状态、事件和报告落盘能否工作？”

### `base` 梯：真实研究运行

`config/base.yaml` 使用真实模型和真实 Web 工具：

- 模型当前是 `deepseek-chat`；
- 凭证通过 `$DEEPSEEK_API_KEY` 等环境变量提供；
- `web_search` 和 `web_fetch` 会产生真实外部调用；
- 运行慢、消耗费用、结果不确定，不能放进默认单元门禁。

它回答的是：“在当前模型、skill、工具和配置下，一次真实研究是否能完成，以及实际质量如何？”一次成功不能证明统计意义上的稳定质量。

## 5. 今后发布到底怎么发布

### 5.1 当前已经确定的发布形态

当前发布不是 wheel，也不是已经完成的 Docker / Web / Kubernetes 服务发布。现有可验证的发布面是：

```text
一个递归 clone 的 Git checkout
├── deep_research_harness/   # 我们的应用
└── deerflow/                # 锁定 commit 的上游 submodule
```

两者必须保持兄弟目录关系，因为 `pyproject.toml` 通过相对路径依赖 `../deerflow/backend/packages/harness`。

随行条件：

- Git，并且初始化 submodule；
- Python 3.12+；
- `uv`；
- 首次 `uv sync` 所需的网络或已准备好的缓存；
- real 梯所需的环境变量 / `.env`，由部署使用者在机器上提供；
- 运行数据目录 `deep_research_harness/scopes/` 的持久磁盘空间。

不属于发布运行时：

- `openspec`：开发治理；
- `_backlog/`：计划、复盘和任务账本；
- `.agents/`：会话私产；
- `.venv/` 和 `.uv-cache/`：可再生环境 / 缓存。

### 5.2 当前发布后的启动方式

冷启动和当前人工运行方式是：

```bash
git clone --recursive <repo-url>
cd <checkout>/deep_research_harness
uv sync
make verify
make create PROBLEM="研究问题"                 # 默认 fixture，零凭证
make create PROBLEM="研究问题" CONFIG=base     # 真实模型，需要凭证
```

这意味着当前运行态是：**一个前台 `cli.py create` 进程，直接消费问题，运行结束后退出；Run Bundle 留在本地磁盘。**

当前代码没有实现下面这些发布能力：

- 面向用户的 HTTP / Web API；
- 常驻 worker / job queue；
- 多用户认证和租户隔离；
- 多进程任务调度和 owner 接管；
- 外部数据库或对象存储；
- 发布镜像、systemd、Docker Compose 或 Helm 的本应用部署包；
- 数据备份、跨机器恢复和 schema migration；
- 滚动升级期间的运行协调。

所以现在可以说“发布一个可冷启动运行的源码应用”，不能说“已经发布成一个可供多人访问的在线产品”。

### 5.3 未来真正对外发布前需要补齐什么

这是待做项，不是当前实现：

1. **服务入口**：决定 CLI 是否只是运维入口，再增加 HTTP / host adapter；定义提交、查询、取消、下载报告的跨进程契约。
2. **任务执行模型**：前台进程改为可管理的 worker，明确 active Bundle 的 owner、重启接管、重复提交和并发规则。
3. **持久化和备份**：决定 `scopes/` 是否继续作为生产存储，或者迁移到数据库 / 对象存储；定义备份、恢复和删除语义。
4. **凭证和配置**：把 `$VAR`、secret 管理、模型和工具配置纳入发布环境，而不是依赖开发者工作区的 `.env`。
5. **发布工件**：在源码两件套之外，选择并验证 Docker image、安装包或平台部署工件；当前 wheel 只包含 Python package，不包含 `cli.py`、`config/` 和发布所需布局，不能直接当完整产品包。
6. **运行观测**：把 journal、错误、耗时、token、外部调用失败和终态统计接到正式观测系统。
7. **升级与恢复演练**：为 `state.json`、checkpoint、ledger 和 DeerFlow pin 定义兼容策略，并做冷启动、升级中断、恢复和回滚测试。

在这些决定完成前，最稳妥的使用方式是单机、单操作者、显式命令运行；不要把当前 CLI 直接当成生产多用户服务。

## 6. 质量保障：每一层究竟证明什么

质量车道不是越多越好，关键是每条车道对应运行链上的一个事实。

| 车道 | 命令 | 它证明什么 | 它明确不证明什么 |
| --- | --- | --- | --- |
| 纯单元门禁 | `make verify` | domain 状态规则、Bundle 落盘、准入、journal、配置解析、命令面和负例控制 | 不证明真实模型、真实网络、跨进程运行 |
| 集成 smoke | `make smoke` | 真实 DeerFlow client 接线、SQLite checkpoint、多轮事件、澄清续答、assembly snapshot、CLI 旅程 | 不证明模型研究质量；fixture 模型是脚本化的 |
| 真实梯 | `make create PROBLEM="..." CONFIG=base` | 当前模型、skill、工具和外部 API 的一次真实行为 | 慢、有费用、不确定；一次通过不代表稳定质量 |
| 发布冷启动 | `git clone --recursive` → `uv sync` → `make verify` → fixture `make create` | 发布面没有偷偷依赖开发工作区，随行代码和相对布局完整 | 不证明真实 API 质量、多用户服务能力 |
| 仓库治理门禁 | 从 [根导航](../../AGENTS.md) 进入治理命令 | 结构、依赖方向、spec、指导和发布面声明没有漂移 | 不证明产品运行时成功 |

### 质量的三种对象

1. **研究引擎质量**：研究角度是否充分、事实是否有来源、报告是否有洞察。这主要由真实梯、评审和未来的 live trace evaluation 负责；当前还没有自动化统计评估。
2. **Harness 控制质量**：状态是否诚实、失败是否可见、证据是否经过 validator、ledger 是否可验证、运行是否可检查。这由 unit + smoke 负责，且大部分可离线确定性验证。
3. **发布质量**：全新环境是否能按发布说明跑起来。这由冷启动 lane 负责；它证明“能启动和完成 fixture”，不冒充研究质量验收。

所以驱动项目时，不应每次都从真实端到端开始。先根据问题选择最小车道：

```text
规则 / 状态 / 文件 / 准入问题  → make verify
DeerFlow 接线 / 事件 / checkpoint → make smoke
真实模型 / skill / 外部工具质量   → base 真实梯
发布布局 / 新机器启动             → 冷启动 lane
代码结构 / 依赖方向 / 发布面       → governance checker
```

## 7. 今后改动应该找哪里

| 你想改变的东西 | 先看哪里 | 不要先改哪里 |
| --- | --- | --- |
| Run Bundle 状态、取消、refine、崩溃转移 | `domain/state_machine.py` + `runtime/bundle_actions.py` | 不要从 CLI 文案开始改规则 |
| 一次 run 如何消费 stream、识别澄清、结束 | `runtime/run_engine.py` | 不要把终态判断塞进 `cli.py` |
| DeerFlow 如何被构造、模型和工具如何接入 | `runtime/client.py` + `config/*.yaml` | 不要复制一套 agent loop |
| Deep Research 的方法论和研究步骤 | 随行 DeerFlow 的 `deep-research` skill；若要产品自有角色，再走 `agents/` 合同 | 不要把 skill 当成硬权限或状态机 |
| 哪些产物可以进入 Bundle | `engine/validator.py` + `runtime/admission.py` | 不要由模型输出直接写入 final/evidence |
| 准入事实是否满足阶段需求 | `engine/gate.py` | 不要用报告文本猜测是否通过 |
| 运行数据和历史时间线 | `runtime/bundle_state.py`、`runtime/journal.py`、`runtime/ledger.py` | 不要在文档里另造一份状态 |
| 开发者如何修改和验证 | `AGENTS.md`、`COMMANDS.md`、本文件、测试和 OpenSpec | 不要依赖 coding agent 的会话记忆 |

## 8. 目前最需要明确的结构问题

当前结构的主方向是对的：研究认知交给 DeerFlow，确定性控制留在 Harness；但有三处容易让驱动者误使力：

1. **产品入口需要保持清晰**：[应用 README](../README.md) 提供短控制地图，本文件展开运行/发布/质量事实；改动入口或目录时同步维护。
2. **“workflow”这个词容易混淆**：当前至少有三种东西：DeerFlow 动态研究过程、Harness Run Bundle 生命周期、开发 / 测试质量车道。今后文档中应明确写出是哪一个，避免把 `make smoke` 当产品 workflow。
3. **发布态仍是单机 CLI，不是服务态**：如果产品目标是多人在线使用，必须单独立项服务入口、worker、持久化、认证、升级和恢复；不能靠继续增加 CLI 命令自然长成生产服务。

需要另行决策的行为是 `refine` 的执行方式：CLI help、命令菜单和 playbook 已如实描述为“进入下一代但不自动运行”；`runtime/interaction/cli.py::cmd_refine` 只创建下一代并返回 active，没有调用 `run_engine`。若希望它执行研究，需要独立产品语义决定：

- 若未来定义为“提交下一代任务”，需要定义后续 worker 取任务的合同；
- 若定义是“立即前台重跑”，应补上运行调用并为失败、取消和并发定义契约。

在这个决定明确之前，不应把 `refine` 当作已经完成的自动重跑能力。
