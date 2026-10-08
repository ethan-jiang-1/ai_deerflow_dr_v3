# Plan: 应用开发语料消化与吸收（application-corpus adoption）

> 类型: 设计 | 更新: 2026-10-08（语料第 10 轮增量对照后）
> 来源: 语料 `/Users/bowhead/deer-flow/_deerflow_application_agent_ready_development/`（三卷 19 页正文——卷一 3 + 卷二 10 + 卷三 6，各卷另有 00-index 与 README + `_coverage` 维护层 + `verify.mjs`/`verify.test.mjs`，钉定上游 release tag `v2.1.0` = `345f08be`）逐篇消化；语料第 10 轮（评审落地 + 全量补充）增量已对照，见"第 10 轮增量对照"节。
> 驾驭者三裁决（2026-10-08）：① 诊断成立——"借了器官、缺循环系统"；② 范围=**整个**（流程 / 测试资产 / 质量保证，含代码级守卫）；③ 质量第一指涉=**产出质量**：测试资产是约束机制，"我们生产的内容是对的"是终点。

## 一、总判断

语料对"独立应用仓"的一句话模型：**把用户意图、接入形态、实现、配置组合、测试资产、交付判断连成一条可复查的链；每层证据只证明它断言的属性（能 import / 契约级测试 / 组合装配 / 宿主侧观察是四件不同的事）；证据高于绿勾；每条规则写穿自己的执行等级（成文标准 / 机器门禁 / 自我声明 / 仓库外不可核实）；设计决策归 spec 所有、偏离登记而非隐瞒；主仓 SDLC 不随依赖继承。**

对照结论：v3 在**机制件**层面与语料高度同源（测试学说与"不证明什么"车道表、doc 预算、CI 治理、回执车道、closeout gate、架构/依赖 checker、scar-tissue、Alternatives 负知识、Change Focus 意图入口——archive 十余个 change 的累积）。距离在两层：

- **连接层**（"驾驭无力"的直接病灶）：闭环没有一页可走通的旅程；证据分层没有成为组织词汇；门禁等级不可见；交付记录缺"未执行检查"必填段；偏离登记无常设机制。
- **目标层**（裁决③击发）：产出质量的可断言面未定义——研究引擎质量无自动化验收、替身阶梯级 4（行为断言）未规划、`real-model-io.jsonl` 无测试消费者。CLS-010 Tier C"行为断言 eval 栈"的触发条件（"需要断言研究质量本身时"）已明示满足。

语料最可移的不是某条制度，而是四个元姿势：**证据分层声明边界；声明的等级写穿；偏离登记不隐瞒；文档=交付物由测试钉住**。外加一句双向警告：主仓制度不随依赖继承——语料本身也不是教条，采纳矩阵逐条标"不搬/⏸"。

版本事实（钉定核对，2026-10-08）：语料钉 `v2.1.0`（`345f08be`）；我们 gitlink `ceebf97f` 是它的**后代**（`ethan-v2.1.0~1` digest 研究分支；`git merge-base --is-ancestor 345f08be ceebf97f` 核验 v2.1.0 commit 为祖先）。语料的运行时事实对我们适用；但根 `AGENTS.md`"submodule 锁 `ceebf97f` = 上游 v2.1.0"的等式**不成立**（后代 ≠ tag 本身）——正是语料维护页方法论防的病，见 C3。

## 二、采纳矩阵（语料条目 × v3 现状，2026-10-08 全量盘点）

✓=已对齐｜🟡=部分（缺口列明）｜✗=缺（change 承载）｜⏸=规模/形态门槛｜✗✗=明确不搬

