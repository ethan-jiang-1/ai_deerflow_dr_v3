# _backlog — 问题与缺陷账本（issues / bugs）

> 最后更新: 2026-10-09（adopt-issue-ledger-governance：plans 类别退役、issues 立为正式类别、
> `_done/` 更名 `_archived/`；新增关闭条件四态表、卡片户口与状态词表、活触发器索引与扫描义务、
> methods/ 方法库、刻意不借登记与翻案记录） |
> 本目录追踪本仓库的设计推敲、上游分析与缺陷。
> 活跃工作走 OpenSpec（`openspec/changes/`）；本目录是 **分析与决策记录 + 缺陷池**，不是运行时真相。
>
> **本文件是 `_backlog` 的规矩手册。** 搬迁流程、关闭条件、状态词表都在这里定死，今后大家都遵循这里头定的规矩。
>
> **命名约定：`_` 前缀 = "不在活跃工作件队列里"，分两个诚实类别，别混：**
>
> 1. **归档工作件**（会关闭；coding agent 默认忽略，除非点名）：`_archived/`
>    （含 `_fixed_bugs/`、`_settled_issues/`、`_suspended_bugs/`、`_suspended_issues/`）。
> 2. **留存参考 / 证据**（不参与工作件搬迁；agent 按任务按需读，**不**默认忽略）：
>    `_reference/`（外部系统分析）。
>
> 活跃工作件在无前缀目录（`bugs/`、`issues/`）；`methods/` 是无前缀的**常设方法库**（不是工作件区、不占名册）。**`_` 只表示"不在活跃队列"，不表示"禁止读"**——读不读由任务决定。`check_doc_hygiene.py` 校验：磁盘上任何 `_` 目录必须在此声明，且每个声明名必须出现在本文件中。

## 这个仓库是什么

