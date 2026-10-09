# Plan: fresh-agent-doc-cleanup（文档真理性大扫除）

> 类型: 分析 / 设计 | 更新: 2026-10-04
> 触发: 用户要求以 fresh agent 视角审计本仓库的 ① 渐进披露链是否清晰、② 整体信噪比与概念矛盾，并对问题清单做 REVIEW。

## 背景 / 现状

**审计方式**：三路并行 fresh-context 审计（root+_backlog / deep_research_harness / openspec）+ 本体走查与实测（`UV_OFFLINE=1 make verify` exit 0 / 112 tests；`check_doc_hygiene.py` exit 0；openspec 层断链 0、checker 计数实测核对）。所有行号对准 HEAD `9574298`。

**核心诊断（一句话）**：仓库早已从骨架毕业——specs 主干 9 个能力、28 个 changes 归档、六动词 CLI 落地、112-test 单元门禁在跑——但**骨架期的叙事还活着**：约 40 处常驻文件仍自称或暗示"骨架 / 占位 / 随 change 落地 / specs 为空"。这不是"文档太多"（harness 层 464 md 行 vs 4,564 py 行 ≈ 10%；openspec 活跃面 ~1,950 行；_backlog 活跃面约 324 行，体量都健康），而是**叙事落后于实现（narrative lag）**，且恰好集中在 fresh agent 最先读的那几百字里。openspec 层另有一个独有的病灶：**半落地的装置**（Delivery Lanes / proof-lanes 被写成已存在，实际一条命令都不在）。

**对用户两问的直接回答**：

1. **fresh agent 链清晰吗？** 结构上是好的——AGENTS.md Information Map 与 README Reading Map 互相一致、都路由到真实存在的文件；最好的文档是代码接线的单一权威（`quality-register.md`↔`engine/machines.py` 的 `DECLARED_MACHINES`、`COMMANDS.md`↔`Makefile`↔`cli.py` 由 command-surface-guard 机器守着）。但入口内容错误：fresh agent 读到的头几句话是"这是空骨架"，而真实状态是已实现核心；且存在第二条竞争入口链（CONTEXT-MAP 的 Reading order）会走进死胡同（见 A6、C1）。
2. **信噪比如何？** 总量健康、无大规模概念相左。最大噪音 = 过期真话（40 条，下表）+ 少量格式破损。guard 保护的重复（六动词 CLI 在 5 处出现且互相一致）是 docs-as-contract，**不是**噪音，不要清。

## 决策 / 方案

单一处方：**narrative catch-up——让声明层追上实现层**。每条发现归入三种处置动作之一：

- **删**：过期从句直接删除（预算只降不升，符合 DOB-001 棘轮）；
- **改**：改写为现实真话（如"specs 主干 9 能力已落地，活跃 changes 为空"）;
- **指**：死链改指现处。

另外两个结构性决定（待 REVIEW 拍板）：

- **入口链单一化**：根 AGENTS.md 路由表是唯一正门，补一行路由到 `CONTEXT-MAP.md`（词汇/边界）；CONTEXT-MAP 的 "Reading order for a fresh agent" 降级为"defer to AGENTS.md"，删除指向已清零 plans 列表的中间跳。
- **不动的**：`_reference/` 冷存储保持隔离（只恢复丢失的 consumption-status 索引）；guard 保护的重复一律保留；`agents/` 空层与 `mixed` 组成的去留属 owning change，本 plan 不裁决。

## 问题清单（REVIEW 用，共 40 条：A 级矛盾 11 · B 级过期/死链 16 · C 级术语/结构/噪音 13）

严重度：**A** = 矛盾，会误导 fresh agent 得出错误结论；**B** = 过期 / 死链 / 事实漂移；**C** = 术语 / 链结构 / 噪音。

### A 级矛盾（11 条）

