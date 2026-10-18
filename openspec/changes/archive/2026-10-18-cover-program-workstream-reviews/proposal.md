# Proposal: cover-program-workstream-reviews

## Why

`cover-program-mode-codes` 覆盖了 program 模式**函数内**的 12 个码，并把"工作流级 review 小节校验"
记为**未覆盖**，理由是它"在调用方那层、需要整棵树夹具、另开一把"。**这两条理由都是错的**，本把纠正
并把它做完：

| 我上一把的判断 | 实测 |
|---|---|
| "在**调用方那层**（`validate(root)`）" | **在同一函数内**：`_validate_program_proposal` 第 367 行调 `_validate_selected_policy_reviews(..., review_level=4, code_prefix="program.workstream")` |
| "需要**整棵树**夹具" | **只需为所声明的策略各造一个文档路径**：`POLICY_REGISTRY[policy].path`（几字节） |

触发链（已逐条探针验证）：工作流声明一个**真实策略** → `_triggered_policies` 要求该策略的**指导文档
存在于 root** → 文档在场后，按策略要求一份**level-4** 的 review 记录（普通提案是 level 2）→ 记录缺失
或形状畸形各有其码。

## What Changes

- **夹具两处扩展**：`_workstream_body(..., policies=…)` 旋钮（默认仍是 `none: <理由>`），
  以及 `_raise_with_documents(text, policies)`——为命名策略在临时 root 里造出它们的文档路径。
- **新增 7 条用例**，逐码指名：
  `program.workstream_triggered_policy_document_missing` ·
  `program.workstream_control_placement_review_{missing,shape_invalid}` ·
  `program.workstream_workflow_outcome_review_{missing,shape_invalid}` ·
  `program.workstream_node_agent_review_{missing,shape_invalid}`。
- **按账本约定追记** `cover-program-mode-codes` 的归档记录：把上面**两条错误判断**就地更正（保留原文 +
  日期注记），免得后来者照着"要整棵树"的错误前提再判断一次。
- **实现零改动**：`git diff --stat -- change_guidance_check/` 必须为 0 行。

**不变量**：实现与镜像零改动 · 七 checker + closeout gate + 治理套件全绿 · 不新增 skip ·
产品代码与 harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 只补测试覆盖并更正一条记录。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`openspec/tests/governance/test_change_authority.py`（夹具 + 7 条用例）·
  `openspec/changes/archive/2026-10-18-cover-program-mode-codes/{tasks,design}.md`（追记更正）。
- **不动**：`change_guidance_check/` 的任何实现 · 产品代码 · 治理侧其他规则。
- **触发车道**：治理套件 · 七 checker。

## Change Focus

- **Primary module / causal owner:** `openspec/tests/governance/test_change_authority.py` 的
  `ProgramModeTests` —— program 模式的直接覆盖面；本把补上它最后的**工作流级 review** 一段。
- **Seam classification:** deterministic-guardrail —— 补测试覆盖 + 更正记录；无模型参与。
- **Question:** 一段被上一把判为"跨层、昂贵、另开一把"的校验，能否被证明**既在同一函数内、又只需
  每个策略一个文档路径**——并在不改实现的前提下被逐码覆盖？
- **Necessary adjacent/external contracts:** `_triggered_policies`（answers: 声明真实策略会要求该策略
  的**文档**存在于 root，缺失即 `…_triggered_policy_document_missing`）· `POLICY_REGISTRY`
  （answers: 策略 → 文档路径的唯一映射，夹具据此造文件）· `_REVIEW_RECORDS`（answers: 策略 → 需要的
  记录标题，**裸标题**再按 level 拼前缀）· `review_level=4`（answers: program 工作流的 review 记录是
  **level-4** 标题，普通提案是 level 2——这个区别正是它容易写错的地方）。
- **Evidence seam:** 7 条新用例逐条绿并指名 code · **变异**：关掉工作流级 review 校验 ⇒ 其中 **6 条红**
  （第 7 条在 `_triggered_policies` 里抛，正确地不受影响）· 实现 diff = 0 · 治理套件用例数增长 ·
  七 checker / closeout。
- **Not in scope:** 余下 3 个**形状/取值类**码——`control_placement_review_posture_invalid` ·
  `control_placement_human_interaction_policy_missing` · `node_agent_review_classification_invalid`
  ——它们要求先造出**合法形状**的记录再放一个坏取值（需读各校验器的取值域），夹具面更大；如实记为
  未覆盖并写明理由。· 改实现 · 产品代码。
- **Triggered review policies:** local-context, change-admission
