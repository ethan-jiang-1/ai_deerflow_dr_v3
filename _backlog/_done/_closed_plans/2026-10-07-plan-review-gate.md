# Plan: 计划确认闸门（plan-review gate）

> 类型: 架构设计 / 产品方向 | 更新: 2026-10-07
> 状态: 关闭（CLS-016，2026-10-07）：plan-review-gate + plan-marker-detection 两 change 均落地归档；真梯演示暴露的检测缺陷已修复并固化为回归测试

## 背景 / 现状

驾驭者在对标 Gemini Deep Research 体验后拍板：研究报告的跑前对齐不能只靠"模型含糊时反问"
（interactive-clarification，已落地），要有**计划确认闸门**——agent 先交研究计划，用户审、改、
确认后才开跑。Gemini 的标杆体验证明了这是本品类最有价值的人工闸门：对齐载体是一份具体可读
的计划，比抽象问答更省用户脑力；用户在烧钱之前手握编辑权。

现状盘点（2026-10-07）：

- 反问机制已落地：`on_clarification` 钩子 + TTY/env 门控 + 三类 journal 事件（commit 5bf6217）；
- 真梯演示（bundle c4ea25ba）观察：deepseek-flash 反问阈值偏高——含糊到一定程度它才问；
  计划闸门把对齐从"模型被动触发"升级为"每次必经"，正好补上这个观察暴露的缺口；
- refine 已有"方向文档"机制（用户写的计划注入下一代），计划闸门是它在 gen-1 的 agent 起草版。

## 决策 / 方案

核心架构（在 change design 中细化）：

1. **计划轮在 lead agent loop 内，不另立 harness 自有 planner 角色**：`run_research` 增加
   `on_plan` 钩子（仅 gen-1 且交互上下文）；第一轮消息 = 问题 + 计划请求框架；第一轮的
   plain text 是**计划而非最终答案**（引擎据此分相）；确认/修订后的计划注入同一线程继续研究。
   备选（被拒）：在 `agents/` 空层立 harness 自有 planner（一次便宜模型调用产计划）——那是
   Phase 5 明确搁置的 bounded role 重启，代价大且不必要；复用 lead agent 的计划能力即可。
2. **与反问自然组合**：计划轮中模型若判断问题含糊可先反问（既有钩子接住），答完再出计划——
   "含糊先问、清楚直接出计划"的优先级由模型判断形成，不写死规则。
3. **CLI 三路交互**：回车=确认原计划；直接输入=修订意见（附加进计划）；s=跳过计划注入；
   q=放弃（SystemExit，bundle 走 crash-transfer 诚实归宿）。终端里逐行编辑多行文本体验差，
   修订意见走"附加"而不是"替换"。
4. **已批准计划物化为 request/plan-gen1.md**：计划是本次运行的范围合同，值得进证据链
   （journal 的 lifecycle 条目有逐出机制，不能当唯一留存）。
5. **headless 行为与今日逐字节一致**：无钩子 = 无计划轮，CI/smoke 不受影响。

## 风险 / 取舍

- [计划请求消息是 harness 作者的模型分支内容] → 诚实触发 node-agent 政策评审（proposal 带
  Node Agent Review 表）；消息是任务级框架（与 AUTO_REPLY 同类），不改 system prompt、不授权工具。
- [模型不理会"先给计划"直接开搜] → 计划轮以 plain-text 收尾才进闸门；若它直接开搜，本轮
  以研究行为收尾时引擎按现状处理（计划闸门退化为无闸门）——诚实记录，不硬拦。
- [每跑多花一轮模型往返] → 交互上下文才启用；用户可用 s 跳过；deep 档跑前对齐省下的
  是整轮跑偏的研究成本。
- [修订意见只是附加不是改写] → v1 取舍；真正的文本编辑器级修订等服务形态再议。

## 真梯演示发现（2026-10-07，bundle 58b5440e）

首轮落地后真梯演示暴露真缺陷：真实框架流的 terminal picture 只带最终消息的
tool_calls，研究轮以纯文本报告收尾时与计划轮不可区分 → 闸门在结尾把报告当计划
误触发（journal 末尾出现 plan_proposed/plan_skipped），并多烧一整轮研究。修复：
计划请求框架要求 `<research-plan>` 标记包裹，引擎仅标记存在时触发闸门，无标记
诚实降级——框架自身 `deerflow_error_fallback` 标记的同款手法。修复 change：
`plan-marker-detection`。

## 落地关联

- 实施走 OpenSpec change `plan-review-gate`（proposal 含 Change Focus + Node Agent Review +
  Control Placement Review；specs delta：entry-surface 交互面 / deerflow-wiring 引擎行为 /
  run-bundle 计划物化新增需求）。
- 前置依赖已落地：`interactive-clarification`（2026-10-07 归档）。
- 产品谱系：本计划与 interactive-clarification 同源于"跑前对齐"方向；Gemini 对标调查结论
  见会话记录（2026-10-07，来源 theaiagentindex.com 与 36 氪）。
