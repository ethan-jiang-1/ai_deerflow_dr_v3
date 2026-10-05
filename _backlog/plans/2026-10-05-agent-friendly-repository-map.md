# Plan: Agent-friendly Repo 持续整理

> 类型: 分析 / 维护计划 | 更新: 2026-10-05
> 当前阶段: 导航已落地；用户已授权继续完成目录与入口整理，实施由 clarify-application-surfaces 承接。

## 背景 / 现状

操作者和新 coding agent 不应依赖会话记忆，或先翻归档分析才能找到 Deep Research 主干、代码 owner 和测试资产。
本轮将现有事实暴露在应用内：

- [Repo 地图](../../deep_research_harness/docs/repository-map.md)：目录对象、代码 owner、首次阅读路径。
- [研究过程地图](../../deep_research_harness/docs/research-process.md)：上游 skill 原文、应用绑定、配置、snapshot/journal/checkpoint 与限制。
- [测试资产地图](../../deep_research_harness/tests/README.md)：逐文件被测接口、真实部分/替身、lane、样本来源和最小红绿命令。
- [运行态总图](../../deep_research_harness/docs/runtime-map.md)：运行、发布、质量三种不同问题。

首轮仅补导航。后续用户要求地图与物理组织都完成，由 [clarify-application-surfaces](../../openspec/changes/archive/2026-10-05-clarify-application-surfaces/proposal.md) 收敛 interaction、entry、contract 和 tools；产品合同与 DeerFlow 保持原边界。

## 决策 / 方案

Agent friendliness 是导航的首要验收：任务触发路由 -> owning code/test -> 可执行命令 -> 可观察结果与不覆盖面。
常驻 [应用 AGENTS](../../deep_research_harness/AGENTS.md) 只留短路由，细节按需读取；保持既有字数预算。

持续维护触发条件：

| 触发 | 同轮回写 |
| --- | --- |
| 新增/搬迁/删除源模块 | Repo 地图的对象归属与直接入口 |
| 修改 skill 使用、模型/工具绑定、stream/报告路径 | 研究过程地图；区分声明能力与实际发生证据 |
| 新增/删除测试或改变收集方式 | 测试资产地图、车道声明与实际 runner 一致 |
| 新录制/更新 fixture | 消费者、来源、配置/pin/revision、敏感数据审查与局限 |
| 发布形态改变 | 运行态总图、命令菜单/playbook；以新鲜执行回执为准 |
| 新增文档 | 文档索引、required paths、doc scope；入口预算不因堆细节上调 |

每次维护的完成判据：涉及的对象都有可点击入口；链接有效；选中测试确实执行而非 skip；相关门禁返回 0；运行事实未被 doc 虚构。

## 风险 / 取舍

- 地图是缓存而不是第二套权威 -> 保持链接到 owning code/test，改变对象时同轮回写。
- 目录迁移可能改变 unittest 发现 -> owning change 比较迁移前后测试 ID，并证明 contract 负例被发现、integration 仍排除。
- 研究质量与 Harness 控制容易混淆 -> fixture 只证明合同，真实研究质量仍需显式观测。
- 无期限整理容易扩大范围 -> 维护由具体改动触发，不持续无目标扫描、不擅自实现下列产品决策。

待另行决策 / owning change（不是本轮暗中修复）：

- refine 是提交下一代还是立即重跑；active/watch/cancel 的跨进程语义。
- completed 与 final report admit 是否需要更强完成合同。
- skill 加载的强制程度，以及研究证据/充分性 gate 的真实接线。
- 多用户服务、worker、备份/恢复与正式部署面。
- 真实模型回放完整协议与 provenance、live 研究质量评估。

## 落地关联

导航与结构整理由 [clarify-application-surfaces](../../openspec/changes/archive/2026-10-05-clarify-application-surfaces/tasks.md) 记录设计、任务和验证；不引入新运行规则。另发现 structure spec 的 complete inventory 文字与 checker 注册路径覆盖范围不一致，需独立规范语义裁决，不暗中扩大 checker。
后续任何行为、权限、持久化合同或架构守卫变更，仍须独立 OpenSpec change 和人的规范语义裁决；本计划不是 apply 授权。

本卡保留为活跃维护入口；不把未来产品缺口标记为完成。会话自动目标完成只代表本轮交付，不代表持续维护终止。
