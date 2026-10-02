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
  [`_backlog/_reference/deerflow-native-deep-research.md`](_backlog/_reference/deerflow-native-deep-research.md)。

DeerFlow 是宿主运行时，**不 import 本包**；触达方式（反射工具 / controller skill / 或更薄的接线）由首个 change 定义。

> **当前状态：骨架。** 目录结构、治理机器、账本 ritual 已就位；`openspec/specs/` 为空，应用代码为壳。
> 一切实现从下一个 change 开始——第一站：[`_backlog/plans/2026-10-02-digest-deerflow-native-deep-research.md`](_backlog/plans/2026-10-02-digest-deerflow-native-deep-research.md)。

## 布局

```
deep_research_harness/    ★ 你的应用（deep research runtime，基于 deerflow 的 API 构建）
deerflow/                 被 leverage 的框架（submodule 锁 commit `ceebf97f`，ethan 分支，= 上游 v2.1.0；只读）
openspec/                 设计规格（openspec CLI 管理；specs 从零开始，changes/ 为空）
_backlog/                 任务账本（bugs / plans / todos + _done 归档 + _reference 分析）
.agents/skills/           openspec 技能（Codex 通用入口，项目自有）
（grillme 技能集由全局 ~/.claude/skills、~/.agents/skills 提供）
```

其他根目录居民：

- `config.yaml`、`.env` — 宿主运行时配置与凭证（均 gitignored；按 DeerFlow 宿主约定从模板/环境准备）
- `profiles/` — 本地运行 profile（暂未注册；权威将来落在 harness 的 local-operations 文档）
- `CONTEXT.md`、`CONTEXT-MAP.md` — 三个 bounded context 的词汇边界（Host / Product / Governance）

## 快速开始

```bash
cd deep_research_harness
make install              # 骨架期占位（uv sync）
make verify               # 骨架期占位（无测试，响亮提示后通过）
```

## 给 Coding Agent

见 [AGENTS.md](AGENTS.md)——重点是：应用是主角，框架只 leverage 不改；骨架期先读第一个 plan 再动手。

## 备注

- `deerflow/` submodule 需 `git clone --recurse-submodules` 或 `git submodule update --init` 才完整。
- 框架运行时基座：submodule 锁在 commit `ceebf97f`（ethan 分支，= 上游 v2.1.0，2026-09-24 发布）。
  声明锁与契约测试锚（v2 的 `CURRENT_DEERFLOW_PIN` 模式）将在首个治理 change 中建立。
