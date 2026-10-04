# Plan: Agent 启动面收归仓库自有文档 + 最小发布面

> 类型: 设计 | 更新: 2026-10-04 | 状态: 已 REVIEW 并修订（同日，修订点见下）；待操作者拍板决策 3/5 后入线
>
> REVIEW 修订记录（2026-10-04）：① 决策 5 落位表与决策 3 自相矛盾（spec 主干被误列
> 为"必须进发布面"）——拆行改判，三件套残留字样清除；② 背景日期改为有回执背书的
> 2026-10-04；③ "3 目录 vs 两件套"的出入升格为显式风险项（含裁决后的影响面说明）；
> ④ 状态行同步。

## 背景 / 现状

**触发**：操作者会高频用一句「跑起来 / 跑一个研究」使唤 agent。2026-10-04 实测发现：
repo 文档存在**两层失真**，导致每次被使唤都要重新探索——

1. `deep_research_harness/README.md` 自称 "pre-implementation stub / Entry Surfaces:
   Not defined yet"，但 `COMMANDS.md`、`cli.py`、Makefile、测试 lane 全部已实现。
   README 的状态声明与代码事实相反，agent 信文档就会得出「跑不了」的错误结论。
2. 启动知识里有一批**配置自己不会招供的坑**（make 吃掉 `--config` 旗标、`.env` 缺失、
   smoke 里故意失败测试的 traceback 噪音、langgraph 版本告警），无处登记，靠现场重查。

**初次尝试及其否决**：2026-10-04 曾把启动手册与 HELP 卡写进 `.agents/skills/`
（`run-harness`、`harness-help` 两个私有技能，均已实测生效）。操作者否决了这个做法，
理由成立：`.agents/` 是会话私产，**不随发布走**；把载重知识放在私产里，等于让发布面
依赖仓库外状态，且与仓库自有文档形成第二真相源。

**已完成的补救（本 plan 的现状基线）**：私有两个技能目录已删除；启动序列 + 坑 +
HELP 卡 + 回执纪律已改写进 `deep_research_harness/COMMANDS.md` 的 **PLAYBOOK** 节
（含全绿回执：2026-10-04，verify 106 tests / fixture create 完成 / smoke 9 tests OK）。

**约束**：

- 发布极简：操作者期望「只要 3 个目录就可以发布」，并要求把"发布最简"升格为**约束**，
  反过来引导今后的内容安排（2026-10-04 追加，见决策 5）。
- 边界既定：`.agents/skills/`、`.env`、gitignored 便利件是操作者保留区；`deerflow/`
  只读；规范语义的裁决归人。
- 账本规矩：本 plan 只记思考；契约变更必须走 OpenSpec change，不在 plan 里夹带。

## 决策 / 方案

### 决策 1：两层结构——COMMANDS 是入口面，PLAYBOOK 是子目录（操作者模型，2026-10-04 口述定案）

操作者的原话模型，作为本 plan 的定案基线：

> COMMAND 更多是**入口**一样的东西——就是我们能处理多少事情；细节全部进 PLAYBOOK。
> PLAYBOOK 是一个**子目录**，里头是各种各样的 **MD mixed with CLI**。人给他要求，可以
> 借助 COMMAND 转到 PLAYBOOK，PLAYBOOK 就可以启动整个过程。研究过程有多少可能的命令
> 都可以放进去，包括说明书也可以放进去。

由此定两层职责，严格分开：

**第一层 · `COMMANDS.md` = 入口面（菜单 + 路由）**。只回答「能处理多少事情」：
六动词 CLI、make 目标，每个条目一行；需要过程细节的条目给出指向 playbook 文件的
路由指针。**COMMANDS 里不写过程**——写过程就变成了菜单上印菜谱。

**第二层 · `deep_research_harness/playbook/` = 载重细节子目录**。一个场景一份文件，
**MD mixed with CLI**：Markdown 说明文与可直接复制执行的真实命令混排，每个文件自带
完成判据（退出码级）与该场景的坑。随用随长——研究过程的新命令、新场景、说明书、
手册都落这里，COMMANDS 加一行路由即可，菜单永远薄。

