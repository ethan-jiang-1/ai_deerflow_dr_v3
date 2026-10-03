# Plan: 深研究真跑复盘 + 递归上限/异常守卫修复（deep-run-postmortem）

> 类型: 复盘（postmortem） + 设计 | 更新: 2026-10-03
> 对象: bundle `997fe460…`（EASA 无人机进口认证深研究，真 DeepSeek + 真 deep-research skill）

## 背景 / 现状（复盘记录）

第一次完整深研究真跑的实证与事故：

**工作了的（利用率与 UX 的黄金证据）**
- lead agent 明言 "loading the deep-research skill for methodology" → **skill 真实装载**
- 完整研究行为链：规划 → `web_search`×3 → "fetch the key EASA official pages" →
  `web_fetch`×10+ → "get a few more specifics: remote ID / transition rules /
  third-country obligations" → 再检索 → "I have comprehensive material. Now I'll
  write the briefing" —— **planner→检索→定向抓取→综合 的真流水线**
- 修过的 UX 生效：直播视图可读（模型思考内联流 + "model calls web_search×3" 短语行）
- **崩溃检测按设计工作**：CLI 崩溃 → PID 死 → status 判 `crash_detected` → `failed-resume`
- **研究材料无损**：checkpoint 存 23 条消息 / 13 条工具结果——refine 同线程续跑即用

**坏了的（两个修复项 + 环境噪音）**
1. `GraphRecursionError`：LangGraph 递归上限 100 步耗尽（深研究 10+ 轮工具调用就到顶）
   ——CLI 裸崩输出堆栈，而非人话失败。
2. CLI/engine 未捕获框架异常 → 异常直接穿透，run 停在 active（靠 status 补判）——
   应当场转 failed-resume + 人话报错。
3. 环境噪音（非本仓问题，如实记录）：本机 npm 缓存 root-owned（Readability.js 回退
   纯 Python ✓ 框架优雅降级）；Jina 无 key 422 回退；DDG 偶发超时。

## 决策 / 方案

1. **递归上限提高**：base/fixture 配置 `recursion_limit: 100 → 300`（框架自带上限
   max 1000；深研究 10+ 工具轮 × 每轮多步，300 是保守起点）。
2. **异常守卫**：`run_research` 捕获流消费中的框架异常 → 转移 `failed-resume` +
   journal `terminal` 条目（reason=framework_error, error=异常类名）+ CLI 人话输出
   （"研究在第 N 回合因 X 失败；材料已保存，可 refine 续跑"）——终态诚实要求的
   符合性修复（RUB-001 fail-loud / DEW-001 terminal honesty 已声明）。
3. **复跑即验证**：修复后 `refine` 崩溃的 bundle（同 thread，generation 2）——模型
   在 checkpoint 里看得到自己已收集的材料，应直接写简报——**续跑路径本身也是验证**。

## 风险 / 取舍

- [300 步仍不够] → 失败会再次 fail-loud（守卫在场），按证据再调。
- [守卫吞掉应穿透的编程错误] → 只在 run_research 边界捕获（框架/流层异常转终态）；
  本仓代码缺陷照常抛出（红测试会抓）。
- [环境噪音修复（npm 权限）] → 本机一次性 `chown`，不入仓。

## 落地关联

单 change：`harden-run-continuity`（skip_specs 符合性修复：配置上限 + 异常守卫 +
红绿测试 + 真跑 refine 复跑验证）。
