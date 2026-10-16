# Tasks

## 1. Record the baseline

- [x] 1.1 Capture the pre-split facts: `failing_controls()` empty, `NEGATIVE_CASES` length 43, the 104 top-level names, the inventory pin 31/12/43, `--self-test` stdout and exit code, the suite count 221

## 2. Split the battery

- [x] 2.1 Extract `fixtures.py` (the 56 builders plus the two snippet constants they use) and `registry.py` (`NegativeCase`, `_c`, the 45 case ids, `NEGATIVE_CASES`, the four runners), with decorator spans included
- [x] 2.2 Fix the ownership of the two snippet constants: the extractor filed them by syntax (top-level assignment) rather than by use, which put `fixtures` and `registry` in a cycle; verify the package imports and the edge is one-way (`registry -> fixtures`)
- [x] 2.3 Write `doc_hygiene_battery/__init__.py` (facade) and reduce `_battery.py` to a thin re-export whose name is unchanged; verify the suite runs

## 3. Zero behaviour change, item by item

- [x] 3.1 `failing_controls()` is still empty and `NEGATIVE_CASES` still holds 43 cases
- [x] 3.2 All 104 original top-level names are reachable from `_battery`
- [x] 3.3 `--self-test` prints the same line and exits 0
- [x] 3.4 The inventory pin 31/12/43 is unchanged and the suite still runs 221 tests
- [x] 3.5 Both directions of the old cycle are gone: `_battery` does not import the entry, and the entry does not import `_battery` at module level

## 4. Ratchet, registration, closeout

- [x] 4.1 Re-measure: lower the battery's ceiling to its measured value (118) and add each new module at its own; verify the budget checker and its three tests pass — including `test_table_declares_the_largest_scripts`, which caught the unregistered module on the first run
- [x] 4.2 Register `_battery.py` (never registered before), the package directory and its three modules; verify the architecture checker exits 0 with a mutation check (move `registry.py` away, confirm `path.missing`, restore)
- [x] 4.3 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0 read directly
- [x] 4.4 Confirm `git diff --stat -- deep_research_harness/` is empty
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipts

## Deviation Register

- 偏差 1（抽取器的归属规则过窄，导致包内成环）：我按"顶层赋值 → registry"的语法规则归置那两个
  片段常量，而 fixtures 里的构造器要用它们 ⇒ `fixtures ↔ registry` 成环，导入即 `ImportError`。
  修法是按**使用者**归属（D-3）。**教训：模块归属要跟着引用走，不能只看语法形态**——这与上一把
  "装饰器不在 AST 跨度内"属同一类：工具给的形态不等于我们想要的语义。
- 偏差 2（我第二次搬移漏带同族常量）：第一次搬移只带走了 `_FENCE_LEDGER_README`，把
  `_FENCE_ORPHAN_ROW` 留在 registry，而我又删掉了 fixtures 对它的整行导入 ⇒ `NameError`。
  这是"整块搬移"与"逐名搬移"混用造成的，记在此处。
- 偏差 3（`_battery.py` 从未登记，本轮顺带补上）：它在 `required-paths.toml` 里**一直缺席**——
  名字稳定只靠约定，没有守卫。本把首次登记。
- none: 除上述三项外无其他设计偏离。

## Delivery Record

- **外部行为**: 零变化，逐项对照过：`--self-test` 输出逐字仍为 `doc-hygiene self-test passed.`（exit 0）· **43 条控制全部成立**（`failing_controls()` 为空）· `NEGATIVE_CASES` 仍 43 条且顺序未动 · **104 个原始顶层名在 `_battery` 零缺失** · 清单 pin 31/12/43 不变 · 治理套件 **221 条不增不减** · 七 checker + closeout gate 全绿 · harness 面零改动。**环两个方向都已消失**：`_battery` 不再导入入口，入口顶层不再导入 `_battery`。
- **影响面**: `_battery.py` **724 → 118 行**（薄再导出：`from doc_hygiene_battery import *` + `__all__` 104 名）· 新增 `doc_hygiene_battery/`：`fixtures.py` 419 · `registry.py` 378 · `__init__.py` 226 · `check_code_budgets.py`（电池上限 724 → **118** + 3 个新模块入表）· `required-paths.toml`（`_battery.py` 首次登记 + 包目录进目录区 + 3 个模块进文件区）。
- **实际跑了什么**: 治理套件 exit 0（221）· 七个 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· `--self-test` 直跑：输出与退出码对照 · `failing_controls()` 直跑：空 · 104 个名可达性脚本：零缺失 · **包内依赖方向检查**（`registry ← fixtures` 单边，反向无）· **环检查**（`_battery` 不导入入口、入口不导入 `_battery`）· **登记变红实测**：移走 `doc_hygiene_battery/registry.py` → `ERROR [path.missing]` exit 1 → 恢复 exit 0 · **体积表按实测重测**（电池 118 + 3 模块）且闸与三条预算测试全过，其中 `test_table_declares_the_largest_scripts` 在第一次跑时就抓到了未入表的 `fixtures.py` · harness 改动行数 0。
- **未执行的检查**: **"治理模块之间不得顶层互导"仍没有自动化守卫**——本会话连续两把各手工断掉一处环（入口↔电池、包内 fixtures↔registry），但没有任何 checker 会阻止第三处出现。这是明确的遗留缺口，应单独一把处理（可放在 `check_project_architecture.py` 的导入规则里）。· 未新增或修改任何控制 · `NegativeCase` 未重构 · 真实模型梯未跑（纯治理侧拆分）。

## 交付给 owner 的 follow-up

1. **加"治理模块不得顶层互导"的守卫**（本会话两处环都是手工发现与消除的；这是目前最明显的
   无守卫领域，且两把都撞到过）。
2. 拆分后 `doc_hygiene_battery/` 与 `doc_hygiene_check/` 共 9 个模块，若其中某个再顶格，
   可按同一形态继续下钻。
