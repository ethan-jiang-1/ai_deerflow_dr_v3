# Tasks

## 1. Evidence first

- [x] 1.1 Map every live Next-ID carrier (per prefix) and confirm which one is already validated by the counters rule  ✓ 两个前缀各 3 个活声明点 = 6；其中**唯一已被校验**的是 `_archived/README.md` 计数器表的 `Next ID` 列（`_ledger_counter_problems` 的 docstring 原文：“matches the disk roster and the union-derived next ID”）。
- [x] 1.2 Identify exactly which rule block and which battery controls exist only to police the hand-written copies  ✓ 只服务于副本的是 `_ledger_placement_problems`（函数体**纯粹**是声明唯一性 + 与推导值一致）；只演练它的是 5 条控制（3 负例 + 2 绿色）。
- [x] 1.3 Record how many manual sync points one bug-ID allocation costs today, and how often this session it failed (all self-inflicted)  ✓ 一次 bug 分配 = **6 个手工同步点**；本会话 4 次分配、**3 次因漏改报错**，全部是自伤。

## 2. Collapse the carriers

- [x] 2.1 Delete the four hand-written declarations (bugs, fixed-bugs, issues, settled-issues READMEs), leaving the counters table's `Next ID` column  ✓ 删四处声明（bugs / _fixed_bugs / issues / _settled_issues 的 README），计数器表不动；删后 `doc-layer hygiene passed.`——**证明保留的那一处确实在守**。
- [x] 2.2 Rewrite the ritual prose in all four READMEs to point at the single carrier and say the value is reconciled against the derived allocation — so a later reader sees deliberate removal, not an omission  ✓ 四份 README 的 ritual 文字改向唯一承载处，并写明“2026-10-18 由 consolidate-next-id 删除此处副本，6 处手写只带来漂移”——后来者能看出是有意为之。
- [x] 2.3 Delete the declaration-uniqueness/agreement block in the ledger rule (its only subject was the deleted copies)  ✓ 删掉 `_ledger_placement_problems`（−39 行）及其在 `rules.py` 的调用与导入、在包门面的导出。

## 3. Retire the controls that only exercised the copies

- [x] 3.1 Retire the three negative and two green controls with their fixtures, leaving no dangling references  ✓ 退役 5 条控制与其构造器，无悬挂引用（迭代清理夹具引用；见偏差 1）。
- [x] 3.2 Sync the inventory pins and their prose to 29/11/40  ✓ pin 按**实测极性**同步：32/13/45 → **29/11/40**。
- [x] 3.3 Verify the keeper still fires: a wrong Next-ID in the counters table must still be reported (the `LEDGER_COUNTER_MISMATCH` control), and `failing_controls()` is empty  ✓ 保留的 `LEDGER_COUNTER_MISMATCH` 仍在演练（表里写错号必须报）；`failing_controls()` 为空（40 条全部成立）。

## 4. Ratchet and closeout

- [x] 4.1 Re-measure the touched files and update the budget table; verify the budget checker and its three tests pass (the overall budget should go **down**)  ✓ 体积表按实测重测，且**首次下降**：受管文件总行数 **6502 → 6443（−59）**（ledger −41 · registry −15 · __init__ −2 · rules −1）；闸与三条预算测试全过。
- [x] 4.2 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0  ✓ 治理套件 exit 0（**257 → 252**，见偏差 2）· 七 checker + closeout gate 全 0 · `make verify` 252。
- [x] 4.3 Confirm the real tree passes and the invariants held: numbering still cannot collide (the counters check is intact), no existing judgement weakened, no product code touched  ✓ 真实树 `doc-layer hygiene passed.`；“编号不撞”由计数器表 vs union 推导值的检查继续守（未削弱）· 其余判定只增不改 · 产品代码与 harness 面零改动（diff 为空）。
- [x] 4.4 Write this change's progress and verdict back into the parent card  ✓ 已回写父卡（裁决 #1 标记为已执行，含 −59 行与 pin 下降两个正面信号）。
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipts  ✓ 见下 `## Delivery Record`。

## Delivery Record

- **外部行为**: **被守护的不变量不退让**——“编号不撞”继续由 `_ledger_counter_problems`（计数器表的 `Next ID` 列 vs union 推导值）守，且 `LEDGER_COUNTER_MISMATCH` 仍在演练。变化只发生在**承载事实的地方**：下一个可用编号从 6 处手写收敛到 1 处（已被校验的那一处）。删声明后真实树 `doc-layer hygiene passed.`。治理套件用例数 **257 → 252**（−5，随退役控制一并消失，见偏差 2）。产品代码零改动，harness 面零改动。
- **影响面**: `_backlog/{bugs,issues}/README.md` 与 `_backlog/_archived/{_fixed_bugs,_settled_issues}/README.md`（各删一处声明 + ritual 文字改向唯一承载处）· `doc_hygiene_check/ledger.py`（删 `_ledger_placement_problems`，−41 行）· `doc_hygiene_check/rules.py`（去调用与导入）· `doc_hygiene_check/__init__.py`（去导出）· `doc_hygiene_battery/{registry,fixtures}.py`（退役 5 控制与其构造器）· `test_doc_hygiene.py`（pin 29/11/40）· `check_code_budgets.py`（四处**下调**）· 父卡回写。
- **实际跑了什么**: 删声明后 `doc-layer hygiene passed.`（证明保留处仍在守）· `failing_controls()` 为空（**40 条控制**全部成立）· 治理套件 exit 0（252）· 七 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· 体积闸与三条预算测试全过，**受管文件总行数 6502 → 6443（−59）**——本会话**首次下降** · harness 改动行数 0。
- **未执行的检查**: **计数器表的“数量”列未处置**（父卡裁决 #9：它同样是“声明 vs 磁盘”，但守的是“静默删卡”，需另行取证）· `毕业门`/`可关闭` 字段（裁决 #6）· suspend 面（裁决 #5）· program 模式与 portable export（裁决 #3/#4，各自独立一把）· 未统计“一次 CLS 编号分配”的同步点（issue 卡在毕业时才分配编号，路径与 bug 不同）。

## Deviation Register

- 偏差 1（**我的“未引用夹具”修剪启发式有错，被电池当场抓出**）：清理退役控制的夹具时，我只在 `registry.py` 与包门面里数引用，**没有数 `fixtures.py` 内部**——于是删掉了被另外两个夹具调用的共享助手 `_fix_reference_repo`，`failing_controls()` 立刻 `NameError`。已恢复该函数（连同它注释里那条“负例不能建目录”的陷阱说明）。**教训：判“死代码”必须把同文件内的引用一起数**；而这次是**电池自己**抓到了我对电池的破坏，机制是有效的。
- 偏差 2（套件用例数下降是**有意**的，必须写明以免被读成覆盖丢失）：257 → 252。退役的 5 条控制各自有一条用例，它们演练的是**已删除的代码路径**；留着会变成 vacuous（负例必失败、绿色空洞通过）。这是父卡“不必要的剔除”的直接体现，不是覆盖退化。
- 偏差 3（正面的第一条）：**本会话首次让棘轮下降**——受管文件总行数 −59，`check_code_budgets.py` 四处下调。此前每一把都只增不减。
- none: 除上述三项外无其他设计偏离。
