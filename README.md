# ai_deerflow_dr_v3

一个跑在 [DeerFlow](https://github.com/bytedance/deer-flow) 之上的 **Deep Research Harness**（v3，重写版）。
它不是"问一句、拿报告"的单管道 deep research 应用，而是一套 deep research 的**运行 / 控制底座**：
把每一次研究变成一个独立、可检查、可单独删除的 **Run Bundle**，并在有界 LLM 认知之外做确定性准入
（validator / evidence ledger / gate）。

与 v2（前代仓 `ai_deerflow_deep_research_v2`）的分野：

- **思想与结构继承**：Run Bundle 是持久真相、显式组成（`all_real` / `fixture` / `mixed`）、
  "模型提议、代码裁决"、OpenSpec spec-driven 开发、`_backlog` 任务账本、DeerFlow 只读边界——全部延续。
- **实现路线反转**：v2 逐节点手搓研究图；v3 **消化并借力 DeerFlow v2.1.0 原生的 Deep Research
  能力**——lead agent + `deep-research` skill（四阶段研究方法论）+ subagent 委派系统，harness 退守
  "运行底座 + 确定性控制边界"。历史分析另存账本参考。

## 一屏地图（先看这里）

### 目录：什么住在哪，谁拥有它

```
ai_deerflow_dr_v3/
|-- deep_research_harness/   ★ 你的应用（本仓几乎全部工作在这里）
|   |-- cli.py                  唯一启动入口（转交 runtime/interaction/cli.py）
|   |-- src/…/domain/           纯规则：状态机、路径合同、journal 词汇
|   |-- src/…/engine/           确定性裁决：validator、admission gate
|   |-- src/…/agents/           预留层（当前为空）
|   |-- src/…/runtime/          装配、DeerFlow 绑定、run loop、持久化、CLI 交互
|   |   `-- scripted/           脚本梯 providers（fixture 梯用的假模型/假搜索）
|   |-- tests/                  unit / contract / integration + fixtures（样本）
|   |-- docs/                   全部地图（control-map 是总图；playbook 是操作旅程）
|   |-- config/                 base（真模型）/ fixture（零凭证）两梯配置
|   `-- tools/                  显式录制等开发操作（不是测试）
|-- runs/                    本地 Run Bundle 数据（每次研究的状态/证据/报告；gitignored，
|                            应用子树之外；DEEP_RESEARCH_RUNS_ROOT 可覆盖）
|-- deerflow/                被 leverage 的框架（submodule 锁 ceebf97f = ethan-v2.1.0 的前一提交；只读不改）
|-- openspec/                设计规格、准入与治理 checker（开发治理，不参与运行）
|-- _backlog/                任务账本（issues / bugs + 归档）
`-- .agents/skills/          openspec 技能（用户保留区）
```

### 一次研究怎么串起来（入口 → 报告）

```
python3 cli.py create "问题" --config fixture        ← deep_research_harness/ 下执行
  -> runtime/interaction/cli.py      参数、交互、直播输出
  -> runtime/bundle/bundle_actions   创建 Run Bundle（runs/d_日期/<bundle-id>/）
  -> runtime/assembly.run_foreground 配置、client、SQLite checkpointer 装配
  -> DeerFlow lead agent             框架的 agent loop（按需加载 skill、搜索、委派 subagent）
  -> runtime/pump                    消费事件流、有限续答、取消、终态
  -> engine/validator + admission    最终回答确定性准入
  -> runs/…/final/report-genN.md     通过准入的报告落在 Bundle 内
```

> 两种 loop 并存且职责不重叠：**DeerFlow agent loop** 决定搜什么、何时收束（研究认知）；
> **Harness run loop**（pump）决定状态、终态与准入（运行控制）。详见[控制地图](deep_research_harness/docs/control-map.md)。

### 三个 lane 的命令（都在 deep_research_harness/ 下执行）

```bash
# 跑研究（运行态）
make create PROBLEM="研究问题"              # fixture 梯，零凭证；CONFIG=base 用真模型（需凭证）
python3 cli.py status|watch|inspect <bundle_id>   # 观察：状态 / journal 直播 / 时间线证据
python3 cli.py refine <bundle_id> "方向"    # 下一代研究；cancel 记录取消请求

# 测试与门禁
make verify                                 # 离线单元门禁（stdlib，无依赖，秒级）
make smoke                                  # 集成 lane：脚本模型 + 真框架（需先 uv sync）

# 调试 / 录制
make record-stream PROBLEM="…" CONFIG=base  # 显式录制真实 API 事件流（供回放测试）
```

## 深入阅读（按问题选）

- [应用 README](deep_research_harness/README.md)：应用级阅读地图与"改一处先证明哪一层"
- [控制地图](deep_research_harness/docs/control-map.md)：唯一总图——主链、两种 loop、owner 路由
- [研究过程地图](deep_research_harness/docs/research-process.md)：skill 原文、lead agent 绑定、工具与运行证据
- [Run Bundle 地图](deep_research_harness/docs/run-bundle.md)：持久化合同、artifact 权属
- [测试资产地图](deep_research_harness/tests/README.md)：每份测试证明什么、最小红绿路径
- [操作旅程](deep_research_harness/docs/playbook/run-research.md)：跑研究的步骤、完成判据与坑

## 给 Coding Agent

> **当前状态：已实现核心。** specs 主干 13 个能力落地、69 个 changes 归档
> （实际清单见 `openspec/specs/` 与 `openspec/changes/archive/`）。

见 [AGENTS.md](AGENTS.md)——重点是：应用是主角，框架只 leverage 不改；当前该做什么看
[`_backlog/README.md`](_backlog/README.md) 的知识地图。

## 备注

- `deerflow/` submodule 需 `git clone --recurse-submodules` 或 `git submodule update --init` 才完整。
- 框架运行时基座：submodule 锁在 commit `ceebf97f`（ethan digest 分支，ethan-v2.1.0 tag 的前一提交而非 tag 本身；上游 v2.1.0 于 2026-09-24 发布）。
  声明锁已在[结构 registry](openspec/governance/project-structure.toml)。
- 其他根目录居民：`config.yaml`、`.env`（按需准备的宿主配置与凭证，gitignored）、
  `profiles/`（本地运行 profile）、`CONTEXT.md` / `CONTEXT-MAP.md`（词汇边界）。
