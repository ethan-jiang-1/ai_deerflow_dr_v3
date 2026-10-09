# Plan: doc-hygiene-second-sweep（第二轮文档卫生审计）

> 类型: 分析 | 更新: 2026-10-04
> 触发: 用户要求第二轮 fresh-agent 视角卫生复审（① 渐进披露是否不多不少、② 信噪比与概念相左），审计结论入账并 review 卡片质量。上一轮 = CLS-012 fresh-agent-doc-cleanup（40 条，已由 catch-up-doc-truthfulness 等消费）。

## 背景 / 现状

**审计方式**：本体走读 agent chain 与 task execution chain 全部入口 + 三路并行 fresh-context 审计（链接完整性 38 文件 / `_backlog`+openspec 账本 / harness docs 信噪比）+ 实测回执（`make verify` exit 0 / 112 tests / 0.14s；`check_doc_hygiene.py` exit 0；`check_project_architecture.py` exit 0）。所有行号对准 HEAD `6458c2d`。

**核心诊断（一句话）**：上轮打扫是有效的——0 断链、账本三处全绿、守卫内重复零漂移、112-test 精确吻合——但暴露出**两个复发机制**与一批上轮范围外的新病灶：

1. **内联计数无守卫，每次 archive 自动过时**：根 README 计数恰由上轮 catch-up change 亲手写对（9/29），随后两个 change 归档即再漂移（实际 11/31）——"29"现不属于任何一套簿记体系（CLS=12、changes=31）。
2. **账本"补记"动作绕过 ritual 表格结构**：CLS-012 行被追加在 plans/README 卡片模板代码块之后（B3），_closed_plans 表格再次被补记空行截断（B5，上轮 C7 修过）——checker 校验"在场"不校验"位置"，补记是复发入口。

**对用户两问的直接回答**：① fresh agent 链清晰、渐进披露纪律真执行（change-guidance 六文件合计 259 行、38 文件 0 断链、预算棘轮在跑；执行链由 config.yaml rules + closeout gate + 技能闭合）；偏差集中在三个"少了/多了"点（A8 悬空 first-read、27 行 LLM-Node 门的步骤 2-4 今天无 referent、governance 导航漏真实组件）。② 信噪比骨架健康；噪音 = 26 条下表（A 矛盾 8 · B 过期/断裂 10 · C 复述/沉积 8）。

## 决策 / 方案

三条处置动作（沿上轮）：**删**（过时从句，预算只降不升）、**改**（改写为现实真话）、**指**（死链改指现处）。本轮新增第四条——**防复发**（否则第三轮还会捡到同样的东西）：

- **计数指针化**：常驻/入口文件里的 specs 数、change 归档数、测试数一律不再内联数字，改"指向可数处"的一句话（如"能力清单见 openspec/specs/，归档见 changes/archive/"）；或由 checker 把计数钉死。二选一属规范语义，REVIEW 拍板。
- **账本补记走表格**：补记/追加行必须落在所属表格内（B3/B5 的根因）；若采纳，`check_doc_hygiene` 规则 7 加"行位置"校验——属 checker 语义改动，另立 change。

## 问题清单（REVIEW 用，共 26 条：A 级 8 · B 级 10 · C 级 8）

严重度：**A** = 矛盾/误导，fresh agent 会得出错误结论或走错路；**B** = 过期 / 死链 / 结构断裂；**C** = 复述 / 沉积 / 格式。带 ⏮ = 上轮修过或同族的复发/残留。

### A 级矛盾（8 条）

