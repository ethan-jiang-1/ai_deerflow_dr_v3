# Issue: backlog 制度显性化（借鉴 loop_advisor）——缺陷修复流、状态生命周期、门票条件与 agent 门牌

> 立卡: 2026-10-12 ｜ 关闭: 2026-10-12 ｜ 状态: 已结 ｜ 类型: Task ｜ 毕业门: 已过 → make-backlog-process-explicit ｜ 可关闭: 是

**问题与期望结果：** 驾驭者点名
`/Users/bowhead/ai_dsh_loop_advisor/_backlog/issues/2026-10-12-backlog-process-made-explicit.md`
（同源谱系上游，2026-10-12，waiting-for-owner），要求借鉴立卡、借助它把本仓 `_backlog/` 的内容
调对：把本仓**已实行但未写下**的流程写显——① 缺陷修复流（谁授权开修、走哪条通道、什么算确认
修好）；② 双轨状态生命周期（词表 + 翻转法则成表成法）；③ 立卡门票两轨写全（清晰 + 验收手段，
由格式承载）；④ agent 门牌（`_backlog/AGENTS.md`，让规则推送到任何落进该区的 agent）。完成 =
拍板后的一个 OpenSpec change 把章程 / 模板 / 门禁词表 / 门牌落地全绿，本卡按 ritual 关闭。

**当前情况：** 制度大件已在（[CLS-019 adopt-issue-ledger-governance]
(../_archived/_settled_issues/2026-10-09-backlog-governance-reborrow.md)，2026-10-09：章程、两轨
模板、户口词表、triggers、methods、checker rule 7 门禁）。源卡七缺口已按本仓实况重审：**六条
成立**（其中两条本仓已有对应物，属收窄）、**一条不成立**（不借）。上游三条裁决（同一位驾驭者
2026-10-12 在源仓拍板）作为默认继承项列于下方；与本仓现行法有相互作用的两处标 ⚠ 待确认。

**未决问题：** 三个，均为 owner 选择：① 例外边界的本地操作化（接根 [AGENTS.md](../../AGENTS.md)
的 REVIEW 节制表，还是独立成文）；② bug 词表扩集与 `活跃`→`调查中` 更名；③ agent 门牌要不要
（要则入 `DOC_BUDGETS` 登记）。

**下一步：** 已收口（2026-10-12）：驾驭者放行全程落地，三张未决票按卡内推荐项默认（例外边界接
REVIEW 节制表 / bug 词表扩集更名 / 门牌采纳，翻案随时可）。make-backlog-process-explicit：
propose 工件齐（plan gate 0）→ apply 红绿全绿（prove-it-red 在案）→ 归档。本卡按 ritual 关闭为
CLS-024，去向 = make-backlog-process-explicit——同源谱系第四波（loop_advisor → 本仓）完成回流。

## 已知与未决

### 谱系与借法（借推敲，不借 diff）

loop_advisor 2026-10-03 曾从本仓补借主干 / 挂起池 / _reference（CLS-019 谱系节在案）；本仓
2026-10-09 反向借 ai_dsh_assitant（CLS-019）；本次是同源制度第四波。源仓的落点载体全是 DSH
特有的，逐项映射到本仓后，可迁移的只有推敲内容：

| 源仓载体 | 本仓对应物 |
|---|---|
| verify §7 frontmatter/状态行正则 | [check_doc_hygiene.py](../../openspec/governance/check_doc_hygiene.py) rule 7（词表 + 户口 + 滞留 + Next-ID） |
| `notes/proposed/` RFC + patches 一轮落 | OpenSpec change（propose → apply → archive；「一次放行一把」不变） |
| YAML frontmatter 状态生命周期 | 状态行 + 章程翻转表（[刻意不借 N2](../README.md) 延续：两套头部是纯成本） |
| `notes/` 交接 | `openspec/changes/`（methods: [issue-to-change](../methods/issue-to-change.md)） |

### 本仓缺口重审（对照源卡七缺口：六成立、一不成立）

