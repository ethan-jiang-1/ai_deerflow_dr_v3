# Plan: 消化 DeerFlow v2.1.0 原生 Deep Research 能力，划定 v3 harness 边界

> 类型: 设计 | 更新: 2026-10-02

## 背景 / 现状

v3 骨架已立（本仓库）：`deep_research_harness/` + `deerflow/`（submodule 锁 `ceebf97f` = v2.1.0）+ `openspec/`（空壳）+ `_backlog/`（本账本）。命名与结构沿用 v2，**实现从零开始**。

方向性决策（用户拍板，2026-10-02）：v2 逐节点手搓研究图；v3 直接借力 DeerFlow v2.1.0 原生的 Deep Research 能力。原生能力的盘点见 [`../_reference/deerflow-native-deep-research.md`](../_reference/deerflow-native-deep-research.md)：框架侧没有固定研究图，deep research = `deep-research` skill（四阶段方法论）+ subagent 委派系统（可自定义类型、一层委派、框架级预算/并发治理）+ 宿主工具。

## 本 plan 要回答的问题

1. **harness 还剩什么职责？** 候选保留区（继承 v2 思想）：Run Bundle 生命周期（start/resume/status/cancel/refine）、确定性控制边界（validator / evidence ledger / gate）、显式组成（all_real / fixture / mixed，零凭据可跑）、可观察可操作（bundle 检查、事件日志、demo 阶梯）。哪些留、哪些砍、哪些改形态——本 plan 给出第一版清单。
2. **控制边界插在哪一层？** v2 的 gate/ledger 作用在静态图节点之间；v3 的研究过程是 lead agent 内的动态委派。候选插桩点：(a) skill 内容（软约束）；(b) subagent 类型声明与预算参数（配置约束）；(c) harness 自己的薄外层图（确定性编排）；(d) Gateway/工具层。需要按"模型提议、代码裁决"原则选位。
3. **Run Bundle 与框架 runtime 的关系？** 框架有自己的 persistence/checkpointer；harness 的 Bundle 是独立可删除的持久真相。两者的记录边界、恢复语义、谁拥有哪段状态，必须先定合同。
4. **v2 的哪些"血泪守则"必须带过来？** 候选：自证后才交回、证据高于感觉（新鲜回执）、fixture 隔离包、deerflow 只读边界 + 契约测试锚（`test_deerflow_public_api.py` 模式）、Gitlink 元数据校验。逐条判断"仍然适用 / 形态要变 / 不再需要"。

## 决策 / 方案

（2026-10-02 填实。证据底座：[原生能力盘点](../_reference/deerflow-native-deep-research.md)（事实层）
+ DSH 借鉴 plan 的产品映射表（设计检查单：执行链三环节 / 静与动四层 / 模型可见⟺落日志 /
可见集≠授权 / 事实源检验法）+ 框架只读指引。四问答案由 change ② 的 design 按吸收义务全量消化。）

### Q1 · harness 还剩什么职责？

**留（差异化核心，框架没有）**：Run Bundle 生命周期（独立可删除的持久真相）；确定性验收边界
（validator / evidence ledger / gate——「模型提议、代码裁决」）；显式组成（all_real / fixture /
mixed，零凭据可跑）；可观察可操作（bundle 检查、事件日志）。

**砍（交给框架原生）**：研究认知全部（deep-research skill 方法论 × subagent 委派）；静态研究图
（框架无固定图，v2 范式整体作废）；研究过程逐步控制——接受过程黑盒度上升（本 plan 风险节预判，
对策是 Bundle 侧验收而非过程插桩）。

**改形态**：v2 的 gate/ledger 作用在静态图节点之间 → v3 只承诺**提议进入 Bundle 前过确定性验收**
（研究结果、证据、报告候选 → 验收裁决 → admit / reject），过程内部不承诺每步可控。

### Q2 · 控制边界插在哪一层？

**分层组合 (b)+(c)，(a) 只作方法论补充，(d) 不用**：

- **(b) 事前约束（配置层，框架原生支持）**：harness 经 `CustomSubagentConfig` 声明自己的研究
  subagent 类型（工具白名单 / skills / max_turns / token_budget / 超时）+ 委派治理参数（并发、
  每 run 总数）。这是「可见集收缩」：控制研究子代理能看见什么、花多少——DSH 边界纪律：可见集
  影响选择空间，不是授权边界。
- **(c) 事后裁决 + 生命周期（harness 薄外层确定性图）**：run 的确定性生命周期由 harness 图驱动，
  认知整体委派给框架 agent（图里的认知节点）；确定性验收收口在图上**单一 admission owner**
  （DSH 判据自查：「加一条准入规则要改几个文件？答案是一」）。
- (a) skill 内容是软约束（纯提示词），不能承载确定性准入——只作后续可选的方法论增强。
- (d) Gateway/工具层插桩需要进程内 middleware/扩展，违背薄接线与不动框架铁律，不用。

### Q3 · Run Bundle 与框架 runtime 的关系？

用 DSH 事实源检验法分界（「丢了不心疼的不是事实源；两处存真才是事故」）：

