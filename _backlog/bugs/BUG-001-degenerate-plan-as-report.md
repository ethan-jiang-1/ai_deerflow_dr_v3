# BUG-001: 真梯连续两跑"计划走私 + 计划冒充报告"退化（CLS-018 病状复发）

> 严重级别: P1 | 发现: 2026-10-10 | 状态: 活跃

## 症状

两次真梯 run（E-2 录制尝试，`runs/d_20261009/f6d960ec-…` 与 `runs/d_20261009/2d8762ce-…`）
以完全相同的形态退化：

1. 模型把**完整研究计划塞进 `ask_clarification` 的问题文本**（"请确认是否按此计划执行"）
   ——CLS-018 记录过的走私病状；
2. headless 自动应答后，模型**将计划文本直接作为最终报告输出**（`final/report-gen1.md`
   以 `<research-plan>` 标记开头，约 4KB，零检索、零委派、零来源）；
3. 该"报告"经 hold point **被 admit**（结构契约只验结构：标题/来源节字样计划里都有）；
4. journal 仅 3 事件（model_tool_call/run_completed/disposition_recorded），
   `behavior-profile` 机器判定：`degenerate research — 0 search-or-fetch call(s) recorded`
   （CLS-020 机器当日落地后首次实战即命中此案）。

对照：CLS-018 落地（2026-10-09）前的真梯全旅程跑（如 `5bb2c343`，34 事件、9 搜索+3 抓取+1 委派）
正常完成研究。两次退化均发生在 CLS-018 措辞纪律落地之后。

## 根因（假设）

- H1（主嫌）：CLS-018 的提示词措辞（"提问轮只携带 ask_clarification、计划确认只走标记"）
  在真梯上产生了反效果——模型遵从了"提问轮带 ask_clarification"的字面，把计划整体装进问题里；
  且"计划确认只走标记"未阻止模型把带标记的计划当最终消息发出。
- H2（并行嫌疑）：计划标记检测（CLS-016 plan-marker-detection）未覆盖"最终报告以
  `<research-plan>` 标记开头"的形态——标记在场却未触发闸门/未拦截 admission。
- H3（排除项）：录制包装（JournalingDeepSeek）不是原因——两次退化形态一致，且第二次
  未经任何 journaling 行为差异（journal 零行是旁路 bug，与本退化无关）。

## 复现

`CONFIG=base make create PROBLEM="<调研类问题>"`（headless；两次不同问题均触发）。

## 修复关联

待立 change：①提示词/契约层复查（H1）——覆盖 headless 自动应答轮的措辞边界；
②plan-marker 检测对 final_report 形态的覆盖（H2）——或 admission 结构契约对
"报告主体即计划"的拒绝面；③验收判据：behavior-profile 画像 `min_search_calls` 不再
命中退化（真梯复跑 ≥1 搜索/抓取调用）。横切排查：CLSS-018 的真梯验收是否需要复测。
