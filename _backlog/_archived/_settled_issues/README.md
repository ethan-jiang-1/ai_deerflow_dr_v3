# Settled Issues Index — 已结 issue 归档

> 最后更新: 2026-10-09（adopt-issue-ledger-governance：plans 类别退役，本目录更名 `_settled_issues/`，CLS 编号连续） | `_backlog/_archived/_settled_issues/` — 已结 issue 的归档目录。
> 接收来自 [`../../issues/`](../../issues/) 的卡。`_` 前缀 = coding agent 默认忽略。
>
> **卡结后文件名不变，位置即状态。** 移入时分配 `CLS-NNN` 序号，按完成时间递增。

## 接收一张已结的 issue

issue 关闭后从 `_backlog/issues/` 通过 `git mv` 移入本目录：
1. 在本文件表格加一行（CLS-NNN + 日期 + 文件名 + 简述），编号 = 当前最大 + 1
2. 更新最后的 "Next available plan ID" 行
3. 更新 `../../issues/README.md`（移除该卡的行）
4. 更新 `../README.md`（计数 +1）

---

## 已完成列表

| ID | Date | File | Summary |
|----|------|------|---------|
| CLS-001 | 2026-10-02 | [2026-10-02-execution-roadmap.md](2026-10-02-execution-roadmap.md) | 排产 plan：change establish-project-structure 闭环（propose → polish → apply → 门禁全绿 → archive），13/13 任务完成 |
| CLS-002 | 2026-10-02 | [2026-10-02-borrow-dsh-harness-gap-analysis.md](2026-10-02-borrow-dsh-harness-gap-analysis.md) | DSH 借鉴 plan：硬化队列 A–F 全吸收（A→CI+hook、B/F→决策记录纪律、C/D→预算闸+D 理由、E→垂直切片记录），三个治理 change 闭环 |
| CLS-003 | 2026-10-02 | [2026-10-02-digest-deerflow-native-deep-research.md](2026-10-02-digest-deerflow-native-deep-research.md) | digest 边界 plan：六裁决推敲定案（embedded/checkpoint 内嵌/普通状态机/最小 CLI/只配置/HITL 暂缓）+ 元原则 + 契约镜像要求，拆解为三份衍生 plan |
| CLS-004 | 2026-10-03 | [2026-10-02-bundle-contract.md](2026-10-02-bundle-contract.md) | Run Bundle 合同：六决策全落地（establish-run-bundle + establish-run-admission 两 change 归档；validator hold point/哈希链 ledger/gate/RT10 注册处/make verify 变真），质量控制映射成立 |
| CLS-005 | 2026-10-03 | [2026-10-02-entry-surface.md](2026-10-02-entry-surface.md) | 入口面：六子命令 CLI 全落地（establish-entry-surface 归档；create/watch/status/cancel/refine/inspect + 共享渲染 + 有界 watch + 双梯 + EV2 证据 journey/golden/负例；known-limitations 激活） |
| CLS-006 | 2026-10-03 | [2026-10-02-wiring-structure.md](2026-10-02-wiring-structure.md) | 接线与结构：决策 1/2/3/4/6/8 落地（remove-graph-layer + establish-embedded-wiring），决策 5 以明示 posture + 深度自校验守卫处置（pin-subagent-knobs）——三份衍生 plan 全部消费完毕 |
| CLS-007 | 2026-10-03 | [2026-10-03-stream-adapter-and-live-view.md](2026-10-03-stream-adapter-and-live-view.md) | 流适配器修正：真实流形状（扁平 chunk/逐 token）适配 + journal 回合聚合 + token 内联直播；real 梯实证（journal 聚合条目含真实回答节选） |
| CLS-008 | 2026-10-03 | [2026-10-03-deep-run-postmortem.md](2026-10-03-deep-run-postmortem.md) | 深研究真跑复盘：skill 装载/完整研究流水线/崩溃检测/材料保全实证 + 守卫落地（framework_error 人话终态）；递归上限经 per-call 缝（非 AppConfig）——已记 known-limitation 待修 |
| CLS-009 | 2026-10-04 | [2026-10-04-queued-triple.md](2026-10-04-queued-triple.md) | 三连击全落地：① land-final-report（报告经 hold point 落 final/，真跑实证 ledger admit）② refine-slim-restart（新线程+机械摘要+lineage，机制实证；一次完成如实界定为非保证）③ ci-integration-lane（setup-uv + make smoke，声明三件套同步，UNVERIFIED-until-push） |
| CLS-010 | 2026-10-04 | [2026-10-04-test-doctrine-borrows.md](2026-10-04-test-doctrine-borrows.md) | 测试战略采纳路线图（v3 全量版）：十篇 digest 逐篇消化的长期参照与触发条件表 （文件先期移入，账本行此次补记——迁移时漏登） |
| CLS-011 | 2026-10-04 | [2026-10-04-agent-playbook-and-minimal-release.md](2026-10-04-agent-playbook-and-minimal-release.md) | agent 启动面 + 最小发布面全落地（ratify-agent-playbook-and-minimal-release 归档：COMMANDS 菜单+playbook/ 两层、发布面两件套、冷启动守卫红先绿后、全动词旅程回执） |
| CLS-012 | 2026-10-04 | [2026-10-04-fresh-agent-doc-cleanup.md](2026-10-04-fresh-agent-doc-cleanup.md) | fresh agent 全库文档审计（40 条发现）：catch-up-doc-truthfulness + remove-requirement-id-tracking 两 change 归档（narrative catch-up + 两条红先绿后守卫 + req 追踪体系退役）；A11/B4/agents 空层三项规范语义留待各自 change（B11 lane 装置已由 land-proof-lane-registry 落地拆除） |
| CLS-013 | 2026-10-04 | [2026-10-04-doc-hygiene-second-sweep.md](2026-10-04-doc-hygiene-second-sweep.md) | 第二轮文档卫生审计 26 条全处置：账本 ritual 修正直落（B2-B5/A4）+ 同名 change 归档（19 条声明层修复；A5/C2/C3 与计数钉死形态 defer 给操作者与后续治理 change；依赖方向守卫新抓三处跨树链接即改即绿） |
| CLS-014 | 2026-10-06 | [2026-10-05-runtime-test-interaction-architecture.md](2026-10-05-runtime-test-interaction-architecture.md) | Runtime/Test/Interaction/AgentLoop 结构与控制面重整主计划：Phase 0–4 五 change 归档 + Phase 5 八项裁决收官（三项落地、五项维持现状已记录）；2026-10-06 §8 验收清单正式执行全勾（verify/smoke/7 checker/git 检查全 0，11c29fe）；assembly/execution 采有原则退让（entry.py/run_engine.py 平铺，单文件不满足建目录原则）；后续结构维护由应用 docs/README.md 的地图维护触发条件承接（CLS-015） |
| CLS-015 | 2026-10-06 | [2026-10-05-agent-friendly-repository-map.md](2026-10-05-agent-friendly-repository-map.md) | Agent-friendly Repo 持续整理维护卡：两轮结构整理落地（clarify-application-surfaces + relocate-runs-and-clarify-structure）；触发表由 docs/README.md "地图维护触发条件"节吸收，活跃队列不再留常驻卡（回执 json 随卡归档） |
| CLS-016 | 2026-10-07 | [2026-10-07-plan-review-gate.md](2026-10-07-plan-review-gate.md) | 计划确认闸门：agent 交计划、操作者审改确认后开跑；plan-review-gate 落地后真梯演示暴露检测缺陷（报告被误当计划），plan-marker-detection 以内容标记修复并固化回归；交互反问先行落地为 interactive-clarification |
| CLS-018 | 2026-10-09 | [2026-10-07-clarification-channel-discipline.md](2026-10-07-clarification-channel-discipline.md) | 反问/计划通道纪律：吸收反问记 journal clarification_absorbed（5128f695 静默吸收黑洞消除，纯谓词与未答谓词对称）+ 计划框架消息通道纪律措辞（提问轮只带 ask_clarification、计划确认只走标记）；真梯自驱动验收全绿（标记遵从/走私消失/预算 0/2/journal 完整），自驱动替代真人 TTY 已登记 Deviation Register |
| CLS-017 | 2026-10-08 | [2026-10-08-application-corpus-adoption.md](2026-10-08-application-corpus-adoption.md) | 应用开发语料吸收主卡：C1 闭环地图 + C2 权威三件套（Deviation Register/Delivery Record 常设段+CHA-001 守卫）+ C3 钉定纪律与语料入库（38 文件）+ C6 第一批（C 回放物化/A 来源可溯机器/B 结构契约准入+hash_mismatch 退役+spec sync）+ C4/C5 小件，八 change 全归档；E/F 立项才动、G 显式不做 |
| CLS-019 | 2026-10-09 | [2026-10-09-backlog-governance-reborrow.md](2026-10-09-backlog-governance-reborrow.md) | _backlog 治理反向借鉴（同源制度下游增量回流）：plans→issues、_done→_archived、_closed_plans→_settled_issues 三层更名 + 关闭条件四态表 + 户口/状态词表 + triggers.md 活触发器索引（8 行种子）+ methods/ 方法库（7 篇，apply 中翻案采纳）+ checker 户口/滞留门禁（prove-it-red 1→0）；两条 apply 中翻案（methods、_archived）均登记；新门禁下第一张完整生命周期卡 |

**Next available plan ID: CLS-020**
