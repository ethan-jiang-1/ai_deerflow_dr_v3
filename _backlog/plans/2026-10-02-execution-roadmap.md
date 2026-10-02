# Plan: 执行排产——从账本到首个 change 闭环

> 类型: 设计（排产） | 更新: 2026-10-02

## 背景 / 现状

上一会话的 change `establish-project-structure` propose 进行到一半，工件未提交、已不在工作区
（`openspec/changes/` 只剩 `archive/.gitkeep`；交接文档 `/tmp/handoff-ai-deerflow-dr-v3-2026-10-02.md`
部分失真）。当前治理门禁 3 红同根（`check_project_reqs` / `check_project_architecture` /
`check_project_req_coverage`，全部指向 PRS-001 无 owning spec），是 7/7 全绿的唯一障碍。

本 plan 是[_backlog 总流程](_backlog/README.md)下**当前放行的一把**；原 todo（todos 类别已按
用户决定整体裁撤）的执行链由本 plan 吸收。

## 决策 / 方案

执行顺序（0 → 4，每步可独立验收）：

0. **落袋**：提交账本增量——DSH 借鉴 plan、`_backlog/README.md` 总流程节、账本简化
   （todos 类别裁撤 + required-paths 同步）、本 plan。提交信息用引号 heredoc
   （`git commit -F -`，仓库 Shell 卫生规矩）。
1. **重做 propose**：按 openspec-propose 工作流重做 establish-project-structure 四件工件
   （proposal / specs delta / design / tasks），按规划边界停在 apply 前。Change Focus 复用
   交接记录：owner=`openspec/governance`，seam=`deterministic-guardrail`，
   policies=`deerflow-downstream`；配方 = boundary plan 的 change ① 实测清单。
1.5. **polish（用户拍板的固定工序）**：四件工件齐后、apply 前，走
   polish-openspec-change 对 proposal/design/delta specs/tasks 做迭代审查与加固
   （含验证计划）；打磨通过后停在 apply 边界等用户拍板。
2. **切片进 closeout**：垂直切片五行走查写进 tasks 的 closeout 任务（DSH 借鉴 plan 的 E 项）。
3. **等用户拍板 → apply**：`@impl PRS-001` 注解 → main spec 建立 → 3 红转绿 → 7/7 全绿；
   治理测试套件保持全绿；退出码直测回执。这一笔走完即 FAQ Phase 1 的正式垂直切片，
   三清单（打不开的链接 / 要靠猜的 owner / 没有证据的声称）回填 DSH 借鉴 plan。
4. **收尾**：本 plan 关闭，`git mv` 至 `_done/_closed_plans/`（三处 README 联动）。

后续队列（不与当前一把并行，做完再放下一把）：

- 治理硬化批（各自独立 change，挂载点见 DSH 借鉴 plan 落地关联表）：
  A（CI + hook，用户拍板时机后定）→ B/F（change-practice 硬化）→ C（入口文件预算闸）；
- 产品线：change ② run-bundle 生命周期合同（design 先答 Bundle vs checkpointer 谁是权威，
  用 DSH 借鉴 plan 的映射表）→ ③ 显式组成与 fixture 隔离 → ④ harness ↔ 原生能力接线。

### 三个 plan 的接力关系与关闭次序（2026-10-02 盘算）

三份 plan 不是平行三件事，是一条接力链；落地次序由依赖决定：

| plan | 本质 | 状态 | 落地形态 |
|------|------|------|---------|
| digest（边界） | change ① 配方 + 产品边界四问 | 配方已干跑验证；**决策/方案节待填**（Q2/Q3 未答） | 配方 → change ①；四问答案 → ②/④ 的 proposal/design |
| DSH 借鉴（差距分析） | 治理硬化队列 A–F + 产品设计检查单 | 分析已完成 | A–F → 硬化批各 change；E → ① closeout；映射表 → ②/④ design |
| 本 plan（排产） | 调度器：当前放行的一把 | 第 0 步已落袋（abd21b7） | 第 1–3 步 = change ① 闭环；关闭后指针移交 |