| # | 位置 | 问题 | 处置 |
|---|------|------|------|
| A1 | `README.md:19` | "当前状态：骨架…specs 为空，应用代码为壳" vs 现实（9 specs、28 归档 changes、真 CLI 与门禁） | 改写状态段 |
| A2 | `AGENTS.md:20` | COMMANDS.md 标注"骨架期占位"，实为 ENS-001 权威入口菜单 | 删括注 |
| A3 | `AGENTS.md:49-50` + `README.md:43-44` | `make verify` 标"占位（无测试）"，实跑 112-test 门禁 | 改写 |
| A4 | `docs/local-operations.md:6` | "install/verify 均不承载验证承诺"为假；且漏掉 test/smoke/create/record-stream 全部真实命令——本层最烂的一份文档 | 重写或并入 COMMANDS.md |
| A5 | `docs/README.md:10` vs `:14` | 同一文件把 known-limitations.md 一行标"尚未建档"、另一行标"✅ 首版" | 删 :10 行 |
| A6 | `CONTEXT-MAP.md:21` + `README.md:20` + `_done/README.md:6` | 三处都指向"活跃 plan 列表 / 三份衍生 plan"，实际 plans/ 已清零（CLS-004/005/006 早已消费）——顺链走进空文件 | 改指 `_closed_plans/` 或删除 |
| A7 | `plans/README.md:33-43` | 归档索引缺 CLS-008（deep-run-postmortem）与 CLS-009（queued-triple）——违反自家"编号、索引、计数三处一致"ritual（_done 侧权威表两者都在） | 补两行 |
| A8 | `deep_research_harness/AGENTS.md:98-99` + `Makefile:10` + `COMMANDS.md:24` | "CLI / admission / receipt lanes 随 owning change 落地"、"editable 接线随 wiring change 落地"——全部**已经**落地（cli.py 六动词、pyproject.toml:7/42 editable） | 删将来时从句 |
| A9 | `openspec/change-guidance/local/deep-research.md:36-46` | **Delivery Lanes 指挥不存在的命令**：`make proof` / `proof-status` / `debugger-proof` / `mutation-check` 与 `proof-lanes.toml` 全部不存在——fresh agent 照做即失败；本审计中唯一会"误导出失败动作"的条目 | 改写为"lane 随 owning change 落地；今天只有 verify/smoke" |
| A10 | `openspec/governance/README.md:45,67,81` vs `:35-42` | checker 计数三个说法打架："九个" vs "六个" vs "八个"；实测 gate 清单（check_project_gate.py:41-51）= 8，其中 check_proof_receipts.py 不在 README 命令列表里、check_release_face.py 在列表里却不在 gate 里 | 统一为"8"并列真实清单 |
| A11 | `specs/run-bundle/spec.md:19,29,76,171-178` vs `specs/entry-surface/spec.md:17-19` | 跨 spec 命名矛盾：run-bundle 说 bundle 由 `start` action 创建，entry-surface 说 `create` SHALL start a bundle，无任何映射——两个名字一个概念（**规范语义，REVIEW 拍板**） | run-bundle spec 加一句 start↔create 映射 |

### B 级过期 / 死链（16 条）

