# Plan: 借鉴 DSH Harness 思想——开发/产品双 harness 差距分析

> 类型: 分析 | 更新: 2026-10-02

## 背景 / 现状

用户要求把外部整理材料「 borrowing DSH harness idea」的结论搬进本仓库账本。源材料：
`/Users/bowhead/deepseek-harness/_faq_on_digested/07_borrowing-dsh-harness-idea/`（17 个文件，
question/answer + 道五篇 + 落地总纲 + 术七篇；**本机路径，不在本仓库**——本 plan 自包含其结论，
不依赖该路径可达）。

**DSH = DeepSeek Harness**（`deepseek-ai/deepseek-harness`）——「一切皆插件」的 agent harness。
FAQ 的核心结论压缩为三条立场 + 一条反转：

1. **agent 是一等参与者**：知识外置成可发现的入口，不靠口口相传。
2. **规则是可执行的代码**：可机械检查的承诺接 `exit non-zero` 命令；*Agents follow enforced
   gates far more reliably than prose conventions*。
3. **每类事实有唯一 owner**：一处一个权威，不重复、不漂移；负知识（「为什么不走某条路」）
   也有 owner。
4. 反转：不赌「更聪明的模型」，赌**成本结构**——正确路径阻力最小、错误路径早撞机器。

**适用框架：本仓库有两个 harness，借鉴分层适用，不混谈**：

| 层 | 是什么 | FAQ 适用度 |
|----|--------|-----------|
| 开发 harness | 让 coding agent 在本 repo 不糊涂/不乱发挥的一切（AGENTS.md 入口链、openspec 治理、_backlog 账本、checker 门禁） | 直接适用（FAQ 的「普通项目」即指此层） |
| 产品 harness | 要写的 `deep_research_harness/`——套在 DeerFlow 原生 deep research 外的运行/控制底座 | 思想适用、形态不适用（执行链/披露/隔离 → Run Bundle/gate/ledger 设计） |

## 十维评估结论（2026-10-02，基于全仓通读）

已经达标或超出 DSH 水准、**不需要动**的：

| 维度 | 现状证据 | 相对 DSH |
|------|---------|----------|
| 归属 | 根 `AGENTS.md` 57 行纯路由；`CLAUDE.md` 经 `@AGENTS.md` 导入零复制；`CONTEXT-MAP.md` 有 fresh agent 阅读次序 | ✅ 达标，阅读次序比 DSH 显式 |
| 正确路径 | `deep_research_harness/AGENTS.md` Application Focus 表（目标→owner→升级条件）= DSH 归属表等价物；LLM-Node Authoring Gate 六步路由；`utils/helpers/common` 禁区接进 `check_project_architecture.py` | ✅ **最亮眼一维**，表+gate 成对 |
| 反馈之一 | 6 component checker + 聚合 gate；退出码直测纪律（governance README）；`check_doc_hygiene --self-test` 负例控制；`test_project_gate.py` 有真实「能变红」断言 | ✅ 负例控制已实践 |
| 反馈之二 | `check_proof_receipts.py`：runner 产出回执、退出码、revision diff 为空、transcript digest 匹配 | ✅ 超出（DSH "verify the world, not the self-report" 的更细产品化） |
| 术语纪律 | ACTIVE_TERMINOLOGY_RULES 禁临时措辞冒充当前事实（"skeleton"/"later wave"…） | ✅ 超出（DSH「Document current state」的机器化，DSH 自身无此层） |
| 决策记录状态机 | `_backlog` 的 `_suspended_plans/`（暂停≠完成，保留重启条件）比 DSH 四态多一个诚实状态；`git mv` 即状态 + 三处 README 联动 | ✅ 达标 |

十维打分：变更闭环 7 · 归属 9 · 决策记录 7 · 静与动 7 · 正确路径 9 · 入口链 8 · 执行链 6 ·
反馈 8 · Skills 7 · 披露 5（骨架期合理）。

## 决策 / 方案：开发 harness 的六个缺口（按收益/成本排序）

