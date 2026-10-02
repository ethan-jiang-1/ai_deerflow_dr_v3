# Reference — 外部系统分析资料

> 最后更新: 2026-10-02 | 本目录存放对外部系统的分析、研究笔记、架构参考。
> 这些是**消化材料**——读完、理解完之后，产出 `_backlog/plans/` 里的实际方案。

## 目录

| 条目 | 内容 |
|------|------|
| [deerflow-native-deep-research.md](deerflow-native-deep-research.md) | DeerFlow v2.1.0（submodule 锁 `ceebf97f`）原生 Deep Research 能力盘点：deep-research skill、subagent 委派系统、宿主工具与运行时 |
| [v2-harness-app-shape.md](v2-harness-app-shape.md) | v2 应用骨架全貌（非 Bundle 部分）：五层+resources/tool.py、12 节点静态图、入口面「操作剧场」（两条凭证路线/跑法阶梯/soft-bundle 子命令族/TUI/调试工作台）、runbook 体系、对 v3 的四个推敲议题 |
| [deerflow-cognition-engine.md](deerflow-cognition-engine.md) | DeerFlow 认知引擎与治理参数面：deep-research skill 四阶段方法论全文、CustomSubagentConfig 精确 schema、委派治理参数全表（并发/总数/token 预算两档/超时/一层深度）、lead agent 可配置面、最小配置路径、harness 旋钮清单 |
| [v2-run-bundle-implementation.md](v2-run-bundle-implementation.md) | v2 Run Bundle 真实实现：磁盘形态（7 子树+state.json+graph.sqlite）、事件日志（10 类事件/有界保留/诚实丢弃）、生命周期状态机（5 动作/6 状态/CAS+目录 lease）、确定性验收三件套（纯函数 validator→hash 链 ledger 单一收口→gate kernel）、删除语义三层保证、显式组成（fixture 独立包+adapter 选择）、v2 决策记录与教训、v3 继承/改掉清单 |
| [deerflow-runtime-and-persistence.md](deerflow-runtime-and-persistence.md) | DeerFlow 运行时与持久化面：进程内两真路（DeerFlowClient 嵌入式 vs 自组装 RunManager）+ Gateway REST 全端点表、Internal Auth、持久化三块（checkpointer/RunStore/RunEventStore）、resume 语义（同 thread 新 run/checkpoint 404 fail-closed）、trace 身份（X-Trace-Id/ContextVar）、SSE 事件清单 |
| [deerflow-harness-architecture.md](deerflow-harness-architecture.md) | DeerFlow harness 包架构标本：分层与依赖方向（config 叶→子系统→agents 装配→runtime 宿主）、装配机制（类路径反射+两级工厂+tri-state features）、36 条 middleware 链、extension-api 契约（7 类贡献+语义 placement）、skills/sandbox/tools 机制、双持久化分离、可借鉴 12 模式 vs 8 项复杂度包袱 |

## 与 plans 的关系

```
reference/  →  学习外部系统的设计、机制、取舍
    ↓ 消化
plans/      →  基于学习产出本项目的具体方案
    ↓ 落地
openspec/   →  OpenSpec change 推动实现
```
