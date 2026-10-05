# Deep Research SOP：本地阅读与调整入口

从这里开始读 [SKILL.md](SKILL.md)。这是当前 DeerFlow pin 对应的完整英文原文，已复制到 Harness，方便逐条阅读、讨论和比较。本目录目前用于参考；应用仍使用框架的 skill 加载机制，修改此处不会自动改变一次研究。

## 先看哪几段

| 问题 | 原文入口 | 中文理解 |
| --- | --- | --- |
| 什么任务触发研究？ | [When to Use](SKILL.md#when-to-use-this-skill) | 需要网络信息的研究问题，以及依赖现实信息的内容生成 |
| 第一轮查什么？ | [Broad Exploration](SKILL.md#phase-1-broad-exploration) | 搜背景，发现子问题、维度、参与方和观点 |
| 怎样继续深挖？ | [Deep Dive](SKILL.md#phase-2-deep-dive) | 逐个重要维度定向查询、换问法、读全文、追引用 |
| 怎样避免单面结论？ | [Diversity & Validation](SKILL.md#phase-3-diversity--validation) | 补事实数据、案例、专家意见、趋势、比较和反对意见 |
| 什么时候可以写报告？ | [Synthesis Check](SKILL.md#phase-4-synthesis-check) | 检查 3–5 个角度、重要全文、具体证据、局限、时效和权威；不足就继续研究 |
| 时效怎么处理？ | [Temporal Awareness](SKILL.md#temporal-awareness) | 以运行上下文的日期构造查询，按“今天/本周/本年”选择时间精度 |
| 研究够不够？ | [Quality Bar](SKILL.md#quality-bar) | 能回答关键事实、案例、专家观点、趋势、局限和当前意义 |

四阶段可以回返；skill 没有定义固定搜索次数或静态 Python 执行图。原文示例保留了部分 2024 年查询，但时间规则要求使用实际当前日期，不能照抄示例年份。

## Skill 能决定什么

Skill 提供模型执行研究时的方法：怎么展开、深挖、补反例、检查充分性、综合回答。它是研究 SOP 的重要控制面。

工具权限、子代理可用性、递归上限、取消、状态转换和产物准入由框架配置及 Harness 代码负责。文字中的“必须”需要模型遵循；当前 Harness 没有把四阶段检查全部接成硬 gate。当前 [client binding](../../../src/deerflow_deep_research/runtime/adapters/client.py) 使用 `available_skills=None`，并没有显式要求每次读取这份 skill。具体运行是否加载、是否照做，要看工具调用与 checkpoint；方法见 [研究过程地图](../../research-process.md#怎样看到某一次真的发生了什么)。

## 将来调整在哪里

先在本目录审阅 SOP、指出要改的具体条款和预期研究行为。需要改变实际运行时，建立 Harness 自有的 skill 版本并通过框架公开加载接口接入，再验证模型实际读到的是本地版本；只改这份文档副本不会生效。这一步属于认知策略和接线变更，要有独立设计、加载验证及适用的真实研究评估。

目前原文保持不变，便于作为基线比较。没有观察到问题、也没有产品需要的框架能力继续使用上游；这里不复制 lead agent、工具或调度实现。读取这份参考原文也不等于安装了一个新的 Coding Agent skill。

## 来源与维护

- 上游：[bytedance/deer-flow](https://github.com/bytedance/deer-flow)。
- 来源 commit：`ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7`。
- 来源路径：`skills/public/deep-research/SKILL.md`。
- 原文 SHA256：`04712f4daa7937cc1f8dabc1a086a9549e670eb3fa3f1a8d30abdc3ea8b31a79`。
- 机器可读记录：[provenance.json](provenance.json)。上游 MIT 许可及版权声明：[LICENSE](LICENSE)。

升级上游 pin 时，明确审阅 SOP 差异后决定是否更新快照，并同步来源 commit/hash。不得自动覆盖本地讨论或未来自有版本。此次只复制公开 skill 和许可，没有修改上游文件，也没有更改运行时配置。
