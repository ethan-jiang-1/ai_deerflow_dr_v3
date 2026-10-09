# BUG-001: headless 跑计划门缺席——计划输出直落 completed 冒充报告（根因已确诊，初判修正）

> 严重级别: P1 | 发现: 2026-10-10 | 状态: 活跃

## 症状（2026-10-10 根因确诊后修正）

真梯 headless `create`（研究型问题）连续四跑同形态退化（`f6d960ec`/`2d8762ce`/
`5b675921`/`ab6a6ec0`，2026-10-10）：

1. 模型按 deep-research skill 方法论**输出研究计划为纯文本**（`<research-plan>` 标记 +
   末尾"请确认"，**零工具调用**——journal 的 model_tool_call detail 无 `calls` 键实证）；
2. 运行**直接 completed**（无任何 plan-gate/clarification lifecycle 事件），计划文本
   （4KB）作为 final_report 经 hold point 被 **admit**；
3. 零检索、零委派、零来源——`behavior-profile` 机器判定
   `degenerate research — 0 search-or-fetch call(s) recorded`（CLS-020 机器当日实战命中）。

**初判修正**：原卡症状一"计划走私 ask_clarification"是**误读**——`answer_excerpt` 是轮文本
尾 80 字符（`_consume_turn` 在案），不是澄清问题；部分历史跑（如 `1d8f6b86`）确有真
ask_clarification，但与本案无关。按纪律如实改正，误读过程留本节。

## 根因（已确诊，证据链）

**headless 上下文的 `_plan_handler()` 返回 None**（cli.py:65 在案："A non-interactive
context gets no handler and the engine never enters a plan phase"）→ `on_plan=None` →
`awaiting_plan=False` 且 `PLAN_REQUEST_SUFFIX` 不附 → 模型的计划输出无门可进 →
`detected=None` + `awaiting_plan=False` → completed → 计划冒充报告被 admit。

对照实证：历史全旅程真跑（如 `5bb2c343`，34 事件 9 搜索）均为 **TTY 交互跑**（计划门在、
人确认后研究）；四次退化跑均为 headless 后台跑。原三假设裁决：**H1（CLS-018 措辞反效果）
不成立**（headless 下措辞后缀根本没附）；**H2 部分成立**（admission 对"计划冒充报告"零
拒绝面——真正的洞）；**H3 维持排除**；新增 **H4（确诊）：headless 计划门缺席是设计缺口**。

## 复现

headless（无 TTY 无 `DEEP_RESEARCH_INTERACTIVE`）`CONFIG=base make create PROBLEM="<研究型
问题>"`——后台 job/管道环境即触发。

## 修复关联

change `fix-headless-plan-gate`（进行中）：
①headless 计划门 = **自动确认**（auto-confirm handler，与澄清的有界自动应答同哲学；journal
可见 plan_proposed/plan_confirmed 全生命周期）；
②admission 拒绝面：final_report 携带 `<research-plan>` 标记 → `report_structure_violation`
点名拒绝（计划不是报告——结构维度新方面，复用现有封闭码）；
③验收判据：真梯 headless 复跑，behavior-profile `min_search_calls` 不再命中退化
（≥1 搜索/抓取调用），且全旅程（计划→检索→报告）journal 完整。