### A. 规则没接进「接受路径」——没有 CI、没有 hook ⭐ 最优先

DSH 立场 2 的完整句：*Every mechanically checkable AGENTS.md promise gets a command that
exits non-zero. **CI invokes the exhaustive set**, while Git hooks reserve their latency
budget for cheap local defects.* 我们做到了前半（checker 体系），缺后半：

- `.github/workflows/` 不存在，`.git/hooks` 为空；
- 六 checker + 聚合 gate 只活在 `openspec/config.yaml` 的 tasks 规则里——「归档前必须跑
  closeout gate」是写给 agent 的 prose convention，不是错误时刻会拦人的 enforced gate。

**动作**（不必等实现期）：
1. 最小 CI workflow：`check_project_gate.py --phase closeout` + `openspec validate <change> --strict`
   + harness `make verify`。无跨平台矩阵诉求，单 job 即够；穷举归 CI。
2. pre-commit 等价物（pre-commit framework 或 lefthook）：只放便宜高置信项——`git diff --check`、
   staged ruff、doc hygiene。**hook 不是小号 CI**：测试、快照、类型分析明文禁止进 hook
   （DSH 纪律：hook 是便宜高置信缺陷的快反馈层，随 diff 变化面大的检查一律不进）。

### B. 负知识没有 owner

openspec `specs/` 只收正知识；`changes/archive/` 是历史；`_suspended_plans/` 只覆盖「暂停待重启」。
「评估过并否决的方案」「已知限制」散落在 plan 的风险/取舍节，plan close 后沉入 `_done/`，
检索路径变长。失效形态：新会话 agent 把明确缺席当遗漏，反复提出已否决方案。

**动作**（二选一或并行）：
1. change 的 design 增 `## Alternatives` 惯例（OpenSpec 原生位），并在
   `openspec/change-guidance/core/change-practice.md` 把它从建议升为「有真实备选被放弃时必填」；
2. `deep_research_harness/docs/README.md` 文档表预留 `known-limitations.md` 位（随首个 change
   建档），索引声明「负知识的家在这」。

顺带补 **豁免判据**（抄 DSH 原话进 change-practice.md）：机械/局部修改免写决策记录；
*diff 大小不是豁免理由，没有持久取舍才是*。防两个方向的走形：机械建档 / 该记不记。

### C. 常驻层没有预算闸

`check_doc_hygiene.py` 管链接/编码/结构，不管体积。膨胀风险点：
- `openspec/config.yaml` 的 `context` + `rules` 已是高密度长文，是每次进 OpenSpec 流程的
  事实常驻注入层；部分 rule（如 tasks 的归档前清单）内容已有 owning checker/policy 拥有，
  rules 里在**复述**——one-home 原则的反面苗头。
- 根 `AGENTS.md` 目前 57 行克制，但无机制阻止膨胀。

**动作**：FAQ 结论「数值不迁移，门禁迁移」——给入口链文件（根 AGENTS.md、
`deep_research_harness/AGENTS.md`、`openspec/config.yaml`）设行数/字节上限，接进
check_doc_hygiene 或独立 checker（保持 Python 标准库风格）；上限只降不升，上涨须在 change
里论证。中文按字符数计（`wc -w` 对中文虚松一个数量级）。config.yaml rules 的收窄
（一行契约 + 指回 owning policy）是 OpenSpec 机器读契约，动它走治理 change，先挂账。

### D. 「Do not add nested AGENTS.md」没写理由（违反本仓规矩 #4：刻意分歧就地写明）

`deep_research_harness/AGENTS.md` Boundaries 全禁嵌套 AGENTS.md，比 DSH 通则（有子树专属
常驻规则时才放、宁少勿多）更严。可能是对的，但缺理由 + 升级条件。

**动作**：一行成本。补一句理由（防「为放而放」）+ 升级条件（例：某子层积累 ≥3 条只有该层
需要的常驻规则时，重新评估放子树入口）。

