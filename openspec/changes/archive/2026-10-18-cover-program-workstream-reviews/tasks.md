# Tasks

## 1. Correct the earlier premise

- [x] 1.1 Probe where the workstream-level review validation actually lives (not the caller, as I had claimed)
- [x] 1.2 Probe what it actually costs to exercise (one policy document file, not a whole tree)
- [x] 1.3 Record the corrected premise as a dated note in the earlier change's record, keeping the original text

## 2. Cover the review codes

- [x] 2.1 Add a `policies` knob to the workstream body, defaulting to the policy-free posture
- [x] 2.2 Add a helper that materializes the named policies' guidance documents in the temp root
- [x] 2.3 Seven cases, each naming its code: document missing; per policy, the record missing and the record malformed
- [x] 2.4 Keep every earlier check satisfied so each case lands on the branch it claims

## 3. Prove they are load-bearing

- [x] 3.1 Mutation: disable the workstream-level review validation and verify the affected cases fail
- [x] 3.2 Confirm the case raised elsewhere (the policy-document check) is correctly unaffected
- [x] 3.3 Restore byte-identically; verify the implementation diff is zero

## 4. Lanes and closeout

- [x] 4.1 Governance suite, seven checkers, closeout gate green; no new skip
- [x] 4.2 Confirm the product side and the harness side are untouched
- [x] 4.3 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（**我上一把把便宜的活判成了贵的活**）：`cover-program-mode-codes` 里我写"工作流级 review 校验在调用方那层、需要整棵树夹具、另开一把"。两处前提**都被探针证伪**：校验就在同一函数内（367 行），而夹具只需为每个策略造**一个**文档文件。**代价估计必须探针验证**——我因为一个没验证的估计，把一个能顺手做完的切片推迟了一把，还让记录里留下了一个错误前提。已按章程约定在归档记录里追记更正。
- 偏差 2（流程顺序，再次）：本把**先实施测试、后补 propose/design/tasks**。同一模式已在多处记录，此处如实再记。
- 正面记录：本把**主动去证伪自己上一把的结论**（而不是照着它继续"另开一把"），并因此发现它更便宜——这比"照记录办事"多花了两次探针，省下的是一整把 change。
- none: 除上述两项外无设计偏离。

## Delivery Record

- **外部行为**: **实现零改动**（`git diff --stat -- change_guidance_check/` = **0 行**）· 产品代码与 harness 面零改动。可见变化：治理套件用例数 **270 → 277**（+7，无新增 skip）。program 模式的行为一个字节没变。
- **影响面**: `openspec/tests/governance/test_change_authority.py`（夹具两处扩展 + 7 条用例）· `openspec/changes/archive/2026-10-18-cover-program-mode-codes/{tasks,design}.md`（各一条日期追记更正）。
- **实际跑了什么**: 治理套件 exit 0（**277**，无新增 skip）· 七 checker + closeout gate 全 0 · **变异**：关掉工作流级 review 校验 ⇒ **6 条**新用例红（逐条列出），第 7 条（`triggered_policy_document_missing`，在 `_triggered_policies` 中抛）**正确地不受影响**；恢复**字节一致**并复跑 277 全绿 · **实现 diff 0 行** · doc-hygiene exit 0（含被更正的归档记录）· 未跑 harness 车道（本把不触产品侧）。
- **未执行的检查**: **余下 3 个形状/取值类码未覆盖**——`control_placement_review_posture_invalid` · `control_placement_human_interaction_policy_missing` · `node_agent_review_classification_invalid`；它们要求先造**合法形状**的记录再放坏取值（需读各校验器的取值域），夹具面大一档（design D-3，**记着不做而非忘了**）· 未断言 review 记录里表格**行内容**的语义（只断言"形状/缺失"）· 未覆盖 `program.*` 之外与 program 相关的码（如 `config.program_route_missing`，属另一函数）· 未做真梯（纯静态校验）。