| 语料条目（卷·页） | v3 现状 | 处置 |
|---|---|---|
| 开发闭环六步 + 每步页面归属（卷一 00） | ✗ 根 AGENTS 是路由表、`_backlog` 是账本管道；无可走通的旅程页 | **C1** |
| "四件不同的事"证据分层词汇（卷一 00/03） | 🟡 车道表有"不证明什么"列；"mirror 合同 / 装配 / 真实观察 / 冷启动"未成为组织词汇 | **C1** |
| 门禁等级四分：成文标准/机器门禁/自我声明/仓库外不可核实（卷二组织立场） | ✗ 散件在（回执=runner 写、checker=机器门禁）但无词汇、规则不带标 | **C1**（定义词汇）+ **C2**（标注到规则） |
| 交付记录四段：外部行为/影响面/实际跑了什么/未执行检查（卷一 03 §4） | 🟡 Change Focus + tasks 回执 +「state plainly what could not be verified」散件在；无成段必填——"没测的部分"最易被生成文本的自信语气掩盖 | **C2** |
| spec 权威三件套 + deviation register（卷二 02） | 🟡 design.md 是每 change 权威载体、Alternatives 在案；偏离仅一次性披露先例（entry-surface tasks 6.1）；无"tasks 只排序不决策"声明、无常设登记段 | **C2**（核心——语料点破 agent"顺手重新设计"的解药） |
| slice 收尾重读 spec 检查单（卷二 02） | 🟡 apply-resume 重读义务仅在 control-placement 触发时强制（config.yaml tasks 规则） | **C2** |
| red-green 自报句式（卷二 03） | 🟡 红先行成文+回执在案；无"先红后绿"自问格式 | **C2**（并入交付记录段） |
| PR 表面/AI 披露（卷二 04）→ 翻译为 change 工件 | 🟡 Change Focus=用户视角；无影响面勾选、无 AI 参与披露/责任段 | **C2**（按 solo+agent 形态裁剪：评审强度信号，不是合规仪式） |
| 四类陈述：运行时事实/上游要求/应用仓建议/仓库自定（语料 README） | ✗ 缺——也是防止语料自身变教条的疫苗 | **C2** |
| 意图入口 trigger+pain、非平凡先对齐（卷二 01） | ✓ Change Focus（owner/Question/Not in scope）覆盖 | 维持 |
| TDD 强制 + 套件三分 + live 永不进 CI（卷二 03） | ✓ doctrine 三车道 + real 显式 opt-in | 维持 |
| CI 门禁矩阵结构：触发/例外/契约双端触发（卷二 05） | 🟡 单 job canonical 序列 + 路径过滤已声明且由 `check_ci_governance.py` 机器校验；"双端触发"因单 job 全序列而天然满足 | **C5**（仅写明语义，不加机制） |
| 架构边界/指南预算/文档示例进测试/工具链钉住（卷二 06、卷三 02） | ✓ 大量已有（architecture checker、doc-budgets、command surface 钉、CI 预算与 pinned 工具链）；🟡 docs 内代码示例未 exec | **C4**（按需：出现会被人抄的示例时钉） |
| 术语表 + 常见误读（卷一 02） | 🟡 CONTEXT-MAP 三 bounded context 在；无误读栏 | **C4** |
| "指南与代码冲突时信代码"（卷三 01） | ✗ 未写明 | **C4**（一行） |
| 手册阶梯"最快理解路径"起步页（卷三 03） | 🟡 docs 索引在；无"三步跑通"起步页 | **C4**（可选） |
| 上游边界与代价页（负面事实+对策，卷三 06） | 🟡 散见（框架只读、"不证明什么"）；无成页 | **C4**（并入 deerflow-downstream 或 docs） |
| 发版版本五源门 / 迁移链 / nightly / 按时长分片（卷二 05/07/08） | ✗✗ 主仓规模长出来的；我们已有最小发布面 + 冷启动守卫（CLS-011） | 不搬 |
| support-bundle / agent 评审评论面（卷二 09） | ⏸ 无外部报障面/多维护者；scar-tissue ✓ 在案 | ⏸ |
| 豁免反自授权 / 双入口信任（卷二 10） | ⏸ 无豁免机制（CLS-010 已记先例条件） | ⏸ |
| 分层指南 + nearest-file + 单一事实源（卷三 01） | ✓ 根路由 + app AGENTS + 禁嵌套 AGENTS 政策 | 维持 |
| 配置版本升级 / doctor（卷三 05） | ⏸ 配置 schema 演进时 | ⏸ |
| 钉定纪律 + 重审触发（`_coverage` 方法论） | ✗ 实证缺口在案：根 AGENTS.md pin 等式失真 | **C3** |
| 语料处置（复制进仓 vs 原地引用） | 待裁决 | **C3**（裁决+落地） |
| 产出质量可断言面（卷一 03"更深的组合证据应用仓自建" + 裁决③） | ✗ 触发已击发：无自动化研究质量验收、级 4 未规划、real-model-io 无消费者；探索确认现有裁决面 **0 个**断言内容质量 | **C6**（本 plan 主事件；探索完成，A–G 面与批次见 C6 节） |

### 第 10 轮增量对照（2026-10-08，语料"评审落地 + 全量补充"后复核）

第 10 轮**不改 C1–C6 路线**；增量条目处置如下（语义并入上方矩阵，不单开 change）：

