# Plan: 流适配器修正 + token 流式直播视图（stream-adapter-and-live-view）

> 类型: 设计 + 复盘（postmortem） | 更新: 2026-10-03
> 来源: real 梯首跑的实机调试（本 plan 的背景节就是调试记录）

## 背景 / 现状（调试记录：fake 把 bug 盖住了）

第一次 real 梯真跑（真 DeepSeek + 真 deep-research skill）成功产出高质量回答，但暴露
三个 fake 事件盖不住的真实形状问题：

1. **`messages-tuple` 的 data 就是消息块本身**。实机 dump（真流逐事件打印）：
   `{'type': 'ai', 'content': '1', 'id': 'lc_run--…'}` —— 是**扁平的 chunk 字典**，
   且是**逐 token** 的（"1"/"+"/"1"/"等于"/"2"/"。" 每 token 一个事件）。
   我们适配的是 `data["message"]` 包装形（fake 事件按假设形状构造）→
   真实流下 `kind` 判定落空。
2. **真实 journal 因此是空的**（只有 terminal 一条）：`model_tool`/`subagent`
   条目在真实流下从未记上——journal 沉浸 sink 对真实流静默失效。终态判定没坏
   （`values` 快照路径权威，扛住了所有关键判定——这也是"快照权威"设计决策的实战回报）。
3. **实时视图不可读**：逐 token 事件被渲染成每事件一行 → 直播变成 "message"×12。

### DeerFlow 流协议速览（学到的机制，供驾驭）

| 事件族 | data 形状 | 语义 |
|---|---|---|
| `values` | `{title, summary_text, messages[...], artifacts}` | 全量状态快照；**终态判定的权威来源**（消息完整、含 tool_calls/additional_kwargs） |
| `messages-tuple` | **消息块本身**（扁平 dict，逐 token） | 流式增量；tool_calls 在块上以完整 dict 出现 |
| `custom` | dict（含 event 字段） | subagent 生命周期等带外事件 |
| `end` | `{usage: …}`（stop_reason 仅在触限时出现） | 回合结束 |

装配快照（每 run 一张）已实证：系统提示词 33,588 字符、含 deep-research skill、
真实工具面 `web_search/web_fetch/present_files/ask_clarification/review_skill_package/
list_uploaded_files/task` —— DeerFlow 的利用是**晚绑定**的（运行时才可见）。

## 决策 / 方案

1. **适配器修正**（`runtime/run_engine.py` 的 `_consume_turn`）：`messages-tuple` 的
   data 直接当消息块读（`data["type"]`，去掉 `data["message"]` 包装假设）；fake 测试
   事件同步改为真实形状。这是对既有 deerflow-wiring 需求（"feeding the journal"）的
   **符合性修复**，无需改 spec 文本。
2. **journal 聚合到回合粒度**：不再逐 token 记 `model_tool`（那会淹没账）——
   回合内累积 AI 文本，回合结束时记一条聚合条目（含最终文本节选与工具调用摘要）。
   `values` 快照的权威地位不变。
3. **直播视图改为 token 内联流**（ChatGPT 式）：AI 文本 chunk 以
   `print(chunk, end="")` 内联输出（不换行），工具调用/状态变化/回合结束才换行成
   现有短语——渲染词表不变，新增"流式模式"语义。`watch`/journal 投影不受影响
   （它们读的是回合粒度的聚合条目）。
4. **真集成绩效**：真 DeepSeek 流下，journal 出现回合聚合条目 + 直播视图逐字显示
   回答——两个问题（journal 静默失效 + 直播不可读）一次闭合。

## 风险 / 取舍

- [渲染短语变化会动 golden/单元断言] → 预期内：受影响断言随本 change 显式更新
  （红绿），golden 的形状断言保持"稳定短语 + 排除易变值"的纪律。
- [token 级 on_event 高频回调] → 回调只做打印（O(1)）；journal 聚合在回合内做，
  无逐 token I/O。
- [适配器再遇未见过的事件形状] → 已有 fail-closed 先例（澄清回声、fallback 标记都
  是实机调试揪出的）；真跑即测试的纪律继续。

## 落地关联

单 change 落地：`fix-stream-adapter`（deerflow-wiring 符合性修复 + entry-surface
直播呈现；预计 skip_specs——对既有需求的符合性修复，无新增规范行为）。落地后：
real 梯跑一个**完整深研究问题**（多轮 planner→研究→报告），作为"DeerFlow 利用率 +
UX 好用"的终极实证；journal 出现真实的 model_tool 沉浸条目。