选它而不是另外两个形状的理由：

| 备选 | 否决理由 |
|------|---------|
| A. `.agents/skills/` 私有技能 | 不随发布走；会话私产承载载重知识；与仓库文档形成双真相源（已被操作者否决，2026-10-04） |
| C. 全部塞进 `COMMANDS.md` 单文件（本 plan 初版方案，已自我否决） | 菜单与菜谱同页，COMMANDS 膨胀成第二个 docs/；场景一多入口面失焦，违背"入口只报能力"的操作者模型 |
| D. 独立 `docs/playbook.md` 单文件 | 同 C 的单文件病；且 docs/ 受 doc 预算闸管辖（DOB-001），playbook 要随用随长，不该挤占受预算的文档层 |

> **工作现场说明**：当前 `COMMANDS.md` 里已有一节 PLAYBOOK（本 plan 初版落的种子），
> 形状与决策 1 不符。它就是 `playbook/run-research.md` 的**种子内容**，随落地 change
> 原文迁入子目录；REVIEW 通过前不做现场翻动，避免菜单两次变形。

### 决策 2：playbook 文件的内容纪律——MD mixed with CLI，只做缓存不做第二权威

每份 playbook 文件的固定纪律（写入落地 change 的 spec delta）：

- **MD 部分只写三类东西**：① 完成判据（每步「done 长什么样」，退出码级）；
  ② environment 招供不了的坑；③ 场景说明书（为什么这么走、边界在哪）。
- **CLI 部分必须是可直接复制执行的真实命令**——不写伪码、不写"类似这样的"；
  命令改了，playbook 同一轮改（回执纪律：只报本会话实际执行过的 run；事实过期与
  发现过期同一轮修掉）。
- **动词清单、配置格式等环境能自查的事实不复制**——指回 COMMANDS/Makefile；
  复制必漂移。
- 一场景一文件，文件名 = 场景名（kebab-case）；新场景进 playbook、路由进 COMMANDS，
  两处各一行，不许在 COMMANDS 里展开细节。

### 决策 3：发布物研究（2026-10-04 实证）——最小发布面 = 两件套，openspec 在发布面外

操作者提问：「是不是只要发布 deep_research_harness 就够了，还是需要辅助其他东西？」
按证据回答，逐项查证：

| 候选物 | 运行时依赖？ | 证据 |
|--------|------------|------|
| `deep_research_harness/` | **是（本体）** | cli.py + src + config/ + Makefile + uv.lock 全在此目录内 |
| `deerflow/` | **是（唯一外部硬依赖）** | pyproject `[tool.uv.sources]`：`deerflow-harness = { path = "../deerflow/backend/packages/harness", editable }`；runtime/client.py 懒加载 `from deerflow.client import DeerFlowClient`；cli.py `_pin()` 对该目录跑 `git rev-parse` |
| `openspec/` | **否** | harness 源码/CLI/Makefile 零 openspec 引用；`make verify` 明文承诺不读不引不执行 OpenSpec——纯开发治理面 |
| `_backlog/`、根 `AGENTS.md`/`CLAUDE.md`、`.agents/` | 否 | 开发面/账本/会话私产 |
| `.env` | real 梯要，fixture 梯不要 | 用户保留区，永不入发布 |
| `scopes/`、`.venv/`、`../.uv-cache` | 运行时自建/可再生 | 冷启动现场生成 |

**结论（待操作者拍板）**：

1. **只发 harness 不够**——`deerflow/` 必须随行。但它本是 git submodule（锁
   `ceebf97f`），所以**发布形态 = 本仓库以 git 分发 + `--recursive`**，两件套天然
   同时到位；物理最小集即 2 个目录（harness + submodule）。