| # | 缺口 | 证据 |
|---|---|---|
| 1 | 缺陷修复流未成文：授权与确认语义缺失（**通道已定**，比源仓强） | [章程](../README.md)「一张 issue 怎么走（四门）」是 issue-only；总流程图 bug 泳道写了「修复关联→change→关闭→回写」，没写**谁可开修**、**什么算修好**；[bugs/README](../bugs/README.md) 无对应走法节 |
| 2 | bug 模板无验收字段 | 模板四节（症状/根因/复现/修复关联）无验收；[BUG-001](../_archived/_fixed_bugs/BUG-001-degenerate-plan-as-report.md) 把「验收判据」即兴写进「修复关联」③——缺位的实测成本 |
| 3 | 立卡门票 bug 侧缺验收手段 | issue 侧四门第 1 步有「怎么算完成」；bug 侧模板无对应字段（与缺口 2 同根）。源仓缺口 4 的另一半（毕业判据两轨合一）本仓**已写明**（总流程毕业判据节），不借 |
| 4 | 无 agent 门牌 | 根 [AGENTS.md](../../AGENTS.md) 对账本只给 pull-only 路由；`_backlog/AGENTS.md` 不存在。DSH 平台嵌套 AGENTS.md 在 fs 触碰时自动注入（本会话平台即 DSH）；但本仓有 `DOC_BUDGETS` 常驻层预算棘轮，落地须登记 |
| 5 | 严重级别无消费者 | [bugs/README](../bugs/README.md) 记 P0/P1/P2，无规则读它。本地锚点：根 AGENTS.md REVIEW 节制表已列「不可逆或越界 / 规范语义裁决 → 请人」——消费者有现成接口可接 |
| 6 | 状态生命周期不成文、bug 侧空心 | issues 4 值的翻转规则散落三处（户口表、「等人拍板不是完成词」、暂停节）未成表；bugs 仅 `活跃`/`待修`，无「修就绪 / 已落修」形状——「实施不是验收」无名 |
| — | ~~复现字段缺席~~（源仓缺口 3） | 本仓模板已有 `## 复现`。**不借** |

### 上游三裁决（2026-10-12 源仓，同一位驾驭者；本仓默认继承）

1. **门禁升格缓议**：format first；「验收在场性」检查族（per-state 必备节）记 under-pressure，
   复发再议升格——与本仓「触发器语义门禁化」不借先例（[章程刻意不借节](../README.md)）同向，
   直接继承。
2. **fix-ready 缺陷卡自带修复授权**；严重 / 变向（源仓原话「确实很严重，更改了我们某些东西，
   变了方向」）走 owner。⚠ 本仓相互作用：现行法「卡上的状态与建议不授予实施权限」+ propose
   停在接受边界等拍板。本地适配建议：fix-ready 翻转自授权的是**撰写 propose**（规划工件）的
   动作，拍板仍停在 propose 接受边界（现行法不动）；例外（P0 / 触及契约 / 规范语义 / 变向）
   连撰写也要 owner 明示方向或走 issue 路。待确认。
3. **双轨状态生命周期成法**，词表为推荐材料、非已落地决定——本地形式落在状态行（非 frontmatter）。

### 五条补充（源仓 agent 提出、上游待扫；本仓适配版同样待扫）

1. **严重级别获得消费者**：P0 或触及契约 / 规范语义 / 越界 / 已记录决定的修复不自授权（走
   owner）；P1/P2 修复型 fix-ready 自授权。（闭缺口 5）
2. **铁律获得带日期的范围化例外**：「卡上的状态与建议不授予实施权限」对 fix-ready 的 bug 卡
   明示例外，写进章程——不让新流程暗着违背铁律。
3. **当场修复的横切排查落点成文**：四门第 1 步「当场修掉的缺陷不建卡」在案，但
   [bugs/README](../bugs/README.md)「把每个 bug 当契约探针（横切排查）」对**无卡**当场修如何
   落点未写。建议：落在当轮 change 的 Delivery Record 维护行。
4. **根因纪律一句成文**：假设 → 确认需证据（回执 / git history / 对照）；撤回的错误假设留卡上
   （[BUG-001](../_archived/_fixed_bugs/BUG-001-degenerate-plan-as-report.md)「初判修正」已是
   本仓先例）。
5. **搭载依赖可表达**：「修好判据」可点名其验证搭载的工作（如「随某 change 的真梯复跑一起
   证」），从即兴句子变模板字段。

## 方案与取舍

**事实单家划分**（对应源仓 frontmatter 方案，落在本仓自己的传统上）：状态行 = 当前阶段的
**唯一家**（一个词，rule 7 户口已锚定）；卡内追加行 = **历史**（verdict / 去向 / 撤回）；目录 =
**粗位置**（位置即状态）。不引入 frontmatter。

**issues 翻转表（词表不动，法则成表）：**

| From | Guard | To | Who | 记录 |
|---|---|---|---|---|
| 立卡后 | triage 后才立卡 | 推敲中 | agent | 状态行 |
| 推敲中 | 下一步是 owner 选择 | 等人拍板 | agent | 「下一步」写明问题 |
| 等人拍板 | owner 明确回答 | 推敲中，或出场 | owner | 行追加 |
| 推敲中 | 判断落地 + 交接提交 | 已结（同 change archive） | agent | verdict + 落地关联 + `git mv` |
| 任意活跃值 | owner 叫停（无判断） | 叫停（archive） | owner | `git mv` |
| 叫停 | owner 明确复活 | 推敲中 | owner | 行追加 |
| 已结 | 永不重开——复发 = 新卡引用本卡 | — | — | 回写律 |