| # | 位置 | 问题 | 处置 |
|---|------|------|------|
| B1 | `README.md:15` | 死链：`_reference/deerflow-native-deep-research.md` 已在 ded9c83 重排为 `_reference/deerflow/deerflow-native-deep-research.md` | 补路径段 |
| B2 | `README.md:45` | "the boundary plan **above**"——文件里上方并无此物，全树也不存在 boundary plan 文档 | 删短语 |
| B3 | `docs/runtime-architecture.md:3,6` | 自称"骨架占位" + "详见根目录 boundary plan"（不存在的目标）——但它被两张地图路由为运行时权威 | 重写为真实边界文档或收缩为路由页 |
| B4 | `docs/runtime-architecture.md:11` | 列出 `mixed` 组成，但 enum 之外不可达（cli 只开 fixture/base→all_real） | 标注 declared-but-unwired（规范语义，REVIEW 决） |
| B5 | `AGENTS.md:19` + `README.md:27,49` | "骨架期内容随后续 change 充实" / "specs 从零开始" / "骨架期先读第一个 plan"（无活跃 plan） | 删/改 |
| B6 | `README.md:54-55` | "声明锁与契约测试锚将在首个治理 change 建立"——ci-governance 已归档；未在 harness 代码找到 CURRENT_DEERFLOW_PIN 字面量，**UNVERIFIED**，落实前先核实 | 核实后改写 |
| B7 | `docs/README.md:3,9,11` + `tests/README.md:3-6` | "骨架期"头 + 对已充实文档的 ⬜ 标记 | 刷新状态列 |
| B8 | 5 个 `src/**/__init__.py` | docstring 仍写 "(skeleton)"（其上已有 ~2,400 行实现） | 一行式更新 |
| B9 | `_closed_plans/README.md:3`、`_reference/README.md:3` | "最后更新"头部日期落后于表内最新行（10-03 vs 10-04） | 补记 |
| B10 | `docs/testing-and-evaluation.md:3` | 引用机器本地绝对路径 `/Users/bowhead/deer-flow/_digest/...`——违反自家"结论不得依赖某台机器的工作区现场"铁律 | 改按名引用或复制进 `_reference/` |
| B11 | `openspec/governance/check_proof_receipts.py:9-12` | 硬依赖缺失的 proof-lanes.toml；今天 exit 0 只因 changes/ 为空（实测"no selected change"）——**第一个未来 selected change 就会撞缺失 registry**（required-paths.toml:72 钉了 checker 却没钉 registry）；落地或退役该装置属 change 决策 | 与 A9 同一 change 处置；先由 REVIEW 定落地/退役 |
| B12 | `openspec/governance/req-registry.yaml:24-26` | 头注"specs 为空（从头搭）…registered-not-alive"——specs 已有 9 个且 PRS-001 已 alive，与文件自身三态规则（:17）矛盾 | 删/改骨架期化石注释 |
| B13 | `openspec/governance/selected-change-closeout.md:3` | 文件名写成 `selected_change_closeout.py`（下划线），实际是 selected-change-closeout.py（连字符；config.yaml:97 写对了） | 一词修正 |
| B14 | `openspec/governance/architecture-policy.md:78-79` | 说生成块"names … node grammar"，但 node grammar 被同文件 :39-42/:64-67 移除，实际生成块也没有 | 删"node grammar" |
| B15 | `openspec/governance/required-paths.toml:9-10` | 头注"v3 骨架期…最小集合"，实际清单已 160+ 条目含完整实现路径 | 改写头注 |
| B16 | `openspec/governance/check_project_gate.py:149` | 注释引用未注册的 "PRS-009"（registry 只有 PRS-001）——违反自家 assign-before-use 纪律 | 修正或注册 |

### C 级术语 / 链结构 / 噪音（13 条）

| # | 位置 | 问题 | 处置 |
|---|------|------|------|
| C1 | `CONTEXT-MAP.md:18-22` vs 根 `AGENTS.md:14-21` | 两条互不引用的 fresh-agent 入口链；CONTEXT-MAP 链的中间跳已死 | 见"决策/方案"链单一化 |
| C2 | 根 `AGENTS.md` 路由表 | 漏 4 个根目录居民：README.md、CONTEXT.md、CONTEXT-MAP.md、profiles/ | 补一行（注意预算，见风险 1） |
| C3 | `deep_research_harness/CONTEXT.md:27` | "Entry Interface"（仍标 pending）vs 全库已定名 "entry surface"（ENS-001 已落地）——两个名字一个东西 | 统一命名，删 pending |
| C4 | 多处 | "gate" 双义（admission 机器 vs 质量门禁）；"梯"与实际机制 `--config` 从未挂钩；"建束"未注释 | 各加一行注释 |
| C5 | `Makefile:13` | verify 的 lane 隔离靠 `tests/integration/` 缺 `__init__.py` 的**偶然**（非 package 被 unittest 跳过）——实证 112 vs smoke 9 | Makefile 或 AGENTS.md 加一行说明 |
| C6 | `tests/README.md:5` | 广告空的 `tests/contract/` 目录 | 标注或移除 |
| C7 | `_closed_plans/README.md:28,30,32,34,36` + `known-limitations.md:11,13` | 空行把一张 markdown 表打散成多个单行表（渲染破碎） | 删空行 |
| C8 | `_reference/README.md` | 95248bd 声称加入的 consumption-status 索引在 ded9c83 重排时丢失——test-strategy/ 10 份 digest 已被 CLS-010 全量消费，但现在无从看出 | 恢复消费状态索引 |
| C9 | `config.yaml:29-31` + `test-evidence-policy.md:12` + `governance/README.md:23` | "test-evidence owning spec 待建立"同一 pending 承诺 ×3 | 保留在 test-evidence-policy.md，其余两处改指针 |
| C10 | `config.yaml:47-50` + `:61` + `local/deep-research.md:26-34` | Program Focus 语法三处复述 | config.yaml 拥有语法，deep-research.md 摘要+指针 |
| C11 | 活跃文档 ×6 | "A possible future use is not enough to expand scope" 口号复述 6 次（config.yaml:54、change-practice.md:24,79、deep-research.md:12 与 :16 五行内两现、harness AGENTS.md:17） | change-practice.md 留正身，他处指针 |
| C12 | `openspec/CONTEXT.md:21-31` | 死词汇表："Change Guidance Route" 与 "Cross-Cutting Review Guidance" 在活跃树中无人使用 | 删除或启用 |
| C13 | `openspec/config.yaml`（实测 12,237/12,500 字符 ≈ 98%） | 预算逼近上限且是本层最大单一噪音源（注入每条 OpenSpec 指令路径）；中文 design-routing 块（:77-85）与 change-guidance 路由表重复 | 把细则推入其指向的 profile 文档，为预算降压 |

