# Tasks

## 1. Evidence first

- [x] 1.1 Scan the application package tree with the existing algorithm before touching the rule; record the module count and whether any cycle exists (expected: 49 modules, no cycle)  ✓ 先期扫描：应用侧 **49 个模块、零环**（用现成算法扫整棵包树）——故扩围后真实树为绿。
- [x] 1.2 Record both import styles concretely: the governance directory is on `sys.path` (absolute name == sibling name), while the application package's absolute names start at `deep_research_harness/src`  ✓ 治理侧：目录在 `sys.path` 上 ⇒ 绝对名 = 同目录名。应用侧：包根在 `src/` ⇒ 绝对名从 `deerflow_deep_research.` 起。**两者不同**，是本把的核心抽象依据。

## 2. Generalise the scope

- [x] 2.1 Introduce a `Scope(module_root, absolute_base)` value and a `SCOPES` tuple holding the governance scope and the application scope, with the two fields equal for governance  ✓ `Scope(module_root, absolute_base)` + `SCOPES` 两项；治理侧两字段相同（等价于原行为）。
- [x] 2.2 Resolve absolute dotted names under `absolute_base` and relative names under the file's own package; keep only targets that land inside `module_root` (out-of-scope resolutions are ignored, never silently treated as nodes)  ✓ 绝对名在 `absolute_base` 下解析、相对名在文件自身包下解析；**只有落在 `module_root` 内的目标才算节点**（越界显式忽略）。另：点号名的每一级父包 `__init__.py` 也算被导入（Python 语义）。
- [x] 2.3 Keep `validate_no_import_cycles(root)`'s signature, its first-violation-throws behaviour, and the `import.cycle` violation shape unchanged  ✓ 签名、首次违规即抛、`import.cycle` 形状全部不变；既有 9 条用例全过。

## 3. Prove both scopes

- [x] 3.1 The governance scope's existing nine cases and the governance real-tree assertion still pass  ✓ 既有 9 条 + 治理真实树断言全过（治理侧两字段相同 ⇒ 与原行为等价）。
- [x] 3.2 Application-shaped red cases: a cycle formed by absolute imports, and a cycle spanning subpackages, are both reported  ✓ 绝对导入构成的环 → 红；跨三个子包（domain→engine→runtime→domain）的环 → 红。
- [x] 3.3 Application-shaped green cases: a one-way dependency across subpackages, and a deferred import, are not reported  ✓ 跨子包单向依赖 → 绿；跨子包延迟导入 → 绿；`src/` 下的兄弟包不算节点 → 绿。
- [x] 3.4 The application real tree is asserted clean (the evidence from 1.1 becomes a permanent test)  ✓ 新增 `ApplicationRealTreeTest` 直接断言应用侧无环（把先期取证变成永久测试）。
- [x] 3.5 A mutation check: point the application scope's `absolute_base` back at the module root and confirm the absolute-import red case stops being caught — this is the silent-failure mode the scope models exist for  ✓ **变异检查**：把应用侧 `absolute_base` 指回模块根 → **2 条失败**（绝对导入环 + 跨三子包环双双失灵）；恢复后与备份**字节一致**、15 条全过。

## 4. Ratchet and closeout

- [x] 4.1 Re-measure `cycles.py` and update its ceiling; verify the budget checker and its three tests pass  ✓ `cycles.py` 143 → **203** 行入表（超长函数 0）；闸与三条预算测试全过。
- [x] 4.2 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0  ✓ 治理套件 **230 → 236** 全绿 · 七 checker + closeout gate 全 0 · `make verify` 252。
- [x] 4.3 Confirm the application side is untouched: `git diff --stat -- deep_research_harness/` is empty  ✓ `git diff --stat -- deep_research_harness/` 为空——应用侧**只读**扫描，未改一行。
- [x] 4.4 Fill this change's `## Delivery Record` with the four required labels and the raw receipts  ✓ 见下 `## Delivery Record`。

## Delivery Record

- **外部行为**: **只增覆盖，不改判定**。治理侧 scope 的两个字段相同 ⇒ 判定与原行为等价（既有 9 条用例全过、真实树仍绿）；新增的失败面只多一个 scope：应用侧若出现模块级环，报 `ERROR [import.cycle] module-level import cycle in deep_research_harness/src/deerflow_deep_research: …` + exit 1（真实树实测绿）。应用侧代码**一行未改**（`git diff --stat -- deep_research_harness/` 为空）。
- **影响面**: `project_architecture_check/cycles.py`（143 → **203** 行：`Scope` 值对象 + `SCOPES` 两项 + 绝对/相对解析分离 + 父包链）· `openspec/tests/governance/test_import_cycles.py`（9 → **15** 条）· `check_code_budgets.py`（该文件上限跟实测 203/0）。
- **实际跑了什么**: 先期扫描（应用侧 49 模块零环）· 治理套件 exit 0（230 → **236**）· 七 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· **应用侧红/绿探针**：绝对导入环红、跨三子包环红、跨子包单向依赖绿、跨子包延迟导入绿、`src/` 兄弟包不算节点绿 · **真实树两 scope 均绿** · **变异检查**：应用侧 `absolute_base` 指回模块根 → 2 条失败（正是"全部绝对导入被静默漏掉"的形态）→ 恢复后字节一致 · 体积闸与三条预算测试全过 · harness 改动行数 0。
- **未执行的检查**: **跨 scope 的环未检测**（两个 scope 各自成图；跨治理侧与应用侧的环不存在，因为二者不是同一个包）· 未检测只经由隐式父包 `__init__.py` 达成的环？——**已覆盖**：点号名的每一级父包都算被导入（Python 语义），故这条不是缺口 · 未做自动修复 · 真实模型梯未跑（纯静态分析）。

## Deviation Register

- 偏差 1（实现缺陷，被测试当场抓出）：`_absolute_targets()` 在 `ast.Import` 分支上取了 `node.module`——`Import` 没有该属性 ⇒ `AttributeError`，真实树 checker exit 1、既有 9 条里 3 条 ERROR。修法是先按节点类型分流再取属性。**教训：把两种节点（`Import` / `ImportFrom`）合进一个取值函数时，必须先用类型分流，不能假定共有属性。**
- 偏差 2（我的测试插入脚本把新增内容删掉了，如实记录）：首次插入应用侧用例时，我用"删除第一处 `__main__` guard 到第二处"的方式去重，而这个区间**跨过了我刚追加的新用例**——文件写回后内容不变（仍 9 条），但脚本打印了"已加入"。是随后的用例计数（9 而非 16）暴露了它。修法改为**插在末尾 guard 之前**。这与我本会话前几把的同类错误（区间跨过不该删的内容）是同一个毛病，第三次。
- none: 除上述两项外无其他设计偏离。