**bugs 词表提案（`活跃`→`调查中` 更名 + 三增）：**

| From | Guard | To | Who | 记录 |
|---|---|---|---|---|
| 立卡后 | triage 后 | 调查中 | agent | 状态行 |
| 调查中 | 根因证据确认 + 修复方案选定 + `## 修好判据` 写就；P1/P2 修复型 | 修就绪 | agent | 翻转即门票**且**授权（裁决 2 本地形） |
| 调查中 | 同等就绪，但 P0 或触及契约 / 规范语义 / 变向 | 等人拍板 | agent | 通道问题本身 |
| 修就绪 | 修复已落树 | 已落修 | agent | 行追加 |
| 已落修 | 修好判据满足、证据在卡 | 已修（同 change archive） | agent | verdict 追加 + `git mv` |
| 调查中/修就绪/已落修 | 下一步是 owner 选择 | 等人拍板 | agent | 「下一步」写明问题 |
| 修就绪/已落修 | 根因或方案被证伪 | 调查中（向后翻） | agent | 撤回留卡 |
| 任意活跃值 | owner 停（查明未修、不排期） | 待修（挂起池） | owner | `git mv` |
| 已修 | 永不重开——回归 = 新卡引用本卡 | — | — | 回写律 |

`待修` 语义**保留不变**（停放：查明未修、明确不排期，挂起池）；`修就绪` 是新形状（准备好且
授权修，活跃区）——两者不混。

**共同翻转法则**：沉默不翻转；每次翻转 = 有守卫的动作 + 有记录；出场值只在 archive 的同一
change 内翻转；`可关闭: 是` 是出场守卫旗，随 `git mv` 落（现行法）。

**取舍表：**

| 选择 | 建议 | 落选方 |
|---|---|---|
| agent 门牌 | `_backlog/AGENTS.md` 薄门牌（五个子目录位置、走法、两张门票条件、词表、指针；不复制事实），入 `DOC_BUDGETS` 登记 | README-only（pull）：拒——规则要能到达落进该区的 agent，不取决于它选择去读 |
| 生命周期载体 | 状态行 + 章程翻转表 | frontmatter：不借（刻意不借 N2 延续） |
| 修复通道 | fix-ready 自授权撰写 propose；拍板停在接受边界（现行法） | 每个修复另立 issue RFC：拒（源仓 owner 已拒——bug 卡就是工作件） |
| `活跃`→`调查中` | 更名——与「活跃区」撞词、与 `推敲中` 动名词对称；现役活跃 bug 卡为零，改名零成本 | 保留 `活跃` |
| 毕业去向闭集头 | 不新增字段——本仓「关闭条件四态表 + `毕业门: 已过 → change` 指针」已覆盖源仓 graduation closed head 的功能 | 照抄闭集头 |
| `blocked` 词 | 不设——卡是读者消费的，依赖搭载在「修好判据 / 下一步」 | `blocked` 词 |
| 向后翻转 | 合法带守卫（证伪 / owner 回答 / owner 复活） | 只进不退 |
| 门禁 | rule 7 词表更新 + self-test 新负例（**既有类加强**，非新族）；per-state 必备节检查族记 under-pressure 不落地 | 一次升格全套：缓议（继承裁决 1） |

## 落地关联

OpenSpec change **make-backlog-process-explicit**（2026-10-12 apply 全绿、同日归档）。范围：
① 章程缺陷节写全流程（triage → 调查 → 修就绪 → 通道 → 已落修 → 确认 → 归档 → 回写）+ 例外
条款 + 铁律带日期例外 + 两张翻转表，总流程图 bug 泳道补授权 / 确认语义；②
[bugs/README](../bugs/README.md) 模板补 `## 修好判据`、状态节列词表与翻转规则；③
[check_doc_hygiene.py](../../openspec/governance/check_doc_hygiene.py) `BACKLOG_STATUS_VOCABULARY`
扩集 / 更名 + self-test 负例；④ `_backlog/AGENTS.md` 门牌 + `DOC_BUDGETS` 登记（若采纳）；
⑤ [issues/README](README.md) 状态节链接翻转表。本卡状态与建议不授予实施权限——等拍板。

## 关闭条件

做（四态之一）：owner 扫卡拍板（五补充 / 例外边界 / 词表）→ change propose → 拍板 → apply
红绿全绿 → archive → 本卡按 ritual 关闭（去向 = make-backlog-process-explicit）。