执行分三段：

1. **第一段（当前，pipeline 里唯一一把）**：本 plan 第 1–3 步 = change ① 闭环。配方来自
   digest plan（已验证），E 来自 DSH 借鉴 plan 顺手进 closeout。**buffer 并行推敲**（不占
   pipeline）：填 digest plan 的「决策/方案」四问——① 不依赖它，② propose 前必须有答案，
   DSH 借鉴的映射表就是答题框架（静与动四层 + 事实源检验法 + 模型可见⟺落日志）。
2. **第二段（治理硬化批，做完 ① 再放行）**：CI+hook → B/F → 预算闸。次序理由：CI 让后续
   每个 change 的门禁都有机器兜底，越早越省；B/F 是纯文本纪律最便宜；预算闸要动 checker
   最重。D（一行理由）并入第一个触碰 deep_research_harness/AGENTS.md 的 change（预计 ②）。
3. **第三段（产品线）**：change ②（design 用映射表 + 边界四问答案）→ ③ 显式组成 → ④ 接线。

关闭次序（谁先退休）：**本 plan 最先**——① 闭环后即关，「当前该做什么」指针移交 DSH 借鉴
plan 的落地关联表 → **DSH 借鉴 plan**——硬化批完成且 ② 引用映射表后关 → **digest plan
最后**——② 归档、按吸收义务把其独有内容（含 Q2 若留给 ④）全部吸进 ② design 后关。
每次关闭按三处 README 联动，同步改两处「当前该做什么」指针。

### Goal 队列（用户拍板，2026-10-02）

落地以 ongoing goal 驱动，一次一个，前一个完成后再设下一个：

1. **进行中**（goal 已设立）：本 plan 落地——change establish-project-structure 闭环
   （propose → polish → 拍板 → apply → 门禁 7/7 绿 → 关闭本 plan）。
2. **待设立**：DSH 借鉴 plan 落地——A–F 硬化批逐个 change（A：CI+hook → B/F：
   change-practice 硬化 → C：入口预算闸；D 并入第一个触碰 deep_research_harness/AGENTS.md
   的 change），每个走 propose → polish → 拍板 → apply 闭环；A–F 全部被吸收后关闭该 plan。
3. **待设立**：digest（边界）plan 落地——「决策/方案」四问的 buffer 推敲可与队列 2 并行做
   （不占 pipeline），但该 goal 的落地动作 = change ② propose/design 消化四问并走完闭环；
   ②（及 ④ 对 Q2）吸收全部独有内容后关闭该 plan。

每设一个 goal，objective 指向对应 plan 的完成判据；goal 完成 = 对应 plan 按关闭次序退休。

## 风险 / 取舍

- [todos 类别裁撤后小件无处安放] → 小件直接以 change 入线，或并入最近 plan 的落地关联；
  不为小件保留常设类别（用户拍板：账本只留 plans / bugs 两类）。
- [/tmp 交接文档与 v3dry 干跑副本可能被系统清理] → 配方已固化在 boundary plan 与本 plan，
  不依赖 /tmp 可达；boundary plan 的实测清单是唯一权威配方。
- [plan 文件名漏日期前缀] → 已把「日期前缀强制」编码进 [`plans/README.md`](README.md) 模板
  （历史经验教训），新建 plan 时模板即约束。

## 落地关联

- change ① 配方：[`2026-10-02-digest-deerflow-native-deep-research.md`](2026-10-02-digest-deerflow-native-deep-research.md)
  的「Change ① 的实测清单」节。
- 缺口 A–F 与 change 挂载点：[`2026-10-02-borrow-dsh-harness-gap-analysis.md`](2026-10-02-borrow-dsh-harness-gap-analysis.md)。
- 完成判据：`openspec validate establish-project-structure --strict` 通过；
  `check_project_gate.py --phase closeout` exit 0（7/7 绿）；治理测试套件全绿；
  切片三清单回填 DSH 借鉴 plan。全部达成后本 plan 关闭。
