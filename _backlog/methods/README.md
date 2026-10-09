# methods/ · 按当前问题选择方法

这里的方法辅助 [backlog 流程](../README.md)：澄清需求、补事实、比较方案、准备验收、交接结论。
先用下表选一篇，再读它的步骤；每张卡不必跑完整套。执行到需要外部技能的步骤时，才加载完整
本体；技能未注册或本地缺失时，如实报告缺了哪个本体、阻断哪一步，继续不依赖它的工作。

backlog 负责把问题想清楚，向 OpenSpec 申请后续处理，是前后两段。这里准备结论、依据和必要的
验收标准；下游是否立 change、怎么实施，由 [OpenSpec 流程](../../openspec/README.md) 与
[change-guidance](../../openspec/change-guidance/README.md) 决定。申请提交不等于 change 已立，
也不等于下游完成。

## 现在需要哪篇

| 当前情况 | 方法 | 结果写在哪里 |
|---|---|---|
| 需求不清楚，术语有歧义，或问题太大需要拆开讨论 | [澄清需求](requirements-elicitation.md) | 卡上的目标、边界、已确认回答和待确认问题 |
| 缺事实，需要调研、询问或试原型；收到的外部报告还未经核实 | [补充证据](requirements-probes.md) | 短结论回原卡 |
| 需求已清楚，但不知道怎样算完成 | [设计验收标准](validation-design.md) | 原卡的 `## 验收标准` |
| 信息已齐，需要整理需求、比较方案或决定是否关闭 | [整理方案与结论](requirements-synthesis.md) | 原卡的方案、取舍、结论和关闭条件 |
| 结论已确定，需要申请下游处理或指向已有决定 | [申请下游处理](issue-to-change.md) | 原卡的结论与去向；是否立 change 由下游拍板 |

## 后续需要验证时

这两篇是按需使用的辅助方法，不另立实施流程或验收队列。实施与 change 的维护遵循下游规则。

| 当前情况 | 方法 | 用途 |
|---|---|---|
| 已有验收标准，需要知道用什么证据检查 | [选择证据](validation-evidence.md) | 按 [车道表](../../deep_research_harness/docs/testing-and-evaluation.md) 选最小车道，说明它能证明什么 |
| 声称做完，需要检查是否符合要求 | [判断验收结果](validation-judgment.md) | 逐项记录通过、不通过、证据不足或等待用户判断；结果回到承载该工作的现有记录 |

发现需求不清时，回到具体问题补充确认；发现实现不符合标准时，记录实际差异。不能改标准来迁就实现。

## 方法的维护

这些是持续打磨中的本仓方法，消化自 `ai_dsh_assitant/_backlog/methods/`（其正文又适配自
Matt Pocock 的技能，见其 methods/README 登记的版本），按本仓语境改写：卡片命名、户口字段、
四态关闭、OpenSpec 下游、车道证据 owner 均为本仓事实。文件保留 `name` / `description` /
`whenToUse` frontmatter，正文写输入、步骤、结果位置和完成条件。它们不进入技能发现目录。

方法依据应来自实际使用；未试用的适配须如实说明。问题和结论留在卡片，方法里不维护进度或待办。
方法改进随 owning change 或直接小步修改（方法不是工作件，不占 issues/ 名册）。

## 外部技能的来源与读取

执行时先看当前技能目录：能调用就调用；未注册但能读取完整本体的，说明是读源执行后再继续。
两者都不可用就报告缺少哪个本体、阻断哪一步，继续不依赖它的工作。摘要不能替代执行说明。
这里不安装技能、不修改全局发现配置。

| 方法 | 需要时调用的技能（本仓目录或 harness 目录中按名调用） |
|---|---|
| [澄清需求](requirements-elicitation.md) | `grilling`、`domain-modeling` |
| [补充证据](requirements-probes.md) | `research`、`prototype` |
| [整理方案与结论](requirements-synthesis.md) | 需要分析模块接口时读 `codebase-design` |
| [设计验收标准](validation-design.md) | `tdd`、`codebase-design` |
| [选择证据](validation-evidence.md) | 无外部技能依赖；按本仓 [车道表](../../deep_research_harness/docs/testing-and-evaluation.md) |
| [判断验收结果](validation-judgment.md) | 需要相应步骤时读 `code-review`、`diagnosing-bugs` |
| [申请下游处理](issue-to-change.md) | `openspec-propose`（下游入口）；打磨用 `polish-openspec-change` |
