# Issue: backlog 治理反向借鉴 —— plans 更名 issues、活触发器索引、门禁补盲

> 立卡: 2026-10-09 ｜ 状态: 推敲中 ｜ 类型: Task ｜ 毕业门: 未过 ｜ 可关闭: 否

**问题与期望结果：** 驾驭者点名 `/Users/bowhead/ai_dsh_assitant/_backlog/`（同源账本制度敲打后
最成熟的一环）消化借鉴，调整本仓 `_backlog/`。拍板定调（2026-10-09）：**长远做对**——plans 类别
退役、issues 立为正式类别。本卡按目标形态（issue 卡模板）立卡，已随 adopt-issue-ledger-governance
的目录更名迁入 `issues/`（2026-10-09）。

**当前情况：** 谱系已核清：ai_dsh_assitant 的借鉴记录自证其 `_backlog` 制度上溯
ai_deerflow_deep_research_v2，且同族 loop_advisor 2026-10-03 曾从本仓补借主干/挂起池/reference；
本次是把它下游长出的增量**反向吸收**。对照出的缺口四条：①关闭条件只有"做"一态（以后做/不做/
已在别处无离场仪式）；②延后裁决的触发条件沉底（CLS-010 Tier C 触发表躺在冻结卡里，CLS-020
靠主动翻旧卡才发现触发已满足）；③卡片无机器可锚的 `状态`/`毕业门` 户口；④门禁看不见
"毕业了没走"（名册只查行→磁盘，不查反向与滞留）。

**未决问题：** 无——proposal 已获驾驭者拍板（2026-10-09「apply」），实施中。

**下一步：** apply 进行中（红绿先行）；archive 后本卡按新 ritual 关闭（CLS-019，
去向 = adopt-issue-ledger-governance）。

## 方案与取舍

| 处置 | 内容 |
|------|------|
| 借·更名 | `plans/` → `issues/`；`_done/_closed_plans/` → `_settled_issues/`；`_done/_suspended_plans/` → `_suspended_issues/`。类别数仍为二（issues / bugs），"只追踪两类"铁律保留。CLS-NNN 编号保留（活文档引用 CLS-010/014，换前缀是纯 churn）。原计划 A1（不更名、以 plan 卡状态承载推敲期）被驾驭者推翻 |
| 借·关闭条件四态表 | 做（→ Change Focus + change 去向）/ 以后做（→ 挂起池或触发行）/ 不做（→ 理由+适用范围，呼应根 AGENTS.md 第 4 条）/ 结论已在别处（→ 指针）。补进 `_backlog/README.md` |
| 借·活触发器索引 | `_backlog/triggers.md`：延后不自动加行；只收"不在表上就会把否掉的做法再做一遍、且条件是一次工作里自己会撞上的观察"；删行三条；扫描时机 = change 归档收口 / 立新卡取代检查 / 阶段收口。种子从 19 张已关闭卡收割，宁缺毋滥（plan-review-gate"编辑器级再议"、wiring-structure"subagent 旋钮暂不需要"两条属"用户点名"型，不收） |
| 借·户口与状态词表 | issue 卡状态行：`状态`（推敲中/等人拍板/已结/叫停）+ `毕业门`（未过/已过）+ `可关闭`（是/否）+ `类型`（Feature/Task/未定，旧卡不回填）；bug 卡词表补 `待修` |
| 借·门禁补盲 | `check_doc_hygiene.py` 新增：⑦活跃卡户口（首 12 行含 `状态：` 且词在词表内）⑧名册反向互查（磁盘每张活跃卡必须被名册点名）⑨滞留检测（`毕业门：已过` 或 `可关闭：是` 仍滞留活跃区 → 红）。锚字段不锚形容词，"等人拍板"不是完成词，永不误杀；归档卡祖父豁免。各带红绿自测夹具 |
| 适配·方法路由不设目录 | 不设 `methods/`：方法 owner 已在（openspec/change-guidance、governance、会话技能），只在 backlog README 加"卡走到哪一步 → 读哪个 owner"路由表 |
| 适配·交接回执 | 卡上记录申请去向（change 名 + 日期）；关闭时机维持本仓现状（结论被 change 吸收后关，CLS 台账才能记到真实去向），不照抄"提交即关" |
| 不借·登记负知识 | N1 research/ 卡片随迁生命周期（`_reference/` 是长寿命框架参照）；N2 YAML frontmatter 与 YYMMDD 卡名（本仓状态行传统 + YYYY-MM-DD 拍板）；N3 🔒 保留卡纪律（根 AGENTS.md REVIEW 节制已覆盖）。带日期写进 `_backlog/README.md`「刻意不借」节 |

## 风险 / 取舍

- [新门禁误杀诚实卡] → 只锚 `毕业门`/`可关闭` 字段；夹具含"等人拍板放行"与"部分交付不误杀"负例。
- [AGENTS.md 字符预算 2425 贴边] → 表格 cell 编辑字符中性（"plans"→"issues"等长）。
- [更名弄断活链接] → 活触点清单固定（required-paths.toml 7 处、应用 docs 3 处活链接、
  openspec/README 1 处标签），doc-hygiene 断链规则兜底；`openspec/changes/archive/` 约 30 处
  历史引用属冻结记录，不 rewrite。
- [triggers.md 变成第二事实家] → 纪律进章程：行只是指针，句子留在 owner 卡/决定上；
  挂起池边界不动（池收未裁决暂停件，触发行收已裁决"该做不现在"）。

## 落地关联

OpenSpec change **adopt-issue-ledger-governance**（proposal 待拍板）。范围四件套：
①三笔 `git mv`（19 张归档卡正文零改动，同层搬迁链接深度不变）②章程重写 + `triggers.md` 种子
③checker 规则⑦⑧⑨ + 红绿夹具 ④活触点同步。delta specs：doc-truthfulness（"Ledger bookkeeping
surfaces are machine-consistent"扩展 + 新 requirement）。

## 关闭条件

做（唯一态）：change archive + verify 全绿 + 本卡已随更名迁入 `issues/` 并按 ritual 关闭
（CLS-019，去向 = adopt-issue-ledger-governance）。
