# Design

## Context

证据见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 声明点 | 2 前缀 × 3 = 6（本会话 13 处提及 / 6 文件） |
| 一次 bug 分配的同步点 | **6**；本会话 4 次分配、**3 次漏改报错**（全为自伤） |
| 唯一**已被校验**的一处 | `_archived/README.md` 计数器表的 `Next ID` 列 —— `_ledger_counter_problems` 的 docstring 原文："matches the disk roster and the **union-derived next ID**" |
| 只服务于副本的检查 | `_ledger_placement_problems` 的声明块（唯一性 + 与推导值一致），其注释自陈动机是"重复的陈旧声明混过去" |
| 只演练副本路径的控制 | 5 条（3 负例 + 2 绿色） |

## Goals / Non-Goals

**Goals:** 声明收敛到唯一一处（且已在校验中）· 退役只为副本存在的检查与控制 · **pin 首次下降** ·
"编号不撞"不变量不退让 · 文档 ritual 与实现同向。

**Non-Goals:** 计数器表的数量列 · 卡片字段 · suspend 面 · program 模式 / portable export ·
产品代码。

## Decisions

### D-1｜保留哪一处：**已经被校验的那一处**

- **选**：`_backlog/_archived/README.md` 计数器表的 `Next ID` 列（每前缀一行）。
- **为什么**：它是**唯一已经在被校验**的承载处（`_ledger_counter_problems` 与 union 推导值对账），
  也是**作者自己头注声明为唯一承载**的地方。保留它 ⇒ **本把不需要新增任何校验逻辑**，只是停止
  手工维护其余 4 处。若改选活跃面 README 为唯一处，则要**新写**校验（把表列也算进来），成本更高、
  且与作者已声明的权威位置冲突。
- **代价**：立卡的人要在表里看下一个号（一次跳转）。
- **换来**：零新增逻辑；一处声明、一处校验。

### D-2｜删的是 4 处**手写副本**，不是"删除这个字段"

- **选**：删 `bugs/README.md` · `_fixed_bugs/README.md` · `issues/README.md` ·
  `_settled_issues/README.md` 各一处声明；**不改**计数器表。
- **为什么**：不变量（编号不撞）由推导 + 表校验守住；副本只带来漂移。
- **代价**：四份 README 的 ritual 文字要一起改（否则文档教人同步多处，与实现分叉）。
- **换来**：6 → 1。

### D-3｜退役控制而非保留成"vacuous green"

- **选**：5 条控制与其构造器一起退役，pin 32/13/45 → **29/11/40**。
- **为什么**：它们演练的是**被删掉的代码路径**。留着会变成 **vacuous**（负例会失败、绿色的会
  空洞通过）——而"空洞通过的控制"比没有控制更坏（它谎称有覆盖）。电池自己的
  `test_every_control_declares_its_polarity` 就是防这类东西的。
- **代价**：PIN 下调需要同步散文；`UNION_CONSISTENT_NEXT_ID` 的"union 一致"语义**并未消失**
  ——它由 `LEDGER_COUNTER_MISMATCH` 继续覆盖（表的 `Next ID` 列就是 union 推导值）。
- **换来**：控制集与真实代码路径一致；**pin 首次下降**（本会话一直只增）。

### D-4｜把"为什么删"写进四处 README，而不是让它看起来像漏写

- **选**：四份 README 的 ritual 文字改为指向唯一承载处，并**写明编号由表 + 推导对账**。
- **为什么**：父卡的硬约束——后来者要能看出这是**有意为之**。一份"少了那一行"的 README 会被
  下一个人"补回来"，那才是真正的失败。
- **换来**：去重不会自行回滚。

## Risks / Trade-offs

- [删了声明导致某处消费者读不到] → 唯一消费者是 `_ledger_placement_problems` 的声明块，它同时删除；
  计数器表的读取路径不动。
- [编号不变量被削弱] → `LEDGER_COUNTER_MISMATCH` 保留且仍演练（表里写错号必须报）——本把**以该
  负例仍红**为验收。
- [pin 下调被误读为"放宽守卫"] → 退役的 5 条只覆盖已删路径；本把在 Delivery Record 与父卡写明
  理由与保留的覆盖。
- [四处 README 的 ritual 文字漏改] → doc-hygiene 会因索引/计数/放置规则发现不一致；且 tasks 里
  逐处列出。

## Migration Plan

1. 删四处声明 + 改四处 ritual 文字。
2. 删 `_ledger_placement_problems` 的声明块。
3. 退役 5 条控制与其构造器；pin 29/11/40 + 散文同步。
4. 体积表按实测（预期**下降**）；门禁；父卡回写；收口。

**回滚**：撤销 diff（声明恢复、检查块恢复、控制与 pin 恢复）。
