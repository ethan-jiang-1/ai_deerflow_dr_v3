# Tasks

## 1. Evidence first

- [x] 1.1 Enumerate the program-form codes exactly and separate the real ones from a grep prefix
- [x] 1.2 Read each remaining code's trigger, including the order in which the checks run
- [x] 1.3 Confirm the caller-level half needs a whole-tree fixture and belongs in another change

## 2. Cover the twelve

- [x] 2.1 Turn the fixture into knobs so each case reads as "compliant plus one malformation"
- [x] 2.2 Add the twelve cases, each naming its own code
- [x] 2.3 Keep the canonical green case and the first four cases intact
- [x] 2.4 Keep every earlier check satisfied so each case lands on the branch it claims

## 3. Prove they are load-bearing

- [x] 3.1 Mutation: disable the owner-duplicate check and verify that case fails
- [x] 3.2 Mutation: disable the stable-ID shape check and verify that case fails
- [x] 3.3 Restore byte-identically and re-run the suite
- [x] 3.4 Verify the implementation diff is zero lines

## 4. Lanes and closeout

- [x] 4.1 Governance suite, seven checkers, closeout gate green; no new skip
- [x] 4.2 Confirm the product side and the harness side are untouched
- [x] 4.3 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（**夹具必须让更早的检查通过**）：`candidate_id_invalid` / `candidate_id_duplicate` 两条我一开始写了 `both=False`（只留一个工作流），结果更早的"工作流数量"检查先报 `program.workstream_count_invalid`，把要验的码挡在后面。修法是保留两个工作流、只把 alpha 的候选 ID 写畸形。**教训：要验第 N 条检查，夹具必须满足前 N−1 条——"最小复现"在这里反而是错的。**
- 偏差 2（**变异没施加与测试空洞，输出一模一样**）：变异 A 第一次因锚点缩进不匹配**没有施加**（锚点断言失败、脚本中止），而套件照样报 `OK`。那一刻 `OK` 既可能是"变异没生效"也可能是"测试没价值"，**含义相反、输出相同**。修法是用正则取真实缩进重做，并核对"哪条用例红了"。**教训：变异检查必须证明"变异已施加"，否则它在证伪自己。**
- 正面记录：本把**先写 propose/design/tasks、后实施**，没有再犯本会话反复出现过的顺序问题。
- none: 除上述两项外无设计偏离。

## Delivery Record

- **外部行为**: **实现零改动**（`git diff --stat -- change_guidance_check/` = **0 行**）· 产品代码与 harness 面零改动。可见变化只有治理套件用例数：**258 → 270**（+12）。program 模式的行为一个字节都没变——本把证明的是"它本来就按这些码拒绝，只是此前没人逐码验过"。
- **影响面**: `openspec/tests/governance/test_change_authority.py`（夹具旋钮化 + 12 条用例；既有 4 条只改了一处参数名）。未动 `check_code_budgets.py`（该测试文件不在体积表内）、未动任何实现。
- **实际跑了什么**: 治理套件 exit 0（**270**，无新增 skip）· 七 checker + closeout gate 全 0 · **变异双向**：关掉 owner 重复检查 ⇒ `test_a_duplicate_workstream_owner_is_reported` 红；关掉 stable ID 形状检查 ⇒ `test_an_invalid_workstream_id_is_reported` 红；两次均恢复**字节一致**并复跑 270 全绿 · **实现 diff 0 行** · 未跑 harness 车道（本把不触产品侧；`make verify`/`smoke` 在上一把已绿且本把不涉）。
- **未执行的检查**: **调用方那层未覆盖**——`validate(root)` 里的工作流级 review 小节校验需要**整棵树**夹具（config + change-guidance 树 + product 文档；`test_project_gate.py` 有该模式可复用），**明确移出本把范围**（design D-4），需另开一把
> **追记（2026-10-18）**：本句的**两条前提都被证伪**——① 那段校验**不在调用方**，就在`_validate_program_proposal` 内部（第 367 行 `_validate_selected_policy_reviews(..., review_level=4, code_prefix="program.workstream")`）；② 它**不需要整棵树**，只需为所声明的策略各造**一个** `POLICY_REGISTRY[policy].path` 文档（几字节）。已由 change `cover-program-workstream-reviews` 落地（7 条用例覆盖 7 个码）。 · 未断言错误消息里的**定位信息**（`detail` 含路径）——那由既有用例覆盖 · 未覆盖 `program.*` 之外的 program 相关码（如 `config.program_route_missing`，它属另一函数）· 未做真梯（纯静态校验）。