2. **发布形态是源码仓库分发，不是 wheel**：pyproject 的 wheel target 只打包
   `src/deerflow_deep_research`，cli.py、config/、scopes/ 全不在内——wheel 装出来的
   是没有入口的半成品。明确**不承诺 wheel 发布**；若未来要包分发，另立 plan。
3. **布局铁律**：`tool.uv.sources` 写死相对路径 `../deerflow/...`——发布布局必须
   保持 harness 与 deerflow 的**兄弟关系**；冷启动守卫顺带验证这条。
4. **随行辅助（非目录）**：git + submodule 初始化、Python ≥3.12、uv、uv.lock
   （在 harness 内 ✓）、首次 sync 的网络/uv 缓存；`.env` 由发布后使用方自配。
5. `openspec/`、`_backlog/` 等治理/账本留在开发面：不随发布走，但也不删——本仓库
   同时是开发工作区；"发布"指冷启动判据下的**发布面清单**，不是删目录。

**此界定是规范语义，须操作者拍板**；拍板后写入落地 change。

### 决策 4：使唤协议的失败路径

按 PLAYBOOK 走但门禁红了 → **先诊断再动手**，默认假设「repo 动了」而非「runbook 坏了」；
PLAYBOOK 各步完成判据同时充当最小冒烟集。real 梯缺 `.env` → 停下问操作者，绝不代建
（保留区）。

### 决策 5：发布约束 = 「两件套冷启动」，用它引导内容落位

**发布最简的定义从清单改成判据**：清单（"3 个目录"）会过时，判据不会。判据是——

> **冷启动测试**：全新 checkout 只含发布面（deep_research_harness/ + deerflow/
> submodule，见决策 3 的实证结论；openspec 在发布面外），然后
> `uv sync` → `make verify` → `make create PROBLEM=…`（fixture 梯）全程退出码为零。
> 冷启动里红的任何东西，就是发布约束的违反者；修法只有两种——折进发布面，或论证它
> 本来就不该被运行需要。

有了这个判据，今后每个新产物的「放哪」不再逐个讨论，按落位规则对号：

| 产物类型 | 落位 | 冷启动含义 |
|---------|------|-----------|
| 运行时真相（代码 / 运行时配置 / agent 消费文档） | **必须**进发布面（两件套，决策 3） | 缺了冷启动必红 = 缺陷 |
| 契约 / spec 主干 / 治理 checker | `openspec/`（开发治理面，决策 3 判其在发布面外） | 冷启动用不到，属正常 |
| agent 消费的载重知识（启动序列、坑、HELP） | **必须**进发布面内的 owning 文档（默认 `COMMANDS.md`/harness `AGENTS.md` 既有节，co-location） | 私产里只许放非载重缓存，红了活该 |
| 分析 / 账本 / 复盘 | `_backlog/`（工作面，不入发布面） | 冷启动用不到，属正常 |
| 凭证 / 便利件 | 保留区（`.env` 等），永不入库 | 冷启动用 fixture 梯即证不需要 |
| 新根目录条目 | **默认否决**；须走 change 论证「为何发布面与既有目录装不下」 | 守住"根目录刻意很小"的既有铁律 |

选 fixture 梯作冷启动终点的理由：它证明发布面**自足**（零凭证、零私产、零现场状态
也能跑通全链路），这正是「最少目录就能发布」（实证为两件套，决策 3）的可执行形式。
fixture 通不过的东西，加多少凭证都只是掩盖不自足。

## 风险 / 取舍

- [PLAYBOOK 与 README/AGENTS 漂移（README 状态声明现已确定过时）] → 不在本 plan 顺手改
  文档；README 的过时状态声明作为已知缺口列入落地 change 的任务清单，由 change 一并
  收口（契约/行为变更走主干，本 plan 只记思考）。
- [COMMANDS 与 playbook 两类读者（人查菜单 / agent 执行序列）] → 已由决策 1 的两层
  结构消解：COMMANDS 只剩菜单，过程细节全在 playbook；残余风险只是路由指针断链 →
  内容纪律要求新场景两处各一行、同轮改。
