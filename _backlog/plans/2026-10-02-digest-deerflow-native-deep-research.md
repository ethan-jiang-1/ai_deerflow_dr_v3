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

（待分析填入。第一候选倾向：harness = 薄外层确定性图 + Bundle 生命周期 + 确定性边界；研究认知全部交给 lead agent + skill + subagent。是否成立取决于问题 2 的插桩点论证。）

## 风险 / 取舍

- [动态委派难以做确定性准入] → harness 边界只承诺"提议进入 Bundle 前过确定性验收"，不承诺研究过程每步可控；接受过程黑盒度上升。
- [框架能力随 upstream 演进漂移] → 沿用 v2 的双锚保护：`CURRENT_DEERFLOW_PIN` 契约测试 + governance gitlink 声明锁。
- [v2 的 gate/ledger 思想可能在动态范式下过重] → 第一版宁可薄：先 Bundle + 显式组成 + 最小验收门，其余等证据说话。
- [skill 是纯提示词，研究质量无硬保证] → 评测/校准资产（v2 的 cognitive-evaluation 思路）作为 v3 后续 capability 候选，不在第一版。

## 落地关联

结论成型后拆成 v3 的**首批 OpenSpec change**（候选顺序：① project-structure / 治理清单落地；② run-bundle 生命周期合同；③ 显式组成与 fixture 隔离；④ harness ↔ 原生能力接线）。change 命名与 requirement ID 从零分配，不沿用 v2 的 57 个 spec。

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
