# Research — 外部系统调研与分析语料

> 最后更新: 2026-10-09（adopt-issue-ledger-governance 路径同步 + 驾驭者更名 `_reference/`→`_research/`，角色不变：长寿命留存语料，非随卡迁移证据区） | 本目录存放对外部系统的分析、研究笔记、架构参考。
> 这些是**消化材料**——读完、理解完之后，产出 `_backlog/issues/` 里的实际方案。

## 目录

| 条目 | 内容 |
|------|------|
| [deerflow-native-deep-research.md](deerflow/deerflow-native-deep-research.md) | DeerFlow v2.1.0（submodule 锁 `ceebf97f`）原生 Deep Research 能力盘点：deep-research skill、subagent 委派系统、宿主工具与运行时 |
| [v2-harness-app-shape.md](v2/v2-harness-app-shape.md) | v2 应用骨架全貌（非 Bundle 部分）：五层+resources/tool.py、12 节点静态图、入口面「操作剧场」（两条凭证路线/跑法阶梯/soft-bundle 子命令族/TUI/调试工作台）、runbook 体系、对 v3 的四个推敲议题 |
| [deerflow-cognition-engine.md](deerflow/deerflow-cognition-engine.md) | DeerFlow 认知引擎与治理参数面：deep-research skill 四阶段方法论全文、CustomSubagentConfig 精确 schema、委派治理参数全表（并发/总数/token 预算两档/超时/一层深度）、lead agent 可配置面、最小配置路径、harness 旋钮清单 |
| [v2-run-bundle-implementation.md](v2/v2-run-bundle-implementation.md) | v2 Run Bundle 真实实现：磁盘形态（7 子树+state.json+graph.sqlite）、事件日志（10 类事件/有界保留/诚实丢弃）、生命周期状态机（5 动作/6 状态/CAS+目录 lease）、确定性验收三件套（纯函数 validator→hash 链 ledger 单一收口→gate kernel）、删除语义三层保证、显式组成（fixture 独立包+adapter 选择）、v2 决策记录与教训、v3 继承/改掉清单 |
| [deerflow-runtime-and-persistence.md](deerflow/deerflow-runtime-and-persistence.md) | DeerFlow 运行时与持久化面：进程内两真路（DeerFlowClient 嵌入式 vs 自组装 RunManager）+ Gateway REST 全端点表、Internal Auth、持久化三块（checkpointer/RunStore/RunEventStore）、resume 语义（同 thread 新 run/checkpoint 404 fail-closed）、trace 身份（X-Trace-Id/ContextVar）、SSE 事件清单 |
| [deerflow-harness-architecture.md](deerflow/deerflow-harness-architecture.md) | DeerFlow harness 包架构标本：分层与依赖方向（config 叶→子系统→agents 装配→runtime 宿主）、装配机制（类路径反射+两级工厂+tri-state features）、36 条 middleware 链、extension-api 契约（7 类贡献+语义 placement）、skills/sandbox/tools 机制、双持久化分离、可借鉴 12 模式 vs 8 项复杂度包袱 |
| [deerflow-application-corpus/](deerflow-application-corpus/README.md) | **DeerFlow 应用开发语料**（2026-10-08 原样复制，38 文件）：独立应用仓怎样用 DeerFlow 原生机制组织意图/证据/交付——应用开发模型、SDLC 参考、开发 Harness 三卷 + `_coverage` 维护层。出处 `/Users/bowhead/deer-flow/_deerflow_application_agent_ready_development/`，钉定上游 `v2.1.0`（`345f08be`）；复制时 gitlink `ceebf97f` 为其祖先（digest 分支 `ethan-v2.1.0~1`），`node verify.mjs`（Node 22）自检通过。**重审触发**：gitlink re-pin 或上游新 release 时，走语料 `_coverage/00-corpus-maintenance.md` 的触发路径逐条复核在案论断 |

## 目录组织（2026-10-04 归类）

- `deerflow/` — DeerFlow 机制分析（认知引擎 / harness 架构 / 原生能力 / 运行时与持久化）
- `v2/` — v2 应用形态分析（harness 全貌 / Run Bundle 实现）
- `test-strategy/` — DeerFlow 自测体系消化（10 篇，v3 测试战略的采纳底本）
- `deerflow-application-corpus/` — DeerFlow 应用开发语料（上游 v2.1.0 钉定的三卷 19 页 + 维护层 + verify 脚本，逐字复制不动内容）

## 与 issues 的关系

```
_research/  →  学习外部系统的设计、机制、取舍
    ↓ 消化
issues/     →  基于学习产出本项目的具体方案
    ↓ 落地
openspec/   →  OpenSpec change 推动实现
```
