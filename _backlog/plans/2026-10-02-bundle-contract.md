# Plan: Run Bundle 合同（bundle-contract）

> 类型: 设计 | 更新: 2026-10-02 | 来源: digest 边界 plan 六裁决推敲（裁决 #2/#3/#4观察层/#6）

## 背景 / 现状

裁决：checkpoint 归 **Bundle 内**（精简实现）；外层 = **普通状态机**；HITL **暂缓**（v1 run
全自动）。**debugger 为用户一级硬需求**：watch 直播 / journal 时间线 / checkpoint 回放三层
从第一天都要好用。元原则：v2 资产按「拿得过来」重加权。证据底座：
`_reference/v2-run-bundle-implementation.md`（v2 全量实现 + 继承/丢弃清单）、
`v2-harness-app-shape.md`。

## 决策 / 方案

1. **目录契约**（抄 v2 可继承部分，路径常量集中一个纯 domain 模块）：
   `scopes/{bucket}/{bundle_id}/` + 子树 request/work/evidence/final/diagnostics +
   `state.json` + **`checkpoint.sqlite`**（**sync SqliteSaver 直连**——embedded client
   为同步驱动，async saver 不匹配，修正依据见 wiring plan 决策 1 修正注（2026-10-02）；
   无 64KiB bound 包装、无 legacy 校验子系统；打开失败 fail-loud → failed-resume 降级）。
   thread_id 与 deerflow pin commit 记进 state.json。
2. **普通状态机**（domain + engine 层纯函数）：v1 动作集 start/status/cancel/**refine（仅
   方向文本形态——砍 v2 的 continuation 双形态/replay receipts/crash-window 恢复例外）**；
   状态 active/completed/cancelled/failed-resume（v2 的 suspended/blocked 随 HITL 暂缓砍）。
   state.json 单一真相 + revision CAS + 目录 lease (dev,ino) 活性重验——v2 最硬可继承资产，
   **拿得过来，保留**。
3. **三层观察**（debugger 硬需求）：journal（diagnostics/，有界保留 + 优先级驱逐 +
   admission anchor 永不驱逐——v2「诚实有界」哲学保留；**新增 model_tool 类别落账**
   stream 的工具调用事件；修复 v2 O(n²) 整写 → 真 append + 周期 compaction）；watch 与
   checkpoint 回放的渲染在 entry-surface plan。
4. **验收收口最小版**（engine 层）：纯函数 validator（写前跑）+ hash 链 ledger
   （evidence/submissions.jsonl，单一 commit owner，admit/reject/replay 三分）+ gate
   最小推导（PhaseVerdict pass/blocked 起，repair 预算机制砍）。ResultCode/事件字段
   **小封闭集合起步**（v2 轰炸教训）。
5. **删除语义**：无注册表（发现=扫描目录）、删除即 never recover、写路径活性重验——
   v2 反模式清单（不复活/不静默迁移/不 second authority）全数继承。
6. **显式组成**：fixture/mixed/all_real 状态记进 state.json；v3 的 fixture 替换层 =
   **provider 层**（模型/搜索工具后端），非 v2 的节点适配器层（研究本体已交框架）——
   形态随本 plan 的 change 细化。

## 风险 / 取舍

- [POSIX 手工安全层复制] → v2 每 store 复制一遍（O_NOFOLLOW/mkstemp 遍布）→ v3 抽一个
  共享「安全文件原子层」小模块（拿得过来的部分）+ 接受单进程下可简化的部分。
- [checkpoint 内嵌的格式绑定] → 接受（2/6 裁决）：fail-loud 降级，事实不受损。

## 落地关联

成熟后**经用户拍板**入线（HITL 闸门）。likely change：bundle 域契约 + 状态机 + journal 首笔
（产品第一 change 候选）。