`ai_deerflow_dr_v3` 是对上游 [bytedance/deer-flow](https://github.com/bytedance/deer-flow)（基于 LangGraph 的 AI super-agent 框架）之上，以 OpenSpec spec-driven 规范开发的 **Deep Research 智能体应用**。硬约束：**绝不修改上游源码**（`deerflow/backend/`、`deerflow/frontend/` 是上游镜像，位于 `deerflow/` submodule 内）。Deep Research 智能体开发走 `openspec/`。

## 目录结构

```
_backlog/
├── README.md                          # 本文件（规矩手册 + 索引）
├── triggers.md                        # 活触发器索引（账本：延后裁决的一次观察一行）
├── methods/                           # 🧭 常设方法库（按步骤选方法；不是工作件区）
│
├── _archived/                         # ✅ 归档工作件（会关闭；默认忽略）
│   ├── README.md                      #   状态总览、快速查阅指南
│   ├── _fixed_bugs/                   #   已修复 Bug（编号权威源）
│   ├── _settled_issues/               #   已结 Issue（CLS-NNN 台账；编号权威源）
│   ├── _suspended_bugs/               #   悬挂 Bug（查明未修）
│   └── _suspended_issues/             #   明确暂停、保留重启条件
│
├── bugs/                              # 🐛 活跃 bug → 修完移入 _archived/_fixed_bugs/
├── issues/                            # 📐 活跃 issue（推敲 → 结论 → 交接）→ 完成移入 _archived/_settled_issues/
│
└── _reference/                        # 📚 留存：外部系统分析资料（消化后产出 issue）
```

---

## 知识地图：从活跃到归档，两对生命周期 🗺️

`_backlog` 里只追踪两种工作件（**issue** 与 **bug**，不再增加类别——2026-10-09 起 plans 类别退役，其用法由 issues 继承，CLS-NNN 编号连续）；完成时移入 `_archived/` 下对应的 `_` 前缀子目录。明确不排期、但保留重启条件的记录则移入 `_suspended_issues/`，它不是完成状态：

| 类型 | 活跃（当前工作） | 归档（已完成） | 编号方式 |
|------|-----------------|---------------|---------|
| 🐛 **Bug** | [`bugs/`](bugs/) — 活跃 bug 列表 | [`_archived/_fixed_bugs/`](_archived/_fixed_bugs/) — 已修复 | BUG-NNN 递增，编号权威在 `_fixed_bugs/`；新号 = 已分配的最大编号 + 1（已修复 ∪ 活跃） |
| 📐 **Issue** | [`issues/`](issues/) — 活跃 issue 列表 | [`_archived/_settled_issues/`](_archived/_settled_issues/) — 已结 | CLS-NNN 递增，移入时分配（历史 CLS-001–018 有效） |
| ⏸ **Suspended follow-up** | 无；不进入推荐执行顺序 | [`_archived/_suspended_issues/`](_archived/_suspended_issues/) — 明确暂停 | 文件名不变；重新开启时移回活跃目录 |

> 📖 **想看全局状态、历史决策、查阅指南** → [`_archived/README.md`](_archived/README.md)
>
> 📖 **想看当前该做什么、依赖关系、执行顺序** → [issues 索引](issues/README.md)

---

### 暂停而非完成

当一个 issue 或 bug 已明确不再排期、但仍须保留问题背景和重启条件时，用 `git mv` 将其移入
`_archived/_suspended_issues/`（bug 进 `_suspended_bugs/`），文件名和内容保持不变。随后更新原活跃索引、
对应 `_suspended_*/README.md` 与 `_archived/README.md`；不要把它记为 DONE 或 CLS。**挂起跟显式指示走**：
agent 不得自行挂起；回活需要一次显式的新优先级决定。

---

## 一张 issue 怎么走（四门）

1. **记录问题**：先找已有卡，没有合适的再新建（模板见 [issues/README.md](issues/README.md)）。
   写清什么情况引出了问题、希望得到什么结果、怎么算完成、目前不知道什么。当场修掉的缺陷不建卡。
2. **弄清问题**：缺事实就查资料、读代码或试原型；短结论写回卡上。事实与建议分开写。
   每一步怎么做，查 [方法导航](methods/README.md)。
3. **形成结论**：回答做不做、什么时候做、先做什么、哪些不做。决定做的事项先写可执行的验收。
4. **申请下游处理并交接**：把完整申请（change 名 + 日期）写在卡的「落地关联」，结论被 change
   吸收后按 ritual 关闭。**申请去向必须在卡上可追溯**；卡上的状态与建议不授予实施权限。

## 关闭条件四态（离场前各留下什么）

| 结论 | 关闭前留下什么 |
|---|---|
| **做** | 问题、方案、真实比较过的选择及理由、可执行验收；「落地关联」写明 change 名与状态；毕业门打孔（`毕业门: 已过 → change`）后按 ritual 迁移 |
| **以后做** | 延后的理由、什么时候再看、到时观察什么。显式暂停的进挂起池；已裁决"该做不现在"且条件会自己撞上的，按 [triggers.md](triggers.md) 规则收一行 |
| **不做** | 原因和适用范围。属"刻意分歧"的，按根 AGENTS.md 第 4 条就地写明理由并留锁定测试 |
| **结论已在别处** | 指向已有决定或现行 spec/合同，说明它回答了本卡的什么问题 |

## 卡片户口与状态词表（机器可查）

活跃卡首 12 行必须带 `状态：` 字段，词必须在词表内（`check_doc_hygiene.py` 强制）；
状态行同时承载 `毕业门` 与 `可关闭` 两个锚定字段——**声明毕业或可关闭的卡仍滞留活跃区会红**：

| 区域 | `状态` 词表 | 其他锚定字段 |
|---|---|---|
| `issues/` | `推敲中` / `等人拍板` | `毕业门: 未过/已过`、`可关闭: 是/否`、`类型: Feature/Task/未定` |
| `bugs/` | `活跃` / `待修` | `严重级别: P0/P1/P2` |
| 离场时 | issue → `已结`（_settled）或 `叫停`（_suspended）；bug → `已修` 或 `待修` | 其余字段不动 |

**"等人拍板"不是完成词**——等人确认的卡诚实停在活跃区，门禁永不把它误判为毕业（锚字段，不锚正文形容词）。

## 活触发器索引（[triggers.md](triggers.md)）

延后裁决的触发条件沉在已关闭卡里没人翻，等于没有。索引只收一件事：**不在表上就会把已经
否掉的做法再做一遍，而且那条条件是工作里自己会撞上的一次观察**。延后不自动加行；
「用户点名」型不收（点名的动作本身就是触发）；常设指令/常设机制已经在盯的不收第二份。
**扫描义务**：change 归档收口时、立新卡前的取代检查时、阶段收口时，扫一眼。
写行/删行规则见 [triggers.md](triggers.md) 头部。行只是指针，句子留在 owner 卡上。

### 种子收割回执（2026-10-09，adopt-issue-ledger-governance）

首轮收割扫全部 19 张已关闭卡：收 8 行（见上表）；4 个候选按准入标准判出，在此登记防止下轮再议：

| 候选 | 判出理由 |
|---|---|
| CLS-010「AGENTS.md 预算治理」 | 已由 `DOC_BUDGETS` 棘轮常设机制在盯——常设机制在盯的不收第二份 |
| CLS-015 repository-map 维护触发表 | owner 活在应用 docs/README.md「地图维护触发条件」节，编辑动作自然会读到 |
| CLS-016「编辑器级修订再议」 | 「用户点名」型——点名的动作本身就是触发 |
| CLS-006「subagent 旋钮暂不需要」 | 同上 |

## 卡走到哪一步 → 用哪篇方法（[methods/](methods/README.md)）

方法按卡片步骤组织，消化自借鉴源并按本仓语境改写；每篇指向自己的 owner 与外部技能：

| 卡走到哪一步 | 方法（[methods/](methods/README.md)） | 关键 owner |
|---|---|---|
| 需求不清、问题太大要拆 | [澄清需求](methods/requirements-elicitation.md) | `CONTEXT-MAP.md`（词汇）；取代检查扫 [triggers.md](triggers.md) |
| 缺事实、要调研或试原型 | [补充证据](methods/requirements-probes.md) | 卡内留证；长寿命外部分析进 `_reference/` |
| 不知道怎样算完成 | [设计验收标准](methods/validation-design.md) | [车道表](../deep_research_harness/docs/testing-and-evaluation.md) + [test-evidence-policy](../openspec/governance/test-evidence-policy.md) |
| 信息齐、要比方案定结论 | [整理方案与结论](methods/requirements-synthesis.md) | 本文件关闭条件四态表 |
| 结论定了、要交接下游 | [申请下游处理](methods/issue-to-change.md) | `openspec/change-guidance/README.md`（Change Focus） |
| 验证时选证据 / 判结果 | [选择证据](methods/validation-evidence.md) / [判断验收结果](methods/validation-judgment.md) | 回执纪律 + Delivery Record |

**方法的维护规则**（依据实际使用、不进技能目录、不维护进度）见 [methods/README.md](methods/README.md)。

## 总流程：预处理 buffer → 加工 pipeline → 归位 🏭

```
输入面（发现什么就往对应区扔，允许半成品）
  ├─ 分析 / 设计推敲 / 排产   → issues/（问题 → 结论 → 落地关联，逐节充实）
  └─ 缺陷                     → bugs/（症状 → 根因 → 复现 → 修复关联）

毕业判据（buffer → pipeline 的唯一门票：能写出一张 Change Focus）
  issue:  「方案与取舍」与「落地关联」填实——选了什么、为什么、拆成哪些 change。
  bug:    「修复关联」能落到一个 OpenSpec change（bug 模板已内置此栏）。

加工 pipeline（唯一实施通道 = OpenSpec change）
  propose（只写规划工件，停在规划边界，等用户拍板）
    → apply（红绿先行、证据回执、closeout gate 退出码直测）
    → archive（gate 全绿 + strict validate）
    → 知识归位（specs/ 主干、代码、测试）

归位与回写（pipeline → 各自的家）
  issue 结论被 change 吸收 → issue 关闭（三处 README 联动）
  bug 修复交付 → bug 关闭；横切排查牵出新缺陷 → 回写 bugs/（新 BUG-NNN）
  复测/切片发现的新缺口 → 回写 buffer（新 issue / 新 bug），不在 change 里夹带
```

几条硬规矩：

- **没有 change，没有行为**：buffer 里的东西无论多成熟，都不会自己变成系统行为；入线必须走
  OpenSpec propose，规划工件停在接受边界等拍板。
- **卡记思考，change 记契约**：同一事实只住一处——卡的「落地关联」与 change 的 Focus
  Card 互链（引用，不复制正文）。
- **一次放行一把**：buffer 不是先进先出队列；按优先级每次只放行一个 change，做完再放下一把。
- **机器检查的位置**：入线前无门禁（buffer 允许半成品、允许推敲）；入线后由治理 checker 套件 +
  closeout gate 兜底，push/PR 由 CI 单 job 运行 canonical 序列（详见
  [`openspec/governance/README.md`](../openspec/governance/README.md)）。

---

## 刻意不借（负知识，带日期登记；下轮再议前先读这里）

> 2026-10-09 对 `ai_dsh_assitant/_backlog/`（同源制度的下游成熟形状）借鉴时裁定：

| 不借什么 | 理由 |
|---|---|
| `research/` 卡片随迁生命周期 | 本仓 `_reference/` 是长寿命框架参照（DeerFlow 盘点语料），不是按卡消费的证据堆；活跃卡证据就写在卡内 |
| YAML frontmatter 卡片头 | 本仓状态行传统已被 bug 卡与门禁锚定，两套头部约定是纯成本 |
| `YYMMDD` 短日期卡名 | `YYYY-MM-DD` 是本仓拍板过的强制约定，改名收益不值全量翻修 |
| 🔒 保留卡纪律 | 根 AGENTS.md 的 REVIEW 节制（用户保留区清单）已覆盖同类边界 |
| 触发器语义门禁化 | 「触发是否到场」是语义判断，机械门禁只能查行存在性、会逼出凑格式行；先以扫描义务运行，复发再议升格 |

**翻案记录**（原判被驾驭者推翻，日期与去向就地登记；用户指示即翻案触发）：

| 原判 | 翻案（2026-10-09，apply 中指示） | 现状 |
|---|---|---|
| 不设 `methods/` 目录（方法 owner 已存在） | 驾驭者裁定 methods 很重要，采纳 | [methods/](methods/README.md) 落地：消化改写 7 篇 + 导航，路由表改经方法导航 |
| `_done/` 名字保留 | 驾驭者裁定改名 | `_done/` → `_archived/`（含 `.gitignore`、checker、清单、活链接同步） |

## 搬迁规矩

两种工作件的搬迁步骤完全一样：**`git mv` 过去，文件名不变，位置即状态，连带更新三处 README。** 各子目录 README（`bugs/`、`issues/` 及对应的 `_archived/` 下级）里也写了具体步骤。

### 铁律

- **`_backlog` 独立于 OpenSpec** —— 两层各自簿记，不交叉判定。不要为了在 `_backlog` 标 done 而去动 OpenSpec。
- **文件内容原样保留**，不重写。用 `git mv`（不是普通 `mv`）。
- **反向可以**：`git mv` 回活跃目录即可。极少用，但允许。

### 两条命令

```bash
# Bug 修完
git mv bugs/BUG-<NNN>-<slug>.md _archived/_fixed_bugs/BUG-<NNN>-<slug>.md

# Issue 完成
git mv issues/<name>.md _archived/_settled_issues/<name>.md
```

### 搬完更新

> ⚠️ **README 文件本身永不删除。** "移除"指的是从活跃列表中移除该条目的行，不是删文件。每个 README 永远留在目录里做索引。**文件内容原样保留，`git mv` 搬迁。**

**🐛 Bug 修完：**
| 操作 | 怎么改 |
|------|--------|
| `bugs/README.md` | 从活跃列表移除该 bug 的行 |
| `_archived/_fixed_bugs/README.md` | 表格加一行 + 更新 Next available bug ID |
| `_archived/README.md` | 已修复 bug 计数 +1 |

**📐 Issue 完成：**
| 操作 | 怎么改 |
|------|--------|
| `issues/README.md` | 从活跃列表移除该 issue 的行 |
| `_archived/_settled_issues/README.md` | 表格加一行 + 更新 Next available plan ID |
| `_archived/README.md` | 已关闭 issue 计数 +1 |

---

## 相关外部文件

> 以下路径相对于 **本仓库根目录**，不是 `_backlog/` 目录。

| 路径 | 角色 |
|------|------|
| `AGENTS.md` / `CLAUDE.md` | repo 最高指引（monorepo 定位 + 跨切约定；`CLAUDE.md` 经 `@AGENTS.md` 导入） |
| `openspec/config.yaml` | OpenSpec 项目上下文 + 4 artifact（proposal/specs/design/tasks）规则 |
| `openspec/specs/` | 已接受 spec（运行时真相层，与 `_backlog` 各自簿记） |
| `openspec/changes/` | 活跃 change（完成归档于 `openspec/changes/archive/`） |
| `deerflow/AGENTS.md`、`deerflow/backend/AGENTS.md` | 框架 submodule 自带的只读指引 |
| `_backlog/_reference/` | 外部系统分析资料（如 DeerFlow v2.1.0 原生 Deep Research 能力盘点），消化后产出 `_backlog/issues/` |
| `deerflow/backend/` `deerflow/frontend/` | 上游镜像（**禁改**，submodule 锁定在 `deerflow/` 内） |
