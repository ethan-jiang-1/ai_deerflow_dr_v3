# Plan: Run Bundle 合同（bundle-contract）

> 类型: 设计 | 更新: 2026-10-02 | 来源: digest 边界 plan 六裁决推敲（裁决 #2/#3/#4观察层/#6）

## 背景 / 现状

裁决：checkpoint 归 **Bundle 内**（精简实现）；外层 = **普通状态机**；HITL **暂缓**（v1 run
全自动）。**debugger 为用户一级硬需求**：watch 直播 / journal 时间线 / checkpoint 回放三层
从第一天都要好用。元原则：v2 资产按「拿得过来」重加权。证据底座：
`_reference/v2-run-bundle-implementation.md`（v2 全量实现 + 继承/丢弃清单）、
`v2-harness-app-shape.md`。

## 设计理由：质量控制体系映射（2026-10-02 用户拍板收录）

项目定位（见 wiring plan 背景节三准绳）：研究「带质量控制的 agentic workflow 研发怎么做
合理」，参照建筑施工质量监控体系。本 plan 是 v3 质量控制的心脏，映射如下：

| 施工侧机制 | 本 plan 对应物 |
|-----------|--------------|
| 验收标准先于开工（图纸会审/技术交底） | gate/validator 规则预声明，运行时只裁决不解释（决策 4） |
| 监理独立性（质检不能是施工队自己） | 「模型提议、代码裁决」——v3 存在理由 |
| 三检制（自检/互检/专检） | 自检 = skill Phase 4 Synthesis Check；互检 = `verification.receipts` 引用校验（框架默认开）；专检 = validator/gate |
| 隐蔽工程验收（hold point，覆盖前必检） | 验收收口在提议进 Bundle **前**——不过 validator 不落账（决策 4 ledger 单一收口） |
| 见证取样/材料复验 | artifact 逐个 content_hash 复验；**框架本身 = 进场材料**——契约镜像 contract test 锁其接口（wiring 决策 2） |
| 样板间/试拼装 | fixture 演跑（零凭证彩排，决策 6 + wiring 决策 6） |
| 标准试块（要真的压到破坏） | ReplayChatModel 录制/回放 golden——录一次真实行为，永久比对形状漂移 |
| 旁站监理 + 施工日志 | watch 直播（单向观察）+ journal（有界诚实，决策 3） |
| 关键工序影像记录 | checkpoint 回放（盲区见打磨线索②） |
| 不合格品显式处置（返工/让步/报废，无静默通过） | admit/reject/replay 三分；删除即永久（决策 5）；fail-loud→failed-resume；返工 = refine（v1 砍 in-place repair = 只留「重新施工」砍「现场返修」） |
| 质量追溯（每批材料可溯） | hash 链 ledger + 消息 provenance 戳 + thread_id/pin 入 state.json |
| 竣工资料移交 | inspect 质量报告面（打磨线索③） |
| 质量事故 → 规范更新（PDCA） | postmortem + `@impl BUG-0xx` 原位注解（v2 先例）+ 账本 ritual |

LLM workflow 比施工**多**出的三个质量控制维度：① 非确定性管理（「混凝土」每批不同 →
fixture/replay 确定性）；② 施工队自评不可信（专检必须是代码、互检必须是机械规则）；③
交付后框架会漂移（建筑不会，submodule 会 → pin + 契约镜像 = 「结构被偷偷改」的报警器）。

**打磨线索（缺口，随本 plan 打磨轮逐个过）**：① EV2 负例控制升格为 closeout 机制级条款
（引入违规→看红→还原→看绿并记录——「从不红的守卫≈不存在」）；② RT2/RT7 影像盲区裁决
——system prompt 与组装后可见工具清单不落盘，回放重建得了对话、重建不了「模型当时看到
什么」（接受 + 成文能力边界 vs provider 层 RecordingModel 捕获，两选一）；③ inspect 增
一页「验收结论 + 证据链」人话质量报告（交付给不懂 AI 的接手人）；④ RT10 检查注册处
——validator/gate/contract test/make verify 的单一清单面。

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
   **拿得过来，保留**。澄清自动续答转移（2026-10-02，承接 wiring plan 决策 8）：active
   --检测到未应答 ask_clarification--> auto_proceed（有界 N=2，续答轮经 embedded client
   同 thread 续跑）；耗尽 → failed-resume，未回答的问题原文落 diagnostics。
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
