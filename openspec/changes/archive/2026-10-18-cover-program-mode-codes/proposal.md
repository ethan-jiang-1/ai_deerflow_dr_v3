# Proposal: cover-program-mode-codes

## Why

`cover-program-mode` 给了被保留的 program 模式**第一批**覆盖（正典绿例 + 4 个码），并如实记下缺口：
**17 个匹配里 16 个是真码，只覆盖了 4 个**。本把补上**剩下 12 个**——它们**全部**落在
`_validate_program_proposal` 内部，每个只需一个夹具旋钮 + 一条断言具体 code 的用例。

清单（含触发条件，均已取证）：

| 码 | 触发 |
|---|---|
| `candidate_budget_invalid` | program 预算里有空项（`c1, , c2`） |
| `candidate_budget_duplicate` | program 预算里重复标识（`c1, c1`） |
| `candidate_budget_mismatch` | 预算**不等于**各工作流候选 ID 的并集 |
| `candidate_id_invalid` | 某工作流的候选 ID 列表有空项 |
| `candidate_id_duplicate` | 候选 ID 在同一/跨工作流重复 |
| `workstream_field_missing` | 工作流少一个 `WORKSTREAM_FIELDS` |
| `workstream_id_duplicate` | 两个工作流用同一 stable ID |
| `workstream_id_invalid` | stable ID 不合 `[a-z][a-z0-9-]*`（如大写） |
| `workstream_legacy_triggered_policies_field_present` | 工作流里出现**旧字段名** `Triggered charter policies` |
| `workstream_order_duplicate` | 声明顺序里有重复 ID |
| `workstream_order_invalid` | 声明顺序里的 ID 不合 `WORKSTREAM_ID_PATTERN` |
| `workstream_owner_duplicate` | 两个工作流声明同一个 `Primary module / causal owner` |

## What Changes

- **重构夹具**：`_workstream_body` 支持 `drop=`（删一个字段）与 `extra=`（追加一行）；
  `_program_proposal` 支持 `budget=`、两个工作流的 id 与 body 覆盖。**既有 4 条用例的参数语义不变**
  （正典绿例仍是绿例）。
- **新增 12 条用例**，每条断言**具体 code**（与既有 4 条同风格：直接调 `_validate_program_proposal`）。
- **实现零改动**：`git diff --stat -- change_guidance_check/` 必须为 0 行——本把只补覆盖。

**不变量**：实现与镜像零改动 · 七 checker + closeout gate + 治理套件 + `make verify`/`smoke`/lint 全绿 ·
**不新增 skip** · 产品代码与 harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 只补测试覆盖。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`openspec/tests/governance/test_change_authority.py`（夹具重构 + 12 条用例）。
- **不动**：`change_guidance_check/` 的任何实现 · 任何规则语义 · 产品代码 · 治理侧其他规则。
- **触发车道**：治理套件 · 七 checker。

## Change Focus

- **Primary module / causal owner:** `openspec/tests/governance/test_change_authority.py` 的
  `ProgramModeTests` —— 它拥有 program 模式的直接覆盖面。
- **Seam classification:** deterministic-guardrail —— 补测试覆盖；无模型参与。
- **Question:** 一个被保留、**有真实用户**却**只覆盖了 4/16 个违规码**的模式，能否在不改实现的前提下
  把剩下 12 个**逐码**覆盖——且每条都能指名自己的 code？
- **Necessary adjacent/external contracts:** `_comma_separated_values`（answers: invalid = 空项、
  duplicate = 重复；两者的**先后**决定了哪些输入触发哪个码）· `_workstream_sections`（answers:
  stable ID 必须先有空格且合 `WORKSTREAM_ID_PATTERN`；重复另有码）· `LEGACY_TRIGGERED_POLICIES_FIELD`
  （answers: 旧字段名是 `Triggered charter policies`）· `WORKSTREAM_FIELDS`（answers: 12 个字段，
  删任意一个即 `workstream_field_missing`）。
- **Evidence seam:** 12 条新用例逐条绿并指名 code · 既有 4 条（含正典绿例）不回归 ·
  `failing_controls` 无关（这是测试不是电池）· 治理套件用例数增长 · **实现 diff = 0** ·
  `make verify` / `smoke` / lint / 七 checker / closeout。
- **Not in scope:** **调用方那层**（`validate(root)` 里的工作流 review 小节校验）——它需要**整棵树**
  夹具（config + change-guidance 树 + product 文档，`test_project_gate.py` 有该模式可复用），成本明显
  更高；本把先做便宜且穷尽的一半，贵的那半**另开一把**并在交付记录里写明。· 改实现 · 产品代码。
- **Triggered review policies:** local-context, change-admission