### E. 垂直切片未正式跑过（FAQ Phase 1 第二步）

boundary plan 的「治理门禁干跑全绿」是预演；正式切片 = 拿一笔真实变更按闭环五行走查：
意图可观察结果写得出吗 / 不靠作者本人能找到 owner 吗 / 持久取舍记在哪 / 哪项证据会在旧行为上
变红（红灯对照）/ 逐步标注证据状态。

**动作**：change ①（project-structure 转正）落地时，把五行走查写进其 closeout 任务，产出
「打不开的链接 / 要靠猜的 owner / 没有证据的声称」三清单——比任何通用优先级都准。

### F. 决策记录的取代纪律可预置（小）

在开始量产 change 前写进 change-practice.md：决定反转时**新增记录并交叉链接，不原地改写**；
完全取代前**先吸收旧记录的全部独有内容**（理由/备选/后果/验证缺口）。骨架期成本低，
到 v2 规模（57 spec）再补就晚了。

## 产品 harness 的设计映射（供 change ②/④ design 直接引用）

| DSH 思想 | 产品落点 |
|----------|---------|
| **执行链三环节**：动作先记录再执行 / 策略统一收口 / 结果单一出口 | Run Bundle event journal = 事实源：lead agent 的每次 skill 调用、subagent 委派、候选产出**先 append 进 Bundle 才算发生**（失败也在场）——DSH「模型可见 ⟺ 落日志」的研究场景翻译，即 v2「模型提议、代码裁决」的表述基础。**建议升格为产品 harness 第一 invariant 候选**（契约测试钉「每个 admitted effect 都能在 journal 找到先于它的调用记录」） |
| **策略在工具体之外**（pre-execute waterfall；策略散 N 处是反模式） | boundary plan 问题 2（gate 插桩点选型 a/b/c/d）：判定逻辑收在**一个**确定性收口。自查判据：「加一条准入规则要改几个文件？答案应该是一」 |
| **静与动四层**：两处存真才是事故 | boundary plan 问题 3（Bundle vs DeerFlow checkpointer/persistence）：**最容易踩的警告点**。须显式声明谁是权威。倾向：Bundle 拥有业务级 run 事实；框架 checkpointer 是派生/缓存层，丢了可重建（DSH 检验法：丢了不心疼的就不是事实源） |
| **可见集收缩 ≠ 授权边界** | 控制 subagent 类型声明与预算参数时：限制委派类型影响的是**模型选择空间**；真正授权在 DeerFlow sandbox/approval 层，两者不互相冒充 |
| **compaction 保留 tool-call/result 配对**；spawn 不带父历史 | Bundle 回放/事件裁剪的硬约束：裁剪不拆散一次委派的调用与结果对；subagent 事件落 Bundle 天然隔离父上下文（DeerFlow 委派机制已给一半，Bundle 如实记录即可） |

## 不要照搬（逐条核对过）

- **插件图 / capability seam 全家桶**：DeerFlow 已是宿主，不再造一层组合架构。
- **双语三件套 / hash 配对**：非双语平等项目。替身警惕：根 AGENTS.md（中文）与
  `deep_research_harness/AGENTS.md`（英文）是**分层**不是复述，保持分界即可；
  config.yaml 中英混排是轻微风险点，留意识不上机器。
- **自建 host 的披露管线**（注入预算/compaction/inspect）：运行时宿主是 DeerFlow 不是自建
  agent loop；开发侧披露由 Claude Code/Codex 宿主负责。层 1（静态组织）已做完，
  层 2–5 按压力逐项加，可无限期推迟。
- **DSH 的加权批准 / Project 制度**：协作规模不匹配。

## 风险 / 取舍

