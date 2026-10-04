# Plan: test-doctrine-borrows（测试思想借鉴——修订版，全对照）

> 类型: 设计 | 更新: 2026-10-04（v2 修订：应业主要求重新对照十篇 digest 全量盘查；v1 的两条队列太薄）
> 来源: digest `/Users/bowhead/deer-flow/_digest/test-strategy/`（10 篇）对照本仓现有资产逐域盘点。

## 背景 / 现状（诚实的自我审计）

先说已经对齐的（不是客套，是盘点结论）：离线确定性默认、真实边界显式 opt-in、负例控制、
门禁自测、真一切只换模型（smoke 即此形态）、契约镜像、fail-closed、known-limitations
成文——digest 思想篇的骨架我们已经在。**距离不在思想，在三层：机制件没建齐、纪律没
挂钩、规模没到。** 逐域对照如下（✓=已对齐；🟡=部分；✗=缺；⏸=规模门槛未到，有意不借）：

| digest 域 | 我们的现状 | 缺口 | 处置 |
|---|---|---|---|
| 00 全景地图 + 每层"不证明什么" | lane 表有，但缺"不证明什么"列 | ✗ 半缺 | B2（本轮落地） |
| 01 TDD 强制 + 负例 + 门禁自测 | ✓ 全在（红绿回执、gate 红证明、checker self-test） | — | 维持 |
| 01 设计文档自带 Testing Strategy（实现前成文） | 🟡 tasks 有红绿计划，无成文 Testing Strategy 节 | ✗ 半缺 | B1（约定入 change 指导） |
| 01 no-unpinned-invariant（规矩有钉子测试） | 🟡 质量注册处有同步测试；doctrine 文档本身未被钉 | ✗ 半缺 | B2 |
| 01 docs-as-contract（文档=交付物，一致性由测试执行） | ✗ COMMANDS.md/Makefile/cli.py 三处命令面无一致性测试 | ✗ | A4 |
| 01 指令链被测试钉死（28 个 AGENTS.md + guidance check） | ✗ 只有 doc-hygiene 管存在性，不管内容 | ✗ 半缺 | B2（先钉 lane 表与守卫清单） |
| 02 替身阶梯级 1（剧本模型） | ✓ ScriptedChatModel（含 raise 动作） | — | 维持 |
| 02 级 2 内容寻址录制回放 | ✗ 完全没有 | ✗ | A1+A2（最大借鉴项） |
| 02 归一化纪律（system prompt 剔出键等） | ✗（随 A2 落地） | ✗ | A2 |
| 02 "miss 响亮失败 + 清单断言"（中间件吞错防线） | 🟡 我们刚建了 fallback 标记守卫（同族问题不同解法） | 🟡 | A2 一并落 |
| 03 反 fake-green（真录制×真栈） | 🟡 smoke 是真栈+剧本；无真录制回放 | 🟡 | A1 |
| 03 真 SDK payload 钉住（第三方行为假设的钉子） | ✗ stream kwargs 的 per-call 语义刚踩过坑（recursion_limit），镜像未覆盖 stream 缝 | ✗ | A3 |
| 03 跨语言契约 JSON | n/a（无前端） | — | ⏸ |
| 04 部署配置即测试 / CI pinning CI / AGENTS.md 治理 | 🟡 checker trio 已是此模式；AGENTS.md 内容未钉 | 🟡 | B2 |
| 05 时长基线分片 | ✗ 90 测试未到规模 | ⏸ | 规模门槛 |
| 05 autouse 重置/monkeypatch 纪律 | ✓ unittest per-test 隔离已严格（temp dirs + cleanup） | — | 维持 |
| 07 崩溃模拟离线习语 | 🟡 死子进程 + 直构状态已在用；"同 store 重建 as-if-restarted"习语未成文 | 🟡 | B3 |
| 08 技能测试面（四测试面 + SkillScan + waiver） | ✗ 完全没接（技能定制的前置） | ✗ | A5 |
| 09 覆盖率门禁取舍 | ✓ 同取"无覆盖率门禁"立场 | — | 维持 |

（维护注：本表是活对照——digest 域 × 我方资产；每轮借鉴后更新状态列。）

## 决策 / 方案（分层借鉴队列）

**Tier A——机制件（各自一个 change，全管道）：**

- **A1 真实事件流回放 fixture**（最急，扁平 chunk bug 的永久疤）：把 EASA 真跑的
  事件流录成 fixture（诊断 dump 已有素材，重录一次完整版），回放穿过 run_research
  断言终态/journal 形状——**真实形状从此进回归**，fake 形状漂移不再可能静默。
- **A2 内容寻址回放模型**（digest 级 2，最贵证据变永久 fixture）：caller+归一化输入
  哈希索引；归一化剥日期/UUID/路径/系统提醒，system prompt 剔出键；miss 响亮清单；
  hermetic 配置恒等（录制与回放只差 models[].use）。录一次 EASA 简报真跑，此后
  报告落位/澄清/fallback 全部在真实形状上回归。
- **A3 stream 缝镜像扩展**：把 `recursion_limit`/`thread_id` 的 per-call 语义钉进
  契约测试（client.py:293 的缝——recursion 调试链的机械疤）。
- **A4 docs-as-contract 守卫**：COMMANDS.md ↔ Makefile targets ↔ cli.py 子命令
  三处一致性的机械测试（文档即交付物，漂移即红）。
- **A5 unit lane 网络守卫**（digest 自评缺口 #1 的预防性补齐）：unit gate 结构性
  禁外联（socket guard），防"写了真调用的测试 + 宿主机 key = 意外计费"。

**Tier B——纪律挂钩（文档/约定/轻测试）：**

- **B1** change 指导补一条：设计工件自带 Testing Strategy 节（实现前成文——digest
  01 §7 的模式，我们 Evidence seam 的强化版）。
- **B2** doctrine 文档钉住：lane 表的 make targets 必须在 Makefile 里存在、守卫清单
  必须与 machines.py 一致（后者已有）——把"文档即契约"落到我们自己头上。
- **B3** run engine 的"as-if-restarted"习语成文进 doctrine（同 store 重建、直构
  post-crash 状态——我们已在用，补成文与命名）。

**Tier C——规模门槛（有意不借，写明触发条件）：**

- 时长基线分片（测试数 >500）；Playwright 多车道（有前端时）；迁移契约（state
  schema v2 时）；monocle eval 栈（需要行为质量断言时）。

## 风险 / 取舍

- [Tier A 机制件总量不小] → 顺序即优先级：A1 最急（疤已结痂但有复利），A2 最重
  （归一化规则按证据长），A3/A4/A5 各自小；每把独立全管道，失败不连坐。
- [借鉴过度超前于规模] → Tier C 的门槛写明；Tier A 的每件都有真实触发事件
  （扁平 chunk、recursion 链、命令面三处、.digest 自评缺口）。
- [digest 基线漂移] → 借鉴引用带 digest 路径与版本锚；上游演进走 _upstream-sync。

## 落地关联

Tier A 五把 + Tier B 三条，按 A1 → A3 → A4 → A2 → A5 → B* 顺序入线（A1 疤最急、
A2 最重放中间、B 类轻尾）。全部落地后本 plan 关闭（CLS-010），doctrine 文档的借鉴
队列同步收口。