### 明确不是问题的（避免过度打扫）

- harness 文档体量（~10% of code）健康；_backlog 约 82% 体量在 `_reference/` 但已被 `_` 前缀正确隔离且 README 声明"按需读"。
- 账本计数全面吻合磁盘（11 closed plans / Next CLS-012 / BUG-001），ritual 机器本身是健康的。
- 六动词 CLI 等多处一致重复由 command-surface-guard 机器守着——docs-as-contract，保留。
- openspec 层：导航 README 与 9 份 spec 结构是三层中最干净的（非归档 md 零骨架残留、扫描范围内零断链）；但 yaml/toml/脚本注释里仍藏着骨架化石（B12/B14/B15/B16）——"结构干净"不等于"全层干净"。

## 风险 / 取舍

1. **字符预算余量极小**：根 `AGENTS.md` 2323/2500、harness `AGENTS.md` 6934/7000（余量 66 字符）、`openspec/config.yaml` 12,237/12,500（≈98%，见 C13）。所有修订必须**先删后加、逐字计数**，每步跑 `python3 openspec/governance/check_doc_hygiene.py` 看红绿；预期净效果是预算下降（棘轮方向正确），降棘轮顺带在 DOC_BUDGETS 表中落数字。
2. **规范语义裁决项（按铁律 5 由人拍板，本 plan 只呈报）**：`mixed`（B4）、`agents/` 空层去留（AGENTS.md:59 路由目标为空）、A9/B11 的 Delivery Lanes 装置是**落地还是退役**、A11 的 start↔create 映射写进哪个 spec。
3. **修文档 ≠ 改行为**：本 plan 全部落点都在声明层；任何 checker 语义、COMMANDS 路由目标集合、spec 内容的改动都会越界进 change 领地——处置动作若触发这类边界，就地截断另立 change。
4. **B6 是 UNVERIFIED 项**：pin 声明的真实现状需在 change 期核实（在 harness 代码/治理表里找契约测试锚的现行形态），不得按猜测改写。

## 落地关联

- **建议 change**：`catch-up-doc-truthfulness`——纯声明层修订（A1-A10、B1-B16、C1-C13 中的非规范语义项；A11 因动 spec 内容单列），红绿判据 = `check_doc_hygiene.py` + `check_release_face.py`（COMMANDS 路由目标存在性）+ `make verify` 全 exit 0，且 A 级条目逐条前后对照。openspec 侧条目（A9/A10、B11-B16）与根/harness 条目可拆两个 change，按"一次放行一把"节奏由 REVIEW 定。
- **账本修正**（A7、B9、C7、C8）属 `_backlog` ritual 维护，按账本 README 规矩直接修三处 README，不必进 change；若 REVIEW 偏严，可并入上述 change 一并执行。
- **C1/C3（入口链与命名统一）**触及 CONTEXT.md 的词汇权威与 AGENTS.md 预算表，建议在 change 的 Change Focus 中显式列为 scope 边界。
- **实施顺序建议**：先账本修正（零风险）→ 根层（README/AGENTS/CONTEXT-MAP）→ harness 层 → openspec 层 → 每层收尾跑三个 checker。
