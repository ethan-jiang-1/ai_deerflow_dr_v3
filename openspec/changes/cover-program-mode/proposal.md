# Proposal: cover-program-mode

## Why

CLS-026 的跟踪项：**被保留的 program / workstream 模式（约 99 行、6 个模块）没有任何测试演练**。

取证（上一轮）：全仓 `openspec/tests/**` 里出现 `## Program Focus` 的 3 处**全部是围栏测试的夹具**
（`test_guidance_fences.py` 用它构造"围栏里的标题不该被 truncate"的用例），**不是对 program 校验的
覆盖**。同时该模式**有一个真实用户**（`2026-10-07-surface-runtime-structure`：`## Program Focus` +
三个 `### Workstream Focus:`），而且它是**唯一**的多工作流承载机制——所以裁决是**保留**，
但保留的东西**必须能被演练**，否则它只是一段没人验证过的代码。

## What Changes

- **新增直接测试**（落在既有的 `openspec/tests/governance/test_change_authority.py`，与同文件既有的
  "直接调校验函数 + 断言 `ContractViolation.code`"风格一致）：覆盖 program 模式的**核心分支**——
  - **正典绿例**：一个合规的 program 提案（`## Program Focus` 四个字段 + **两个** `### Workstream Focus:`
    各十二字段 + 声明顺序一致）**不报错**——这是该模式存在的意义所在，此前**零覆盖**；
  - `program.workstream_count_invalid`：只有一个工作流 ⇒ 报；
  - `program.mode_invalid`：工作流记录出现在 `## Program Focus` **之前** ⇒ 报；
  - `program.field_missing`：缺 `Program decision authority` ⇒ 报；
  - `program.workstream_registration_mismatch`：声明顺序与实际记录不一致 ⇒ 报。
- **不新增任何校验逻辑**、不改任何规则语义：本把只**补覆盖**。

**不变量**：七个 checker + closeout gate + 治理套件全绿 · `--self-test` 契约不变 ·
program 模式的实现一行不改 · 产品代码与 harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 只补测试覆盖，不改任何 requirement。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`openspec/tests/governance/test_change_authority.py`（新增一个测试类 + 夹具构造函数）·
  `check_code_budgets.py`（若该文件在表内则按实测）。
- **不动**：`change_guidance_check/` 的任何实现 · 任何规则语义 · 产品代码。
- **触发车道**：治理套件 · 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `openspec/tests/governance/test_change_authority.py` ——
  它拥有 change-guidance 校验的直接测试面；program 模式此前**不在其中**。
- **Seam classification:** deterministic-guardrail —— 补测试覆盖；无模型参与。
- **Question:** 一个被保留、**有真实用户**却**零测试**的分支，能否在不改任何实现的前提下被正典
  用例覆盖——绿例证明合规 program 能通过、四条红例各自指名违规码？
- **Necessary adjacent/external contracts:** `_validate_program_proposal`（answers: 被测入口）·
  `PROGRAM_FOCUS_FIELDS` / `WORKSTREAM_FIELDS` / `PROGRAM_FOCUS_HEADING` 常量（answers: 夹具必须
  写全的字段清单；**工作流是十二字段**，不是七个）· `_workstream_sections`（answers: <2 个工作流
  即 `program.workstream_count_invalid`；记录必须出现在 program 标题**之后**）·
  同文件既有的直接调用风格（answers: 不需要搭完整 change 树）。
- **Evidence seam:** 新用例逐条红绿 · 绿例此前**不存在**（零覆盖的实证）· 治理套件用例数增长 ·
  七 checker + closeout · 实现零 diff。
- **Not in scope:** 改 program 模式的实现或语义 · 覆盖整个 checker 的端到端路径（本把测的是
  `_validate_program_proposal` 这个函数；工作流级的 review 小节校验不在本把）· change-guidance
  的其余面 · 产品代码。
- **Triggered review policies:** local-context, change-admission
