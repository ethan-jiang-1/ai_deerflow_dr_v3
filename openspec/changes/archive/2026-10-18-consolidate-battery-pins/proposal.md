# Proposal: consolidate-battery-pins

## Why

父卡裁决 #2。电池的清单测试现在钉的是**精确计数**（负例 29 / 绿色 11 / 总 40），代价实测：

- 本会话我为它改过 **3 次**（31/12/43 → 32/13/45 → 29/11/40），每次都要同时改**三个数字和一段散文**。
- 那段散文**自己已经自相矛盾**：既写"count is 30, not the 31 quoted when the change was planned"，
  又写"the negative inventory is 32 and the green inventory is 13, 45 controls in total"——
  三个数字在同一段里打了三次架。这是**装置在向维护者收税**的典型形态。

**而它想守的那件事其实不是计数，是覆盖。** 本轮取证（第一次实测）：

| 规则 | 控制数 |
|---|---|
| adr_index · docs_scope | **各 1** ← 掉了就零覆盖 |
| backlog_underscore · doc_budgets | 各 2 |
| encoding_newline · root_counts | 各 3 |
| stale_markers | 4 |
| links | 5 |
| ledger_consistency | 18 |

**9 条规则每条都有 ≥1 控制**——所以"每规则 ≥1 控制"是一条**当前成立、且可判定**的真实不变量。
它恰好抓住了计数 pin 真正想防的那个坏情况：**某条规则失去它最后一条控制**（覆盖归零）。

顺带查到一处需要正确对待的东西：控制 `CLEAN_FIXTURE` 的 `rule` 是 `"violations"`——它不是规则名，
而是 `run_rule` 里**有意的哨兵**（`if rule == "violations": return violations(root)`，跑全套）。
新的断言必须**显式承认**这个哨兵，而不是把它当坏引用。

## What Changes

- **用不变量替换计数 pin**：`test_inventory_counts_are_pinned` → `test_every_rule_has_at_least_one_control`，
  并新增**反向**断言：除哨兵 `violations` 外，任何控制都不得指向未知规则。
- **删掉那段自相矛盾的散文**（它的全部内容是解释计数为什么是这些数）。
- 保留既有的极性断言与唯一性断言（它们守的是别的坏情况：vacuous 控制、重复 id）。

**不变量**：覆盖不变量**不退让**（且它现在被显式断言，而不是被计数间接暗示）· 其余测试不动 ·
七 checker + closeout gate + 治理套件全绿 · `--self-test` 契约不变 · 产品代码与 harness 面零改动 ·
未来增加控制**不再需要手工同步计数**（本次整理的目标之一）。

## Capabilities

### New Capabilities

<!-- none: 守卫自身测试的判据替换，不改任何产品 requirement。 -->

### Modified Capabilities

<!-- none: 同上。被守护的不变量（覆盖）不变，判据从"计数"换成"覆盖"本身。 -->

## Impact

- **改**：`openspec/tests/governance/test_doc_hygiene.py`（替换一个测试类里的断言与散文）·
  `check_code_budgets.py`（该测试文件若变短则上限**下调**）· 父卡回写。
- **不动**：任何控制与其夹具（**一条都不退役**——本把不删覆盖，只换判据）· 任何规则 ·
  产品代码 · 其余测试。
- **触发车道**：治理套件（含电池）· 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `openspec/tests/governance/test_doc_hygiene.py` 的
  `BatteryInventoryTests` —— 它拥有"控制清单没退化"这一判定。
- **Seam classification:** deterministic-guardrail —— 清单判据替换；无模型参与。
- **Question:** 一个被本会话手工同步 3 次、且自陈矛盾的计数 pin，能否换成它本来想守的**覆盖不变量**
  ——且新断言**能变红**（某条规则失去最后一条控制必须被报出），而一条控制都不退役？
- **Necessary adjacent/external contracts:** `doc_hygiene_check.RULES`（answers: 规则的权威清单）·
  电池的 `NegativeCase.rule` 字段与 `run_rule` 的 `"violations"` 哨兵（answers: 判据必须显式承认它，
  否则会把一条合法控制误判为坏引用）· `failing_controls()`（answers: 控制本身仍全部成立）。
- **Evidence seam:** 覆盖实测（9 条规则 × 控制数，adr_index/docs_scope 各仅 1 条 ⇒ 这是最该守的点）·
  **变异检查**：把某条"仅 1 控制"的规则的控制改指别处 ⇒ 覆盖断言必须红 · 治理套件 · 七 checker + closeout。
- **Not in scope:** 退役任何控制 · 计数之外的清单性质（顺序、分组）· 计数器表数量列（父卡 #9）·
  suspend 面（#5）· 毕业门/可关闭（#6）· program 模式与 portable export（#3/#4）· 产品代码。
- **Triggered review policies:** local-context, change-admission