| # | 位置 | 问题 | 处置 |
|---|------|------|------|
| A1 ⏮ | `openspec/governance/README.md:31-43` | 六组件命令块含 check_release_face.py（非组件），真第六组件 check_proof_receipts.py 全 README 未导航；实测 `CHECKER_NAMES` = specs/architecture/change_guidance/harness_dep/ci_governance/**proof_receipts**。上轮 A10 修了计数（"6"），枚举仍错——同族复发 | 命令块列真实六组件；release_face 归 standalone 段；"何时读"表补 proof_receipts、selected-change-closeout、kernel、export 行 |
| A2 ⏮ | `README.md:19` | "9 个能力、29 个 changes 归档" vs 实测 11/31；该数字恰由上轮 catch-up 写对、随后两次归档即再漂移（见诊断 1） | 计数指针化或 checker 钉死（REVIEW 拍板）；短期先改对 |
| A3 | `deep_research_harness/docs/known-limitations.md:3-4` vs 表内 :9-14 | 自称只记"**存续中的**限制"，6 行中 2 行已修、1 行已解决划线、2 行是已落地守卫（:9 与 :14）——5/6 已处置，真正存续仅 :13 待诊断一行（:12 尾存留告诫）——半本处置台账 | 拆"存续"与"已处置"；已处置行收缩为指针 |
| A4 | `_backlog/_done/README.md:47` | "三套搬迁 ritual（todo / bug / plan）" vs `_backlog/README.md:44` 两类铁律（"不再增加类别"）——v2"todo"化石 | 改"两套" |
| A5 | "profile" 一词两义 | 根 `profiles/`（本地运行配置）vs `openspec/change-guidance/profiles/`（政策 profile）；根 AGENTS 路由行与根 README 各指一个；CONTEXT-MAP 未消歧（harness CONTEXT.md 对 "Gate" 双义有消歧先例，机制存在未用） | 词汇登记进 CONTEXT 层（规范语义，REVIEW 拍板归属哪层） |
| A6 | `deep_research_harness/AGENTS.md:4` vs :100-115 | "应用不依赖治理框架" vs 同文结构权威/生成块重渲染在 openspec 治理——各自为真（运行时独立 ≠ 结构被治理），并置无消解 | :4 加半句消解（"运行时不依赖；结构契约由治理拥有"） |
| A7 | `deep_research_harness/AGENTS.md:5-6` vs :42-45 | "不 source-browse deerflow" vs 门步骤 3 "inspect the exact builder"（builder 只在框架内），缺"何时不算 ordinary"判据；实例：known-limitations:11 裸 `client.py:293` 实指上游文件（见 B7） | 加一句判据；裸引用一律限定上游路径 |
| A8 ⏮ | `deep_research_harness/AGENTS.md:59` | "first read: owning contract in agents/" 悬空——agents/ 仅 31 字节骨架；同文 :63-64 自认契约"随代码落地才有" | first-read 加"（空，落地前走框架配置）"标注 |

### B 级过期 / 死链 / 断裂（10 条）

| # | 位置 | 问题 | 处置 |
|---|------|------|------|
| B1 | 根 `AGENTS.md:7` | 层描述列 `scripts`——`deep_research_harness/scripts/` 不存在（常驻文件、最高负载处） | 删"、`scripts`"（净减字符） |
| B2 | `_backlog/_done/_suspended_bugs/README.md:9` | 指向 `_fixed_bugs/README.md` 的 "Suspended" 段不存在（死胡同） | 改指或删 |
| B3 ⏮ | `_backlog/plans/README.md:70` | CLS-012 归档行游离在卡片模板代码块（:53-69）之后，脱离 :31-45 归档表——按表读必漏 | 移入表格（账本 ritual 修正，不进 change） |
| B4 | `_backlog/README.md:3` | 头部"最后更新"停在 CLS-011，未反映 CLS-012（plans/_done 两侧头部均已到 012） | 补记（账本 ritual 修正） |
| B5 ⏮ | `_backlog/_done/_closed_plans/README.md:29-38` | 空行把表格切成多段（CLS-007..012 行渲染破碎；004..006 在完整段内）——上轮 C7 修过，"补记"动作复发 | 删空行（账本 ritual 修正） |
| B6 | `COMMANDS.md:5`（ENS-001）/ `docs/quality-register.md:1`（RT10）/ `playbook/run-research.md:43`（RLF-001） | 退役需求 ID 惯性引用：remove-requirement-id-tracking 后 main specs 已不可解析（该 change 明确留作 inert history，已披露残留） | 保留则标注指向归档 change；或删 |
| B7 | `docs/known-limitations.md:11` + `src/.../runtime/client.py:18` 注释 | 裸 `client.py:293`：harness 自己的 client.py 仅 132 行；实指上游 `deerflow/backend/packages/harness/deerflow/client.py:293`（已核实该行存在 `recursion_limit=overrides.get(...)`） | 限定为上游完整路径 |
| B8 | `README.md:35` | "根目录居民 `config.yaml`、`.env`"两者均不存在（gitignored 待备）；且 config.yaml 与实存的 `openspec/config.yaml`（另一物）重名 | 改"按需准备"措辞；点名区分 |
| B9 ⏮ | `openspec/change-guidance/local/deep-research.md:12-19` | "Context Expansion Gate" 段被 `## Context And Seams` 标题拦腰截断，同一句"start from domain/…engine/…agents/"重复两遍——经 git 归因证实（a30d1c1）为上轮口号收敛编辑进行到一半、停在逗号 | 修复段落结构、去重 |
| B10 ⏮ | `deep_research_harness/README.md:45` | 行内仍逐字保留 "+ the boundary plan above"（全文件唯一 boundary 提及，上方并无此物——上轮 B2 只清了根 README 的同款短语，此处漏网）；且 "v3 direction note" 链接标签在目标 AGENTS.md 无对应文件/章节 | 删悬空短语；改标签为实际内容（AGENTS.md 引言段） |

### C 级复述 / 沉积 / 格式（8 条）

| # | 位置 | 问题 | 处置 |
|---|------|------|------|
| C1 | `Makefile` 头注释 / harness `AGENTS.md:93-98` / `COMMANDS.md:26,31` / harness `README.md:31` / `local-operations.md:10` / `testing-and-evaluation.md:13` / `quality-register.md:14` / `playbook:11-17` | `make verify` 语义 ×8 变体；守卫面（COMMANDS↔Makefile↔cli）外 5 处为裸复述，"不读 OpenSpec"四处近逐字 | COMMANDS 为语义 owner，其余收缩为一词 + 指针 |
| C2 | `node-agent.md:10-31` ↔ `harness AGENTS.md:36-53` | 六步 LLM-Node 门近逐字双写，各自宣称 complete contract（portable / application-owned），步骤 2、6 措辞已分叉 | 权威关系裁决（REVIEW 拍板）：机器钉一致，或显式声明"允许分叉、harness 版为应用权威" |
| C3 | harness README Reading Map ↔ harness AGENTS Information Map ↔ docs/README.md 索引 | 三张路由表覆盖同一文档集（Reader Roles 有分工声明，属刻意，但实测行集合几乎相同，是维护税） | 收缩重叠行或显式接受为 docs-as-contract（REVIEW 定） |
| C4 | `docs/local-operations.md:13-20` ↔ `playbook:61-66` | 坑双写近逐字（3/4 条相同）；local-operations 自称"坑详见 playbook"却自持清单——"只缓存 environment 招供不了的细节"自我定位未守住 | 一处持有（playbook），另一处指针 |
| C5 | 根 `README.md` / 根 `AGENTS.md` / `_backlog/README.md:19` / harness `README.md:7-10` / harness `AGENTS.md:8-10` | v3 哲学叙事 ×5 处叙述性重复（各自措辞略异，漂移敞口） | 正身留一处（根 README），其余一句 + 指针 |
| C6 | `docs/testing-and-evaluation.md:18-25` | 自称"四级谱系"的替身阶梯表出现两个"级 3"（:24 与 :25） | 修编号（行为断言应为级 4） |
| C7 | `testing-and-evaluation.md:37-42` / `playbook:77-90` / known-limitations 数字段 | 已收口历史仍全量展开：借鉴队列（自称已收口）、历史回执、事故考古数字（23→86→209、144K vs 192K） | 收缩为一行指针，细节归归档 change/plan |
| C8 | `.pi/tasks/<uuid>` + `governance/README.md` "何时读"表 | 无文档提及的 untracked 空目录；"何时读"漏收 4 个治理文件（与 A1 同修） | 删目录；补导航行 |

### 明确不是问题的（避免过度打扫）

- 相对 Markdown 链接 0 断链（38 文件逐一按所在文件解析）；账本编号/索引/计数三处全绿且被 checker 规则 7 机械化。
- 112-test 与宣称精确吻合（unit 恰 112，integration 另 9 与 smoke 回执吻合）；GENERATED 结构块与 registry 零漂移。
- 守卫内重复（command-surface-guard 三处、DECLARED_MACHINES↔quality-register、verify sentinel 逐字）是 docs-as-contract，保留不清。
- `agents/` 空层陈述本身诚实（AGENTS.md:10 准确）；"Gate" 双义已被 harness CONTEXT.md 正确消歧——是 A5 该抄的作业，不是问题。
- `deerflow/` 只读边界、harness 不回链治理框架的单向引用纪律，文件层面真实成立。

## 风险 / 取舍

1. **三个常驻文件零余量**（check_doc_hygiene DOC_BUDGETS 实测）：根 `AGENTS.md` 2435/2435、`deep_research_harness/AGENTS.md` 6864/6864、`openspec/config.yaml` 11436/11436。凡动这三处（B1、A6-A8、C2 相关行）必须**净减少或先删后加、逐字计数**，每步跑 `python3 openspec/governance/check_doc_hygiene.py` 看红绿。
2. **规范语义裁决项（按铁律 5 由人拍板，本 plan 只呈报）**：A2（计数指针化 vs checker 钉死）、A5（profile 登记进哪层 CONTEXT）、A3（known-limitations 拆分形态）、A7（"非 ordinary work"判据措辞）、C2（六步门双写的权威关系）、C3（三张路由表去留）。
3. **修文档 ≠ 改行为**：防复发装置（计数回写/指针化、账本行位置校验）动 checker 语义或 ritual 语义，越界进 change 领地，另立 change；本 plan 只立方向。
4. **行号时效**：全部行号对准 HEAD `6458c2d`，处置前逐条复核（账本在上轮归档后仍在动）。

## 落地关联

- **账本修正（B2-B5）**按 `_backlog` ritual 直接修三处 README，不进 change（沿 CLS-012 先例）。
- **建议 change `doc-hygiene-second-sweep`**：A1-A4、A6-A8、B1、B6-B10、C1、C4-C8（openspec 侧 A1/B9 可与根/harness 侧拆两个——B6 的三处位置均在 harness 层——按"一次放行一把"由 REVIEW 定）。红绿判据 = `check_doc_hygiene.py` + `check_release_face.py` + `make verify` 全 exit 0，A 级条目逐条前后对照。
- **防复发装置**（计数指针化/回写、账本补记位置校验入规则 7）另立治理 change，属 checker 语义，REVIEW 拍板后立项。
- **实施顺序**：账本修正（零风险）→ 根层 → harness 层 → openspec 层 → 常驻三文件最后做（预算最紧）→ 每层收尾跑 checker。
