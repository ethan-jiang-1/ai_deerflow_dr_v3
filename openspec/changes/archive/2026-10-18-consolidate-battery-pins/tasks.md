# Tasks

## 1. Evidence first

- [x] 1.1 Measure the rule-to-control map from the battery and the rule registry: how many controls each rule has, and which rules have only one  ✓ 实测规则→控制图：adr_index 1 · docs_scope 1 · backlog_underscore 2 · doc_budgets 2 · encoding_newline 3 · root_counts 3 · stale_markers 4 · links 5 · ledger_consistency 18 —— **9 条规则每条 ≥1**，故覆盖是**当前成立**的不变量；而 adr_index/docs_scope **各仅 1 条**，删掉即零覆盖（最该守的点）。
- [x] 1.2 Confirm the count pin's cost this session (how many times it was hand-synced) and read the prose it carries  ✓ 本会话为计数 pin 手工同步 **3 次**（31/12/43 → 32/13/45 → 29/11/40）；它带的散文自陈矛盾：既写「count is 30, not the 31 quoted when the change was planned」又写「29…11…40」。
- [x] 1.3 Identify any control whose `rule` is not a rule name, and determine whether it is a defect or a documented sentinel  ✓ 找到一处非规则名：`CLEAN_FIXTURE` 的 `rule == "violations"`。它不是坏引用，而是 `run_rule` 里**有意的哨兵**（`if rule == "violations": return violations(root)`，跑全套）。

## 2. Swap the criterion

- [x] 2.1 Replace the exact-count assertion with a coverage assertion: every rule has at least one control, and the rule set is non-empty  ✓ 换成 `test_every_rule_has_at_least_one_control`：`set(规则) - set(控制指向)` 必须为空，且**规则集非空**（否则会空洞通过）。
- [x] 2.2 Add the converse assertion: no control names an unknown rule, with the documented sentinel acknowledged explicitly as a named constant  ✓ 反向断言 `test_no_control_names_an_unknown_rule`，哨兵以具名常量 `WHOLE_CHECKER` 显式承认（不误伤那条合法控制）。
- [x] 2.3 Delete the now-obsolete count prose and record the deliberate trade-off (a redundant control's loss is no longer asserted) in the docstring  ✓ 删掉整段计数散文；把**有意的取舍**写进 docstring：冗余控制的丢失不再被断言捕获（它不改变任何规则的可测性且在 review 里是显式 diff），而计数 pin 为这点保障向每一次**新增**收税。
- [x] 2.4 Keep the polarity and identifier-uniqueness assertions untouched; retire no controls  ✓ 极性断言与唯一性断言未动；**一条控制也没退役**（控制总数保持 40 不变：本把不动控制集）。

## 3. Prove it can go red

- [x] 3.1 Mutation check: point the only control of a single-control rule at another rule and verify the coverage assertion fails  ✓ **变异 1**：把 adr_index 的唯一控制改指 links ⇒ 覆盖断言红，报 `rules with no control at all: ['adr_index']`。
- [x] 3.2 Mutation check: make a control name an unknown rule and verify the converse assertion fails  ✓ **变异 2**：把一条 links 控制改指拼错的 `lnks` ⇒ 覆盖仍成立而**反向断言红**，报 `controls targeting rules that do not exist: ['lnks']`（同时 `run_rule` 抛 KeyError——未知规则连跑都跑不起来，属纵深防御）。
- [x] 3.3 Restore and verify the battery's own `failing_controls()` is empty  ✓ 两次变异后均与备份**字节一致**；`failing_controls()` 为空（40 条控制全部成立）。

## 4. Ratchet and closeout

- [x] 4.1 Re-measure the touched test file and update its ceiling if it moved; verify the budget checker and its three tests pass  ✓ 本把只动测试文件（不在体积表内——表只管治理实现文件）；闸与三条预算测试全过，**无新增上调**。
- [x] 4.2 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0  ✓ 治理套件 exit 0（**252 → 253**，见偏差 1）· 七 checker + closeout gate 全 0 · `make verify` 252。
- [x] 4.3 Confirm no control was retired, no rule changed, no product code touched, and the coverage invariant is now asserted directly  ✓ 控制零退役 · 规则零改动 · 产品代码与 harness 面零改动（diff 为空）· 覆盖不变量现在**被直接断言**，而不再由计数间接暗示。
- [x] 4.4 Write this change's progress and verdict back into the parent card  ✓ 已回写父卡（裁决 #2 标记为已执行）。
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipts  ✓ 见下 `## Delivery Record`。

## Delivery Record

- **外部行为**: **控制集一条未动、规则一条未改**——变的只是"清单没退化"的判据：从精确计数（29/11/40）换成覆盖不变量（每个规则 ≥1 控制）+ 反向断言（不得指向未知规则，哨兵 `violations` 显式承认）。测试数 **252 → 253**。对外不可见的行为变化：**未来新增控制不再需要手工同步计数**；可见的行为变化：某条规则失去**最后一条**控制时，现在会明确报出"哪条规则零覆盖"（此前只报"计数变了"）。
- **影响面**: `openspec/tests/governance/test_doc_hygiene.py`（`BatteryInventoryTests`：换断言 + 删自相矛盾散文 + 取舍写进 docstring；新增包引用一行）· 父卡回写。**未动**：任何控制与其夹具 · 任何规则 · `check_code_budgets.py`（该测试文件不在表内，无需调整）。
- **实际跑了什么**: 覆盖实测（9 规则 × 控制数）· 两次**变异检查**（adr_index 失覆盖 → 红并指名；links 控制指向 `lnks` → 反向断言红并指名）· 变异后恢复与备份**字节一致** · `failing_controls()` 为空（40 条）· 治理套件 exit 0（253）· 七 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· 体积闸与三条预算测试全过 · harness 改动行数 0。
- **未执行的检查**: 未断言**控制顺序/分组**等清单性质（父卡未列，且无证据表明它们重要）· 未给"冗余控制丢失"加任何替代断言（**这是 D-2 明说的有意取舍**，已写进 docstring）· 父卡其余裁决项（计数器表数量列 · suspend 面 · 毕业门/可关闭 · program 模式 · portable export）各自独立一把 · 真实模型梯未跑（纯清单判据）。

## Deviation Register

- 偏差 1（用例数 +1，属预期）：252 → 253。我把一个测试方法拆成两条断言（覆盖 + 反向），净 +1。与上一把"退役控制导致 −5"不同，这次**没有任何覆盖被移除**。
- 记录一条**有意的取舍**（不是偏差，但必须留在案）：本把放弃了"冗余控制的丢失被断言捕获"这一微末保障。理由已在 design D-2 与测试 docstring 写明——那种丢失**不改变任何规则的可测性**，且在 git 里是显式 diff；而计数 pin 为它向**每一次新增**收税（本会话 3 次，且散文已自相矛盾）。**这是判据与不变量对齐，不是放宽守卫。**
- none: 除上述两项外无其他偏离；本轮未出现前几把的脚本级失误（嵌套引号/重复节）。