| 第 10 轮新增（卷·页） | 对 v3 的意义 | 处置 |
|---|---|---|
| 第五接入形态 custom agent/ACP 定义、guardrails 三 provider、IM/GitHub 渠道绑定（卷一 01 新节） | 我们是内嵌 harness 形态，不用 Gateway 部署面、`plugins:` 装载与 task 委派目录配置 | ⏸ 登记；将来启用 config 定制子代理或 guardrails 时回看 |
| 非交互运行语义：`context.non_interactive` 排除 `ask_clarification`、客户端自带副本被服务端双入口丢弃（卷一 01） | 上游对"非交互不能依赖问用户兜底"的原生立场；我们已有反问门控（TTY/env）+ 拒答回落自动应答（`test_clarification_journey`），实践同源 | 上游事实参考：clarification-channel-discipline plan 可引用；C4 上游边界小节一并登记 |
| issue 表单三路分流（bug/想法/漏洞各归各口）（卷二 01） | 无外部贡献面 | ⏸ 不搬 |
| RFC 原生层 + "旧 RFC 示例与已合并代码及测试不一致时，以已合并契约为准"（卷二 02） | deviation register 裁决权的原生先例：偏离裁决在**已合并契约与测试**，不在先写的文档 | 并入 C2 依据引文 |
| 门禁配套文档层：BLOCKING_IO_DETECTION / REPLAY_E2E 的 "fake green" 动机（卷二 05） | 与我们 replay 车道学说同源——"手写 mock 的 e2e 会 fake green"正是我们录制回放 fixtures 的动机 | C5 写明 CI 语义时引用 |
| copilot-instructions 修正：两套指南面并存、互不引用、优先级主张不同（卷三 01） | 我们单一指南面（AGENTS.md + CLAUDE `@` 导入），无此病 | C4 预防性一行：若出现第二工具专属指南面，显式写明冲突时信谁 |
| 两级文档阶梯 / backend/docs 工程文档五类（设计/行为/门禁/契约/运维）（卷三 03） | 我们 docs/ 已有近似分层（地图/研究/测试/运行/运维/质量登记 + playbook + skills） | C4 可选参考，不新增结构 |
| 手册快照警示：integration-guide 三处与 v2.1.0 源码不符（`stream()`/`chat()`、`get_app_config()`、`app.gateway`）、`POST /api/skills/install` 代码比文档严（admin-only）（卷一 01） | "上游文档是快照、引用上游行为必须对源码核验"的实证案例 | 并入 C3 钉定纪律 |
| 语料更名"DeerFlow 应用开发语料"（去 "agent-ready" 流行语） | 目录名保留作外部制品标识 | 无动作 |

## 三、落地路线（每件一 change，一次放行一把）

### C1 `land-development-loop-map` —— 地图先行，最快治"驾驭无力"（✅ 已落地 2026-10-08，archive：`openspec/changes/archive/2026-10-08-land-development-loop-map`；闭环页落点裁决为 `openspec/README.md` 扩展，根 AGENTS 余量 22 字符不足加行）
一页式开发闭环旅程：意图（Change Focus）→ 权威归属（Policy Route / owner）→ slice 交付 → 证据分层（车道）→ 验证形态 → 交付记录；每步页面归属可点。"四件不同的事"按我们形态命名：**离线契约 mirror / 装配 smoke / 真实梯观察 / 冷启动发布**。门禁等级四分词汇随页定义。落点候选（proposal 定）：`openspec/README.md` 或根 AGENTS 路由扩展 + app docs 入口；受 doc budgets 与 doc-hygiene checker 约束。纯文档为主，快。