| 层 | 拥有 | 检验 |
|----|------|------|
| **Bundle（事实源，唯一权威）** | 业务级 run 事实：生命周期状态、append-only 事件日志、admitted 证据与产出、验收记录 | 丢了心疼、不可重建；删除 Bundle = 该 run 永久不可得，harness 照常工作 |
| **框架 checkpointer/persistence（派生层）** | 认知过程中间态（对话历史、工具调用过程、thread state） | 对业务真相而言丢了可接受——已验收产出在 Bundle；过程回放是诊断便利 |

记录边界（「模型可见⟺落日志」的 Bundle 版）：**每个 admitted effect 必须能在 Bundle 事件日志里
找到先于它的记录**（候选 invariant 第一条，v2 「模型提议、代码裁决」的表述基础）。框架 trace
（X-Trace-Id）记录认知过程细节；Bundle 存 trace 引用做关联，**不复制过程内容**（一处事实一个
家）。恢复语义：进行中 run 的过程态由框架管（resume 委托给框架 thread），harness 只记录「resume
发生」与验收结果；框架 thread 丢失时进行中 run **降级为 failed-resume 并 fail loud 记入 Bundle**，
不静默假装继续。

### Q4 · v2 血泪守则逐条取舍

| 守则 | 判断 | 落点 |
|------|------|------|
| 自证后才交回、新鲜回执 | **仍然适用，已落地** | 本仓 AGENTS.md 不可谈判 #2/#3 + test-evidence-policy + proof receipts 机制 |
| fixture 隔离包（显式组成） | **仍然适用，形态收窄** | v2 逐节点 fixture → v3 降到组成面（整个 run 的 provider 层替换，fixture 适配器在 harness runtime 层）；随 change ③ |
| deerflow 只读边界 + 契约测试锚（CURRENT_DEERFLOW_PIN 模式） | **仍然适用，分两半** | gitlink 元数据校验已落地（PRS-001）；harness 侧契约测试锚（test_deerflow_public_api.py 模式）随 change ④ 建立——test_upstream_pin_agreement 已预留激活点 |
| Gitlink 元数据校验 | **已落地** | PRS-001 + 架构 checker + test_upstream_pin_agreement |

### 落地拆解确认

第一候选成立：**harness = 薄外层确定性图（(c)）+ Bundle 生命周期 + 确定性验收边界**，研究认知
全部交给框架。change ② 承载 Q1 的「留」清单与 Q3 的记录边界/恢复语义；change ③ 承载显式组成
（Q4 fixture 行）；change ④ 承载接线与契约测试锚（Q2 的 (b) 层参数随接线声明）。

## 风险 / 取舍

- [动态委派难以做确定性准入] → harness 边界只承诺"提议进入 Bundle 前过确定性验收"，不承诺研究过程每步可控；接受过程黑盒度上升。
- [框架能力随 upstream 演进漂移] → 沿用 v2 的双锚保护：`CURRENT_DEERFLOW_PIN` 契约测试 + governance gitlink 声明锁。
- [v2 的 gate/ledger 思想可能在动态范式下过重] → 第一版宁可薄：先 Bundle + 显式组成 + 最小验收门，其余等证据说话。
- [skill 是纯提示词，研究质量无硬保证] → 评测/校准资产（v2 的 cognitive-evaluation 思路）作为 v3 后续 capability 候选，不在第一版。

## 落地关联

结论成型后拆成 v3 的**首批 OpenSpec change**（候选顺序：① project-structure / 治理清单落地；② run-bundle 生命周期合同；③ 显式组成与 fixture 隔离；④ harness ↔ 原生能力接线）。change 命名与 requirement ID 从零分配，不沿用 v2 的 57 个 spec。

### HITL 闸门（用户拍板，2026-10-02，硬约束）

**任何由此 plan（或其衍生 plan）触发的 openspec propose 动作，之前必须经用户 review——
推敲清楚之前不进入 openspec pipeline。** 推敲产物按需衍生多份 `_backlog/plans/` 里的
plan（证据底座见 `_reference/` 六份调查材料），每份衍生 plan 各自成熟、各自经用户
拍板后才入线成 change。change ① 已于 2026-10-02 走完闭环（establish-project-structure）。

### Change ①（project-structure 转正）的实测清单（2026-10-02 干跑全绿验证）

在 /tmp 副本上按下列步骤做了一次完整干跑，治理门禁 7/7 全绿（exit 0）：

1. 新建 `openspec/specs/project-structure/spec.md`：`> req: PRS-001` 行 + 恰好一行
   `> structure: openspec/governance/project-structure.toml` + `### Requirement:` 与
   `#### Scenario:` 结构。
2. 在 owning 治理脚本（check_project_architecture.py）的模块 docstring 里加
   `@impl PRS-001`——req_coverage 要求每个治理 requirement 有脚本证据注解。
3. **术语红线**（check_project_specs 的 ACTIVE_TERMINOLOGY_RULES，扫描 specs +
   harness AGENTS/README + 未来 SKILL/SOUL）：禁止 "skeleton"、"change NNN"、
   "full-fake"、"later wave" 等历史性/临时性措辞。因此 harness 两份权威文档已改用
   "pre-implementation" 措辞；spec 正文同样不得出现。
4. `src_fixtures/` 空壳已从骨架撤下（manifest 声明 fixture 段即要求非空
   production_contracts，v3 尚无）；它随 change ③（显式组成）连目录带
   `[package].fixture_root` + `[fixture_imports]` 一并进入。
