# Plan: Agent-friendly Repo 持续整理

> 类型: 分析 / 维护计划 | 更新: 2026-10-06（关闭：CLS-015）
> 关闭原因: 触发表已由 `deep_research_harness/docs/README.md` 的"地图维护触发条件"节吸收（活跃队列不留常驻卡）；待裁决项均在 CLS-014 归档记录与 known-limitations 挂号。本文件保留为历史记录。

## 背景 / 现状

操作者和新 coding agent 不应依赖会话记忆，或先翻归档分析才能找到 Deep Research 主干、代码 owner 和测试资产。
当前导航事实暴露在（2026-10-06 起，旧 repository-map / runtime-map / runtime-architecture 已合并，勿再引用）：

- [根 README 一屏地图](../../README.md)：目录表（含 `runs/`）、入口链、run/debug/test 三 lane 命令——驾驶者第一入口。
- [控制地图](../../deep_research_harness/docs/control-map.md)：唯一总图；主链、两种 loop、owner 路由、目录树。
- [研究过程地图](../../deep_research_harness/docs/research-process.md)：上游 skill 原文、应用绑定、配置、snapshot/journal/checkpoint 与限制。
- [测试资产地图](../../deep_research_harness/tests/README.md)：逐文件被测接口、真实部分/替身、lane、样本来源和最小红绿命令。
- [Run Bundle 地图](../../deep_research_harness/docs/run-bundle.md)：持久化合同与 artifact 权属；运行数据在仓库根 `runs/`。

结构整理由 [clarify-application-surfaces](../../openspec/changes/archive/2026-10-05-clarify-application-surfaces/proposal.md) 收敛 interaction、entry、contract 和 tools；运行态存储迁出应用子树（`scopes/` → 仓库根 `runs/`）、`runtime/fixtures` → `runtime/scripted` 改名、playbook 并入 `docs/playbook/`、根 README 一屏地图由 [relocate-runs-and-clarify-structure](../../openspec/changes/archive/2026-10-06-relocate-runs-and-clarify-structure/proposal.md) 落地。

## 决策 / 方案

Agent friendliness 是导航的首要验收：任务触发路由 -> owning code/test -> 可执行命令 -> 可观察结果与不覆盖面。
常驻 [应用 AGENTS](../../deep_research_harness/AGENTS.md) 只留短路由，细节按需读取；保持既有字数预算。

持续维护触发条件：

| 触发 | 同轮回写 |
| --- | --- |
| 新增/搬迁/删除源模块（含 runtime 子目录、scripted providers） | 根 README 目录表 + 控制地图的目录树与 owner 路由 |
| 运行数据根变化（`runs/` 位置、`DEEP_RESEARCH_RUNS_ROOT` 语义） | 根 README、控制地图、Run Bundle 地图的路径合同行 |
| 修改 skill 使用、模型/工具绑定、stream/报告路径 | 研究过程地图；区分声明能力与实际发生证据 |
| 新增/删除测试或改变收集方式 | 测试资产地图、车道声明与实际 runner 一致；collection guard 同步 |
| 新录制/更新 fixture | 消费者、来源、配置/pin/revision、敏感数据审查与局限 |
| 发布形态改变 | 控制地图、命令菜单/playbook；以新鲜执行回执为准 |
| 新增文档 | 文档索引、required paths、doc scope；入口预算不因堆细节上调 |

每次维护的完成判据：涉及的对象都有可点击入口；链接有效；选中测试确实执行而非 skip；相关门禁返回 0；运行事实未被 doc 虚构。

## 风险 / 取舍

- 地图是缓存而不是第二套权威 -> 保持链接到 owning code/test，改变对象时同轮回写。
- 目录迁移可能改变 unittest discovery -> owning change 比较迁移前后测试 ID，并证明 contract 负例被发现、integration 仍排除。
- 研究质量与 Harness 控制容易混淆 -> fixture 只证明合同，真实研究质量仍需显式观测。
- 无期限整理容易扩大范围 -> 维护由具体改动触发，不持续无目标扫描、不擅自实现产品决策。

待另行决策 / owning change（不是本卡暗中修复；Phase 5 已裁决项见主计划归档记录）：

- skill 加载的强制程度，以及研究证据/充分性 gate 的真实接线（已裁决维持现状）。
- 多用户服务、worker、备份/恢复与正式部署面（已裁决维持源码两件套形态）。
- 真实模型回放完整协议与 provenance、live 研究质量评估（未立项）。

## 落地关联

导航与结构整理由 [clarify-application-surfaces](../../openspec/changes/archive/2026-10-05-clarify-application-surfaces/tasks.md) 与 [relocate-runs-and-clarify-structure](../../openspec/changes/archive/2026-10-06-relocate-runs-and-clarify-structure/tasks.md) 记录设计、任务和验证；不引入新运行规则。
后续任何行为、权限、持久化合同或架构守卫变更，仍须独立 OpenSpec change 和人的规范语义裁决；本计划不是 apply 授权。

本卡保留为活跃维护入口；不把未来产品缺口标记为完成。会话自动目标完成只代表本轮交付，不代表持续维护终止。
