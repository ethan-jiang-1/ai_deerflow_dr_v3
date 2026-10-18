# Tasks

## 1. Evidence first

- [x] 1.1 Confirm the mode's test coverage is zero, and that the only mentions of its heading under `openspec/tests/` belong to a different rule's fixtures
- [x] 1.2 Read the program validation entry and the field constants it requires (program fields, workstream fields, the workstream minimum, the order/budget agreements)
- [x] 1.3 Confirm the implementation is not to be touched: this change is coverage only

## 2. Canonical coverage

- [x] 2.1 Add a fixture builder for a compliant program proposal (program section + two workstreams + agreements)
- [x] 2.2 Green case: a compliant program proposal passes — the mode's first evidence that it accepts correct input
- [x] 2.3 Red cases, each asserting a specific code: single workstream, workstreams before the program heading, a missing program field, a declared order that disagrees
- [x] 2.4 Call the validation entry directly, matching the file's established style, and state the resulting scope boundary in the docstring

## 3. Prove the tests are load-bearing

- [x] 3.1 Mutation check: change the workstream minimum and verify the new cases fail; restore byte-identically
- [x] 3.2 Verify the implementation diff is zero lines — coverage was added, the subject was not changed

## 4. Ratchet and closeout

- [x] 4.1 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0
- [x] 4.2 Record the three constraints the fixture iteration revealed, and the drafting leftover that was cleaned
- [x] 4.3 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（**夹具迭代三次——这本身就是本把的证据**）：我写合规 program 提案时连撞三条**读代码也没看出来的**隐含约束：① `Program Focus` 有 **8** 个字段，不是 4 个（我读了常量的前四行就动手）；② `Seam classification` 必须**在值后给简短理由**（`wiring —— …`）；③ program 的 `Candidate / obligation budget` 必须**恰好等于**各工作流 `Candidate / obligation ID` 的并集。**三条都是校验器在报错里教我的**——而"没人知道这个模式的契约"正是**零覆盖**的直接后果。这条偏差同时是本把最有力的存在理由。
- 偏差 2（起草残留，本次会话第二次）：夹具里留了一句 `... if False else ...` 的死分支（起草时用来试两种顺序），提交前清掉。前一次同类是 `test_ledger_graduation.py` 里的 `if False else None`。教训同前：占位要么立刻删、要么写成真断言。
- none: 除上述两项外无设计偏离。

## Delivery Record

- **外部行为**: **实现零改动**（`git diff --stat -- openspec/governance/change_guidance_check/` = **0 行**）· 产品代码与 harness 面零改动。唯一的可见变化是测试：治理套件用例数 **253 → 258**（+5）。program 模式的行为一个字节都没变——本把证明的是"它本来就能正确受理合规输入，只是此前没人验证过"。
- **影响面**: `openspec/tests/governance/test_change_authority.py`（新增 `ProgramModeTests` 5 条 + 两个夹具构造函数；导入加 `_validate_program_proposal`）· 未动 `check_code_budgets.py`（该测试文件不在体积表内）。
- **实际跑了什么**: 绿例（合规 program 提案通过——此前**零覆盖**）· 四条红例各断言具体 code（`program.workstream_count_invalid` · `program.mode_invalid` · `program.field_missing` · `program.workstream_registration_mismatch`）· **变异检查**：工作流下限 2→3 ⇒ 新用例 **3 条失败**（绿例 + 两条红例），证明用例**承重**；恢复后与备份**字节一致** · 治理套件 exit 0（**258**）· 七 checker 逐个 exit 0 · closeout gate exit 0 · **实现 diff 0 行** · harness 改动 0 行 · 未跑 `make verify`（本把不触产品侧；`make verify` 与 `openspec/**` 无关）。
- **未执行的检查**: **未覆盖整条端到端链路**——本把测的是 `_validate_program_proposal` 这个函数；**工作流级的 review 小节校验在调用方**（`_triggered_policies` 之后的分支），不在本把 · **未覆盖该模式的全部违规码**——实测该模式共有 **17 个 `program.*` 码**，本把覆盖其中 **4 个**（`workstream_count_invalid` · `mode_invalid` · `field_missing` · `workstream_registration_mismatch`）+ 一条正典绿例；其余 13 个码各自的夹具成本更高，留给将来按需补· 未验证 `2026-10-07-surface-runtime-structure` 那份真实 program 提案在今天的校验下是否仍合规（它已归档、不再被校验）· 真实模型梯无关（纯静态校验）。