- [治理 gate 只在归档时被 agent 自觉执行，proxy 可信度依赖自觉] → 动作 A 的 CI/hook 直接消除；CI 未落地前，把「gate 退出码直测回执」继续作为 closeout 硬任务（现状已有）。
- [config.yaml rules 与 owning checker/policy 复述、中英混杂] → 不立即动（机器读契约，改动走治理 change）；先由动作 C 的预算闸止胀，收窄挂账。
- [负知识落点若两处都建（Alternatives + known-limitations）会双家] → 动作 B 二选一为主：process 层用 Alternatives（跟 change 走），产品层 known-limitations 只收「当前已知限制」不收历史否决——各自 owner 不重叠。
- [本 plan 结论基于 2026-10-02 全仓通读，repo 演进后十维分数会漂] → 本 plan 是快照；每次 major 治理 change 后回到十维表复测（FAQ Phase 8 的复测纪律），复测记录追加在本 plan 末尾而非改写历史。

## 落地关联

候选 change 挂载（与 boundary plan 的 ①–④ 候选顺序合并排布， governance 项可并行插队）：

| 缺口 | 挂载点 | 时机 |
|------|--------|------|
| A（CI + hook） | 独立治理 change（建议紧随 change ①，或并入） | 最早 |
| E（垂直切片） | change ① 的 closeout 任务 | change ① 落地时 |
| B/F（负知识 owner + 取代纪律 + 豁免判据） | change-practice.md 的 owning 治理 change | 与 A 同批或紧随 |
| C（入口预算闸） | check_doc_hygiene 的 owning 治理 change | A 之后 |
| D（补理由一行） | 任意触碰 `deep_research_harness/AGENTS.md` 的 change 顺带 | 下次触碰时 |
| 产品映射表 | change ②（run-bundle 合同）与 ④（接线）的 design 输入 | 对应 change 启动时 |

结论被上述 change 吸收后，本 plan 关闭，`git mv` 至 `_done/_closed_plans/`。

## E 项落地记录：change ① 垂直切片五行走查（2026-10-02，closeout 时点）

以 establish-project-structure 为首笔走完整闭环的真实变更，按 FAQ Phase 1 第二步行查：

| 问 | 答案 | 证据状态 |
|----|------|---------|
| (a) 用户可观察结果（两行） | closeout 聚合门禁 exit 0（此前三红同根：reqs/architecture/req_coverage 全指向 PRS-001 无 owning spec）；`openspec list --specs` 报告 project-structure 有 owning main spec | 文件可指：gate 回执 + specs/ 目录 |
| (b) 不靠作者本人能找到 owner 吗 | 能：三红 checker 在 gate 输出里**自报名字**（自诊断）；根 AGENTS.md → governance README「何时读」表 → registry/manifest/checker，三跳定位，零猜测 | 链路各文件可指 |
| (c) 持久取舍记在哪、哪些豁免 | design.md 决策 1–6（尤其决策 6：apply 期手工建 main spec，因 native archive 丢 `> req:`/`> structure:` 头行——/tmp 三配置实验回执）；注解本身无持久取舍，按豁免判据免记 | design.md 可指 |
| (d) 哪项证据会在旧行为上变红 | 三红是本会话**实测的活回执**（change 目录建立前直测 exit 1）；治理测试套件含负例控制，证明 checker 能红 | 会话回执 + unittest 套件 |
| (e) 逐步证据状态 | 每步都是命令回执（退出码直测）或可指文件；无一步依赖口头声称 | tasks.md 各验证命令 |

**三清单**（切片产出）：

- **打不开的链接**：无——doc hygiene（链接校验）exit 0。
- **要靠猜的 owner**：无——但有一处**险情**：canonical policy 名是 `deerflow-downstream-boundary`，交接文档误记为 profile 名 `deerflow-downstream`；plan gate 的 `triggered_policy_unknown` 错误自报精确要求，机器纠正而非靠猜——「规则可执行」立场救了一命（B 项的又一实证）。
- **没证据的声称**：无——唯一非声称物是 `make verify` 响亮占位（自我声明"verifies NOTHING"，是诚实的非声称）。

**走查结论**：闭环走通；E 项完成。十维中「变更闭环」维从 7 升至 9（差 CI 未接，即 A 项）。