- [`playbook/` 位于 `docs/` 之外，不受 doc 预算闸（DOB-001）管辖] → 接受为刻意设计：
  playbook 要"随用随长"，不该挤占受预算的文档层；膨胀控制靠内容纪律（一场景一文件、
  三类内容上限）+ 结构登记随 change 入册；若日后失控再议预算化（新 plan，不预造）。
- [回执纪律靠自觉，无机器守卫] → 接受为取舍：启动序列的完成判据本身已是退出码直测，
  造假成本高于照做成本；若日后发现被绕过，再立 checker（新 BUG/plan，不预造）。
- [操作者的"3 目录"预期与研究结论（两件套）有出入] → 已在决策 3 用证据表显式回答
  「第三个是什么」：openspec 经查证不在运行时依赖里；若操作者拍板仍要含 openspec 的
  三件套口径，只改决策 3/5 的清单字样，判据与其余决策不受影响。
- [冷启动测试要拉 uv 依赖，受网络影响] → 首次后缓存暖、sync 毫秒级（2026-10-04 实测
  19ms）；离线口径用 `UV_OFFLINE=1`（verify 对离线安全是 Makefile 明文承诺）。
- [submodule 未初始化（漏 `--recursive`）的冷启动必红] → 这是守卫该抓的第一类违反；
  `cli.py _pin()` 对缺失 pin 已响亮退出，守卫只需把报错提前到 sync 之前并给出修复提示
  （`git submodule update --init`）。
- [fixture 冷启动只证自足，不证质量] → 定位就是发布冒烟，不是全量验收；全量仍由
  verify / smoke / change 门禁分层兜底，不让冷启动越权承载验收语义。
- [落位规则可能被"临时放一下"绕过（脚本、生成物落错处）] → 守卫进 change（见落地关联
  的冷启动守卫项）；绕过一次就红一次，而不是靠自觉。

## 落地关联

毕业判据已满足（决策/方案与落地关联填实）。计划拆**一个** change：

- **`ratify-agent-playbook-and-minimal-release`**（拟名）：以 OpenSpec proposal 正式
  接受 ① 两层结构：`COMMANDS.md` 定格为入口面（菜单 + 路由），新建
  `deep_research_harness/playbook/` 子目录（MD mixed with CLI、一场景一文件、内容纪律
  见决策 2），现有 PLAYBOOK 节作种子原文迁入 `playbook/run-research.md`，HELP 并入
  COMMANDS 菜单（入口面本身即能力清单）；② 发布面两件套界定 + 冷启动判据 + 布局铁律
  （以决策 3/5 的操作者裁决为准写入 proposal）；③ 决策 5 的落位规则表（发布约束，引导后续内容安排）；
  ④ **冷启动守卫**——把判据落成机器检查（CI 单 job 或本地 checker，进治理套件的
  canonical 序列），违反发布面即红；⑤ 顺手收口 `deep_research_harness/README.md`
  过时的 "pre-implementation stub" 状态声明与 "Entry Surfaces: Not defined yet" 段落；
  ⑥ `playbook/` 与其文件在项目结构侧随 change 登记。
- 放行节奏：遵守账本「一次放行一把」——待操作者 REVIEW 本 plan 并拍板决策 3/5 后，
  走 `openspec/propose` 入线；本 plan 在 change 吸收其结论后按账本流程关闭。

> REVIEW 关注点（给未来的评审者）：① 决策 3 的发布面实证结论是否与操作者预期一致——
> 尤其「openspec 不入发布面」「发布形态 = git --recursive 源码分发、不承诺 wheel」
> 两条是否认可；② 决策 1 的两层切分是否到位——`playbook/` 的文件粒度（一场景一文件）
> 与命名约定是否顺手，HELP 并入菜单是否符合操作者"COMMAND=能处理多少事"的模型；
> ③ 冷启动守卫放 CI 单 job 还是本地 checker，要不要进 push/PR 的 canonical 序列；
> ④ 回执纪律的「同一轮修掉」是否要升格为机器守卫。