### C2 `harden-change-authority` —— 权威三件套，治"驱动一下能干点但质量成问题"（✅ 已落地 2026-10-08，archive：`openspec/changes/archive/2026-10-08-harden-change-authority`；config.yaml 0 余量故规则文本住 change-practice.md，语法住 checker @impl CHA-001；本 change 自身 dogfood 两段常设段）
语料卷二 02 的逻辑：agent 天然倾向在实现文件里"顺手重新设计"；解药是 spec 独占设计决策 + 实现工件自降权威 + 偏离登记。落地：tasks 模板加 deviation register 常设段（无偏离时显式声明"none"）；change-practice 补"实现工件只排序与验证、不重新设计"scope rule；slice 收尾重读检查单从 control-placement 泛化；交付记录四段成段必填（外部行为/影响面/实际跑了什么/**未执行的检查**）+ red-green 自问句式 + AI 参与披露段（solo+agent 形态裁剪版）；四类陈述进 change-guidance。checker：`change_guidance_kernel.py` / `check_change_guidance.py` 扩展，新规则必须能红（负例控制）。规范语义改动——proposal 停在规划边界等驾驭者拍板。

### C3 `pin-upstream-claims` —— 钉定纪律，小而关键（✅ 已落地 2026-10-08，archive：`openspec/changes/archive/2026-10-08-pin-upstream-claims`；语料处置=**A 原样复制**（38 文件零差异进 `_backlog/_reference/deerflow-application-corpus/`）；另发现并修正 `README.md:93` 同病等式一处）
修正根 AGENTS.md 的 pin 等式（`ceebf97f` = v2.1.0 后代、digest 分支、v2.1.0 为祖先——写清差异性质）；deerflow-downstream profile 补"对上游的论断必须钉定可核对（tag/commit + 核验方法），pin 前进时重审"纪律；裁决并落地语料处置——**建议原样复制进 `_backlog/_reference/`**（语料 README 自述"复制全部内容并保留相对目录结构即可独立阅读和验证"；`verify.mjs` 可独立跑；引用一律"卷·页"不带行号；重审触发=上游 re-pin 时）。注意：语料自带 `_coverage/` 下划线目录，与 `check_doc_hygiene.py` 的 `_backlog` `_` 目录声明约定的相容性要在 change 里验证处理。复制不动内容。

### C6 `establish-output-quality-acceptance` —— 主事件（裁决③）

**探索已完成**（2026-10-08 盘点：通读 engine/runtime/domain 源码、`run-admission` 主规范、四份文档地图、相关测试与两个 replay fixture，并对 real-small-stream.json 做了脚本核验；行号引用以当日工作树为准，change 时重新取证）。核心结论：**现有裁决面无一面断言报告内容质量**——validator 六码全形状级（research-process.md 自认"不验证引文真实、观点全面或事实正确"），quality register 七台机器全是形状/控制/完整性裁决；但产出质量存在一条**已实证的机器断言路径**。

**可断言面（按确定性排序，每面"证明什么/不证明什么"成对）**：

| 面 | 断言什么 | seam / 契约 | 批次 |
|---|---|---|---|
| **A 来源可追溯性** ✅ 已落地 2026-10-08（形态修正：真实 bundle 探针证明"全 URL 可溯"不成立——厂商端点/模型知识 URL 合法 miss，故改为注册机器+纯函数+测试钉样，**不做 admission 阻断**；fixture 6/6 钉样；admission 化留待独立裁决） | archive：`openspec/changes/archive/2026-10-08-register-source-traceability-machine` | 第一批 |
| **B 报告结构契约** | ≥1 标题、存在 Sources 节、长度上下界、UTF-8 可读 | validator 扩展（封闭码集动 spec）；扩展"模型提议、代码裁决"既有模式，不改权力结构；"有 Sources 节"≠引用真实 | 第一批 |
| **C 回放物化断言** ✅ 已落地 2026-10-08 | 同左 | archive：`openspec/changes/archive/2026-10-08-assert-replay-materialization` | 第一批 |
| **D 真实梯行为侧写** | searches 文件数 / distinct query 数 / web_fetch 深读 / 角度覆盖代理 ≥ 声明区间；end.usage token 区间 | 纯函数可离线对历史 bundle 跑；级 4 lane 栏翻"规划"，永不进默认 CI；**前置接线：pump 现在丢弃 end 事件的 usage**；单次通过不构成统计结论 | 第二批 |
| **E real-model-io 接入完整图回放** | 真实历史输出零凭证驱动完整图+准入 | **诚实结论：现存资产不够**——单条孤立记录缺多轮 key 链与录制元信息（input/model/pin/命令），完整图几乎必然 ReplayMiss；需新录制承诺（费用+脱敏） | 立项才动 |
| **F 陈述级接地抽样** | 关键句（数字/日期/条文名）在同 run 工具输出有支持片段（重叠启发式） | 语义是裁决点（纳入句型/阈值），不定就是自动评分幻觉；LLM 评审属 `agents/` 空层 bounded role——先立合同再放代码 | 立项才动（首轮不进） |
| **G 多轮统计方差** | 同 base 问题重跑的方差/漂移 | 非确定模型+外部搜索漂移，两次运行无统计意义；统计面需 N 次运行+评分器（F 难点放大） | **建议显式登记不做** |

**明确不可断言面（真实梯+人评审，成文登记）**：洞察力/综合质量（SKILL Quality Bar 是模型自检非机器规则）；事实最终正确性（A 面只证"有记录支撑"不证"记录为真"）；覆盖充分性（缺负空间定义，D 面角度数只是代理）；引文-论断语义支持（URL 在场≠内容支持论断）；真实梯统计质量（单次非统计结论）。

**骨架缺口（change 时裁决，不顺手改）**：① validator 无内容维度（A/B 需新结果码）；② gate 数量推导在 runtime **无消费者**（阶段化验收要不要接线是裁决点，现状诚实声明为纯推导）；③ `hash_mismatch` 是**死码**（无生产者；给"final 文件 hash vs ledger hash 巡检"当语义槽位还是删码，二选一）；④ pump 丢弃 end.usage（D 面前置接线）；⑤ 每面落地进 DECLARED_MACHINES + quality register + 负例控制（machines 漂移即红）；⑥ A 面用 diagnostics/ 当依据不改 evidence/ 权属（断言器非 admission，spec 写明物理基础是 searches/）；⑦ `agents/` 空层门槛：LLM 评审先立合同再放代码。

**批次排序**：第一批 **C→A→B**（全部可用现存 fixtures 红绿、不碰运行时接线；A/C 直接把 research-process.md"每次搜索已物化到 diagnostics/searches/ 可直读复核"的人肉流程变成机器断言——"产出质量"裁决的最短落地路径）→ 第二批 **D**（小接线）→ E/F 立项才动 → G 显式不做。C6 按批次拆成多个 change，不一把梭。

### C4 `polish-guidance-vocabulary` —— 小件集合（可并入 C1/C2 顺带）
术语误读栏（CONTEXT-MAP 系）、"指南与代码冲突时信代码"一行、起步页（可选）、上游边界与代价小节。逐件受 doc budgets 约束。

### C5 `document-ci-gate-matrix` —— 可选（机制已够，仅写明）
把"契约双端触发"语义（框架绑定面或应用面任一变更 → smoke）写进 CI 治理文档；不新增机制。

**顺序与并行**：C1 立即（快、纯文档）；C2 随后——它是 C6 落地**可评审**的前提（没有权威三件套，产出质量的 change 工件自己也会漂）；C3 独立小件随时插；C4/C5 顺带。C6 探索**已完成**（2026-10-08，结论已进 C6 节），其 change 家族按批次进管道；驾驭者若要把 C6 第一批提到 C2 前，代价与收益见落地关联。语料第 10 轮对照（2026-10-08）不改变此顺序。

## 四、演变指导

1. 每个新 change：proposal 的 Evidence seam 回答"哪个车道证明它"（已有）+ 交付记录四段（C2 后必填）。
2. 引用语料的规范：结论引用带"卷·页"+钉定版本；主仓制度类条目永远标"上游参考"，不冒充本仓要求（四类陈述）。
3. 上游 re-pin（gitlink 前进或上游新 release）：重审 C1 闭环上的运行时事实 + 语料 `_coverage` 的重审触发路径逐条走。
4. 产出质量面若超出 run-admission 骨架承载，先立 owning spec（test-evidence 的 owning main spec 至今未建，governance README 在案）。

## 风险 / 取舍

- [借鉴过度超前于规模] → 矩阵逐条标 ✗✗/⏸；发版门、迁移链、nightly、分片明确排除；C4 全部可选。
- [流程件越加越重，小变更加不动] → 语料原话"小变更只有一段意图描述+验证方式"——C2 的段与勾选按 change 规模分级，权威唯一保留、形式随规模伸缩。
- [产出质量断言面定义不当（把不可断言的写成断言）] → 探索先交付"证明什么/不证明什么"成对清单；不可自动化面显式留给真实梯+人评审，不造"让不确定性看起来完整的回执"（change-practice 原则的反面教训）。
- [语料复制后与源头漂移] → 原样复制不动内容（verify.mjs 可独立验证）；漂移由 C3 的重审触发管理。
- [C6 探索无边界] → 交付物先定义（可断言面清单+证据语义）；超界问题回 buffer 立 plan/bug，不在 change 里夹带。

## 落地关联

顺序：C1 → C2 → C3（随时插）→ C6 change 家族（第一批 C→A→B，第二批 D；E/F 立项才动，G 显式登记不做）→ C4/C5 顺带。驾驭者可调整放行次序——把 C6 第一批提前到 C2 前的收益是产出质量尽早兑现（A/B/C 全用现存 fixtures、不碰运行时），代价是 A/B 要动 run-admission 封闭码集（属规范语义，本就停在拍板边界，风险可控）而少一层 C2 防漂约束。每把一个 change，propose 停在规划边界等驾驭者拍板（规范语义由人裁决）。本 plan 在首批产出质量资产（A/B/C）落地后关闭（届时分配 CLS-017）。
