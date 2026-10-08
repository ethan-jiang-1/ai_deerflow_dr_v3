# Proposal: Land Development Loop Map

## Why

驾驭者裁决在案（`_backlog/plans/2026-10-08-application-corpus-adoption.md`）：v3
"借了器官、缺循环系统"——机制件（车道表、治理 checker、回执、closeout gate）齐全，
但**闭环没有一页可走通的旅程**：意图从哪进、权威归谁、slice 交付包含什么、哪层证据
证明什么、验证用什么形态、交付记录写什么，散落在十余份文档里，每次驱动都要重新探索。
这正是"驾驭无力"的直接病灶。语料（DeerFlow 应用开发语料，钉定 `v2.1.0`）卷一 00 的
开发闭环与"四件不同的事"是现成解法；本 change 把它按本仓形态落地为地图。

## What Changes

- **`openspec/README.md` 从 18 行薄导航扩展为开发闭环一页地图**：六步旅程（意图 →
  权威归属 → slice 交付 → 证据分层 → 验证形态 → 交付记录与归位），每步页面归属
  可点，全部路由到既有 owner，不复制任何 owner 的正文。
- **定义证据分层词汇（"四件不同的事"按本仓形态命名）**：离线单元与契约 mirror /
  装配 smoke / 真实梯观察 / 冷启动发布——四层各自"证明什么 / 不证明什么"链接既有
  车道表（`testing-and-evaluation.md`），一层通过不代表下一层成立。
- **定义门禁等级四分词汇**：成文标准 / 机器门禁 / 自我声明 / 仓库外不可核实——
  读任何一条规则先问它在哪一层；本仓实例各举一二（治理 checker = 机器门禁、回执 =
  自我声明、required-checks 远端配置 = 仓库外不可核实）。
- **`_backlog/README.md` 总流程节补一行路由**指向闭环地图（缓冲区 → 管道的接力已有
  文字，补"全景一页走通见……"）。
- **`openspec/change-guidance/local/deep-research.md` Reader Roles 表补一行**：登记
  `openspec/README.md` 的新读者角色（维护者/coding agent，job = 走通开发闭环）。
- **不动根 `AGENTS.md`**：余量实测 22 字符（2403/2425），ratchet 纪律只降不升，
  落点刻意避开。

## Capabilities

### New Capabilities

none: 本 change 是纯导航/文档地图，无规范级行为变更。

### Modified Capabilities

none: 不改任何既有 spec 的 requirement；`skip_specs: true` 已在 `.openspec.yaml`
声明。规范性标注（交付记录必填段、deviation register、tasks scope rule）属后续
`harden-change-authority` change 的范围。

## Impact

- 文件：`openspec/README.md`（主落点，扩展）、`_backlog/README.md`（一行路由）、
  `openspec/change-guidance/local/deep-research.md`（Reader Roles 一行）。
- 既有守卫保持绿：`check_doc_hygiene.py`（入口链相对链接解析、既有预算不变）、
  `check_change_guidance.py`。无新守卫（既有链接守卫已能红）。
- 无代码、无运行时行为、无预算表变化、不触碰 `deerflow/` gitlink（既不修改也不
  深读）。
- 触发 lane：governance checks（文档层）；不触碰 harness 的 verify/smoke 面。

## Change Focus

- **Primary module / causal owner:** `openspec/README.md`——SDLC 入口导航层，
  开发闭环旅程"住在哪、路由到哪"这一语义决策的最小 owner。
- **Seam classification:** wiring — 纯导航与路由内容；无认知角色、无运行时状态、
  无准入语义。
- **Question:** 维护者与 coding agent 能否从一页走通"意图 → 权威归属 → slice 交付
  → 证据分层 → 验证形态 → 交付记录"的完整闭环，且证据分层与门禁等级有本仓命名的
  组织词汇？
- **Necessary adjacent/external contracts:** `check_doc_hygiene.py` 入口链规则
  （answers: 新内容的相对链接必须全部可解析，`openspec/README.md` 与
  `_backlog/README.md` 均在 ENTRY_DOCS）；`local/deep-research.md` Information Map /
  Reader Roles（answers: 新导航面的读者角色登记与"路由不复制"纪律）；doc-budgets
  （answers: 根 `AGENTS.md` 上限 2425 不动、余量 22 字符不足加行——落点避开根
  AGENTS）。
- **Evidence seam:** doc-hygiene checker 退出码直测（编辑后入口链链接全解析、预算
  无漂移）+ change-guidance checker 绿；旅程本身即操作者面证据——闭环页六个步骤的
  每个链接可点达真实 owner。
- **Not in scope:** 交付记录必填段 / deviation register / tasks scope rule（C2
  `harden-change-authority`）；pin 等式修正与语料复制（C3 `pin-upstream-claims`）；
  产出质量可断言面（C6 家族）；checker 规则或预算表变化；根 AGENTS.md 预算调整；
  app `docs/` 层新页（那是应用面，闭环是 SDLC 面）。
- **Triggered review policies:** change-admission, local-context
