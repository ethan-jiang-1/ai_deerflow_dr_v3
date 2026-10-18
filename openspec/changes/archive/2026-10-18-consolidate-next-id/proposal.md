# Proposal: consolidate-next-id

## Why

父卡 `_backlog/issues/2026-10-18-governance-apparatus-consolidation.md` 的裁决 #1，证据最硬的一条：

**`Next-ID` 有两个前缀 × 3 个活声明点 = 6 处手工维护，而那个值完全可从磁盘推导。**

| 前缀 | 声明点 1 | 声明点 2 | 声明点 3 |
|---|---|---|---|
| BUG | `bugs/README.md` | `_fixed_bugs/README.md` | `_archived/README.md` 计数器表 `Next ID` 列 |
| CLS | `issues/README.md` | `_settled_issues/README.md` | 同上（同一张表的另一行） |

实测代价：**一次 bug 编号分配 = 6 个手工同步点**；本会话我做了 4 次、**3 次因漏改报错**——每一次
都是我自己漏，没有一次是仓库的真问题。错误模式是**纯噪音**。

**而且作者已经局部修过这件事两次，都没消除这一类**：
- `_archived/README.md` 头注："计数与 Next ID **唯一承载于下方状态总览表**，头注不再复述——**曾因
  复述滞留 "closed issues 19" 而与表格漂移**" ⇒ 删了一处副本。
- `doc_hygiene_check/ledger.py:278-280` 的注释："Next-ID declarations … at most one per file …
  **when a duplicated stale declaration passed while the counters table alone stayed**" ⇒ 于是加了
  一条**"检测重复声明"的检查**，而不是删掉那些副本。

**本把把这件事做完**：保留**已经被校验着的那一处**（计数器表的 `Next ID` 列，由
`_ledger_counter_problems` 与 union 推导值对账），删掉另外 4 处，并**退役只为那 4 处而存在的 5 条
电池控制**——这将是本会话**第一次让 pin 下降**。

## What Changes

- **删除 4 处手写声明**：`bugs/README.md` · `_fixed_bugs/README.md` · `issues/README.md` ·
  `_settled_issues/README.md` 各一处 `**Next available … ID: …**`。
- **四份 README 的 ritual 文字改向唯一承载处**：把"更新 Next available ID"改为"下一个编号由
  `_archived/README.md` 的状态总览表唯一承载，并与磁盘推导值对账"——**读者被指向一处**，而不是
  被要求同步多处。
- **保留**：`_archived/README.md` 计数器表的 `Next ID` 列（**已被 `_ledger_counter_problems`
  校验**，无需新逻辑）。
- **删除** `_ledger_placement_problems` 里**只服务于那 4 处副本**的声明唯一性/一致性检查块。
- **退役 5 条控制**（它们只演练被删掉的副本路径）：
  `ARCHIVE_ONLY_NEXT_ID` · `DUPLICATE_NEXT_ID_DECL` · `DISAGREEING_NEXT_ID_DECL`（负例）·
  `UNION_CONSISTENT_NEXT_ID` · `CONSISTENT_SINGLE_DECL`（绿色）⇒ **pin 32/13/45 → 29/11/40**。
- 连同其构造器一起退役（不留悬挂引用）；父卡回写本把的进展与裁决。

**不变量**：编号不撞这一**不变量本身不退让**——它继续由"计数器表 vs union 推导值"这条检查守
（`LEDGER_COUNTER_MISMATCH` 保留）· 既有其余判定只增不改 · 七 checker + closeout gate + 治理套件
全绿 · `--self-test` 契约不变 · 产品代码与 harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 账本仪轨的去重，不改任何产品 requirement。 -->

### Modified Capabilities

<!-- none: 同上。被守护的不变量（编号不撞）不变，只是承载它的事实从 6 处收敛到 1 处。 -->

## Impact

- **改**：`_backlog/{bugs,issues}/README.md` · `_backlog/_archived/{_fixed_bugs,_settled_issues}/README.md`
  （删声明 + 改 ritual 文字）· `doc_hygiene_check/ledger.py`（删声明检查块）·
  `doc_hygiene_battery/{fixtures,registry}.py`（退役 5 控制与其构造器）·
  `test_doc_hygiene.py`（pin 29/11/40）· `check_code_budgets.py`（按实测，预期**下降**）·
  父卡回写。
- **不动**：`_archived/README.md` 的计数器表（保留且仍被校验）· 产品代码 · 任何有红证的守卫 ·
  `LEDGER_COUNTER_MISMATCH` 与其余账本规则。
- **触发车道**：治理套件（含电池）· 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `_backlog/_archived/README.md` 的状态总览表 —— 它成为"下一个
  可用编号"的**唯一**承载处；`doc_hygiene_check/ledger.py` 的计数器检查是它的守卫。
- **Seam classification:** deterministic-guardrail —— 仪轨去重 + 守卫退役；无模型参与。
- **Question:** 一个被 6 处手工维护、且**只由自我漂移触发**的推导值，能否收敛到唯一一处（已被校验
  的那一处）——而"编号不撞"这条不变量**不退让**、且 pin **首次下降**？
- **Necessary adjacent/external contracts:** `_ledger_counter_problems`（answers: 唯一承载处**已经**
  被校验，故无需新逻辑）· `_ledger_placement_problems` 的声明块（answers: 要删的就是它）·
  四份 README 的 ritual 文字（answers: 它们教人同步多处，必须一起改，否则文档与实现分叉）·
  电池清单 pin（answers: 退役控制必须同步，否则测试红）。
- **Evidence seam:** 删前后真实树 `doc-layer hygiene passed.` · 编号推导仍被校验（构造"表里写错号"
  的负例仍在，`LEDGER_COUNTER_MISMATCH`）· pin 从 32/13/45 **降到 29/11/40** ·
  `failing_controls()` 为空 · 治理套件 · 七 checker + closeout。
- **Not in scope:** 计数器表的**数量**列（裁决 #9，需另行取证）· 卡片 `> 立卡/毕业门/可关闭` 字段
  （裁决 #6）· suspend 面（裁决 #5）· program 模式与 portable export（裁决 #3/#4，各自独立一把）·
  产品代码 · CAS 空转。
- **Triggered review policies:** local-context, change-admission
