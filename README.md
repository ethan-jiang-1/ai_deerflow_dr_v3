# ai_deerflow_dr_v3

一个跑在 [DeerFlow](https://github.com/bytedance/deer-flow) 之上的 **Deep Research Harness**（v3，重写版）。
它不是"问一句、拿报告"的单管道 deep research 应用，而是一套 deep research 的**运行 / 控制底座**：
把每一次研究变成一个独立、可检查、可单独删除的 **Run Bundle**，并在有界 LLM 认知之外做确定性准入
（validator / evidence ledger / gate）。

与 v2（[`ai_deerflow_deep_research_v2`](../ai_deerflow_deep_research_v2/)）的分野：

- **思想与结构继承**：Run Bundle 是持久真相、显式组成（`all_real` / `fixture` / `mixed`）、
  "模型提议、代码裁决"、OpenSpec spec-driven 开发、`_backlog` 任务账本、DeerFlow 只读边界——全部延续。
- **实现路线反转**：v2 逐节点手搓研究图（bootstrap → wave0/1/2 → …）；v3 **消化并借力 DeerFlow v2.1.0
  原生的 Deep Research 能力**——lead agent + `deep-research` skill（四阶段研究方法论）+ subagent 委派
  系统，harness 退守"运行底座 + 确定性控制边界"。能力盘点见
  [应用内研究过程地图](deep_research_harness/docs/research-process.md)；历史分析另存账本参考。

DeerFlow 是宿主运行时，**不 import 本包**；本应用通过 [嵌入式 client binding](deep_research_harness/src/deerflow_deep_research/runtime/client.py) 消费其公开接口。

> **当前状态：已实现核心。** specs 主干 12 个能力落地、40 个 changes 归档（实际清单见 `openspec/specs/` 与 `openspec/changes/`）、六动词 CLI 与单元门禁在跑。
> 边界已定（六裁决，见 [`_backlog/_done/_closed_plans/`](_backlog/_done/_closed_plans/README.md)）；新方向按 [`_backlog/plans/README.md`](_backlog/plans/README.md) 的卡片模板立 plan 入账。

## 布局

```
deep_research_harness/    ★ 你的应用（deep research runtime，基于 deerflow 的 API 构建）
deerflow/                 被 leverage 的框架（submodule 锁 commit `ceebf97f`，ethan 分支，= 上游 v2.1.0；只读）
openspec/                 设计规格（openspec CLI 管理；specs 主干已建立，changes/ 为活跃变更及 archive/）
_backlog/                 任务账本（plans / bugs 两类 + _done 归档 + _reference 分析）
.agents/skills/           openspec 技能（Codex 通用入口，项目自有）
（grillme 技能集由全局 ~/.claude/skills、~/.agents/skills 提供）
```

其他根目录居民：

- `config.yaml`、`.env` — 按需准备的宿主配置与凭证（gitignored，当前不在库内；与实存的 `openspec/config.yaml` 是两物）
- `profiles/` — 本地运行 profile（暂未注册；权威将来落在 harness 的 local-operations 文档）
- `CONTEXT.md`、`CONTEXT-MAP.md` — 三个 bounded context 的词汇边界（Host / Product / Governance）

## 快速开始

```bash
cd deep_research_harness
make install              # 有意 no-op（运行依赖由 uv sync 准备）
make verify               # 单元门禁：stdlib unittest 套件，任一失败非零退出
```

## 从哪里看

先读 [应用控制地图](deep_research_harness/README.md)：入口 → 运行链 → 目录职责 → 最小测试。

- [控制地图](deep_research_harness/docs/control-map.md)：唯一总图——主链、两种 loop、owner 路由、发布形态与未实现清单。
- [研究过程地图](deep_research_harness/docs/research-process.md)：skill 原文、lead agent 绑定、工具与运行证据。
- [测试资产地图](deep_research_harness/tests/README.md)：每份测试证明什么、样本来源与最小红绿路径。
- [Run Bundle 地图](deep_research_harness/docs/run-bundle.md)：持久化合同、artifact 权属与终态/交付/质量的区分。

## 给 Coding Agent

见 [AGENTS.md](AGENTS.md)——重点是：应用是主角，框架只 leverage 不改；当前该做什么看 [`_backlog/README.md`](_backlog/README.md) 的知识地图。

## 备注

- `deerflow/` submodule 需 `git clone --recurse-submodules` 或 `git submodule update --init` 才完整。
- 框架运行时基座：submodule 锁在 commit `ceebf97f`（ethan 分支，= 上游 v2.1.0，2026-09-24 发布）。
  声明锁已在 [结构 registry](openspec/governance/project-structure.toml)，接口证据见 [测试资产地图](deep_research_harness/tests/README.md)。
