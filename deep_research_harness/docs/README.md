# Documentation Index

> 文档索引：每份文档一行状态；事实的权威在各自 owner（代码 / spec / 测试），这里只路由。

| 文档 | 状态 |
| --- | --- |
| [`../AGENTS.md`](../AGENTS.md) | ✅ 分层、owner 路由、LLM-Node 门 |
| [`../CONTEXT.md`](../CONTEXT.md) | ✅ 产品词汇承重词 |
| [`control-map.md`](control-map.md) | ✅ 唯一控制总图：主链、两种 loop、owner 路由、发布与未实现清单（新 agent 先读） |
| [`run-bundle.md`](run-bundle.md) | ✅ Run Bundle 持久化合同与 artifact 权属表 |
| [`research-process.md`](research-process.md) | ✅ Deep Research skill、lead agent、绑定与运行证据入口 |
| [研究 SOP 本地入口](skills/deep-research/README.md) | ✅ 中文阅读路由、完整 skill 快照、来源与未来调整边界 |
| [`local-operations.md`](local-operations.md) | ✅ 本地命令与环境的坑 |
| [操作旅程 playbook](playbook/run-research.md) | ✅ 跑研究的步骤、完成判据与坑（COMMANDS 的路由目标） |
| [`../tests/README.md`](../tests/README.md) | ✅ 测试资产、接口、样本来源、放置规则与最小红绿路径 |
| [`testing-and-evaluation.md`](testing-and-evaluation.md) | ✅ lane 划分、替身阶梯与最小车道选择 |
| [`quality-register.md`](quality-register.md) | ✅ 质量机器单一清单面（代码事实源 = `engine/machines.py`） |
| [`known-limitations.md`](known-limitations.md) | ✅ 存续中的产品已知限制（接手者必读） |
| [应用 README](../README.md) | ✅ 短控制地图：入口、运行链、目录职责与最小验证 |
| [tools README](../tools/README.md) | ✅ 显式录制/诊断操作与副作用 |
| [fixtures README](../tests/fixtures/README.md) | ✅ 输入样本、消费者与来源局限 |

## 地图维护触发条件（谁变了就同轮回写哪张图）

> 地图是缓存不是第二套权威：事实在 owning code / spec / test。每次改动的完成判据——
> 涉及对象有可点击入口；链接有效；选中测试确实执行；相关门禁返回 0；运行事实未被 doc 虚构。
> （承自 agent-friendly-repository-map 维护卡，2026-10-06 落户此处。）

| 触发 | 同轮回写 |
| --- | --- |
| 新增/搬迁/删除源模块（含 runtime 子目录、scripted providers） | 仓库根 README 目录表 + [控制地图](control-map.md) 的目录树与 owner 路由 |
| 运行数据根变化（`runs/` 位置、`DEEP_RESEARCH_RUNS_ROOT` 语义） | 仓库根 README、控制地图、[Run Bundle 地图](run-bundle.md) 的路径合同行 |
| 修改 skill 使用、模型/工具绑定、stream/报告路径 | [研究过程地图](research-process.md)；区分声明能力与实际发生证据 |
| 新增/删除测试或改变收集方式 | [测试资产地图](../tests/README.md)、车道声明与实际 runner 一致；collection guard 同步 |
| 新录制/更新 fixture | 消费者、来源、配置/pin/revision、敏感数据审查与局限（fixtures README） |
| 发布形态改变 | 控制地图、[命令菜单](../COMMANDS.md)/playbook；以新鲜执行回执为准 |
| 新增文档 | 本索引、治理 required-paths、doc scope；入口预算不因堆细节上调 |

产品方向缺口（skill 强制、服务化、真实质量评估）均已由 Phase 5 裁决挂号
（CLS-014 归档记录 + [known-limitations](known-limitations.md)），不在此重复维护。
