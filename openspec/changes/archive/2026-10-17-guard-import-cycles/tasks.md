# Tasks

## 1. Reconnaissance before writing the rule

- [x] 1.1 Confirm the orchestration seam (`facade.validate_project` plus the `--imports-only` branch) and the violation shape (`ContractViolation` -> `ERROR [code] detail`, exit 1)  ✓ 编排接缝 = `facade.validate_project()`（7 步）+ `--imports-only` 分支；违规形状 `ContractViolation(code, detail)` → `ERROR [code] detail` + exit 1。
- [x] 1.2 Enumerate the module-level import forms the governance tree actually uses (relative sibling imports, same-directory absolute imports, package `__init__` imports) so the resolver covers the real shapes  ✓ 实测本仓用到的三种形态：相对兄弟导入（`from .fixtures import x`）、同目录**绝对**导入（`from gitio import run_git`、`from doc_hygiene_check import X`）、包 `__init__` 导入。三种都已被解析覆盖（探针逐条报红/绿）。
- [x] 1.3 Confirm the real tree currently has no cycles (the two this session removed are the only ones known)  ✓ 真实树实测无环（本会话两把已清零）；checker exit 0。

## 2. The rule

- [x] 2.1 Add `project_architecture_check/cycles.py`: enumerate modules, resolve module-level imports to files, build the graph, and report every strongly connected component larger than one  ✓ `cycles.py`（143 行）：枚举模块 → 解析模块级导入到文件 → 建图 → Tarjan 强连通分量 → 每个 size>1 的分量报一条。
- [x] 2.2 Count only imports whose parent is the module body: anything inside a function, a class, or an `if` (including `TYPE_CHECKING`) is deferred and is not an edge — that is the repo's established cycle-breaking technique  ✓ 只算**直接位于 `Module.body`** 的导入；函数/类/`if`（含 `TYPE_CHECKING`）内的导入一律不算边——实测三种合法形态均绿。
- [x] 2.3 Report one `ContractViolation("import.cycle", ...)` per component with a stable, ordered cycle path  ✓ `ContractViolation("import.cycle", …)`，环路径按字典序稳定输出（`a.py -> b.py -> a.py`）。
- [x] 2.4 Wire it into `validate_project()` and into the `--imports-only` branch  ✓ 已接入 `validate_project()` 与 `--imports-only`；**端到端证明**：真实树里临时种一对环文件 → `ERROR [import.cycle]` exit 1 → 清理后 exit 0。

## 3. Prove it both ways

- [x] 3.1 Real tree: the checker exits 0 (no cycle reported)  ✓ 真实树 checker exit 0；套件里另有一条 `RealTreeTest` 直接断言仓库无环。
- [x] 3.2 Two-module cycle in a temporary tree: reported  ✓ 两模块互导（相对导入）→ 红。
- [x] 3.3 Three-module cycle (A -> B -> C -> A, where no pair is mutual): reported — this is what a pairwise check would miss  ✓ **三模块环 A→B→C→A（无任何一对互导）→ 红**——这正是两两互导检查会漏掉的形态，也是选 SCC 的理由。
- [x] 3.4 Legal shapes are NOT reported: a deferred import inside a function, a `TYPE_CHECKING` block, a facade re-export, and a one-way package dependency  ✓ 函数内延迟导入 · `TYPE_CHECKING` 块 · facade 单向再导出 · 包 `__init__` 单向依赖——全部绿（另有包级环的**正向**用例：`pkg/__init__` ↔ `pkg/leaf` 被报出）。
- [x] 3.5 Every one of these runs as a direct test in the governance suite (no subprocess substitutes)  ✓ 9 条用例全部直接调用规则（无 subprocess 替代），落在 `openspec/tests/governance/test_import_cycles.py`；治理套件 221 → **230**。

## 4. Ratchet, registration, closeout

- [x] 4.1 Add the new module to the budget table at its measured value; verify the budget checker and its three tests pass  ✓ `cycles.py` 入表 143/0；闸与三条预算测试全过（`facade.py` 未在表内，其 +3 行不触闸）。
- [x] 4.2 Register it in `required-paths.toml`; verify the architecture checker exits 0 with a mutation check (move it away, confirm `path.missing`, restore)  ✓ 已登记；移走该文件 → 立即失败 exit 1（形态是 `ModuleNotFoundError` 而非 `path.missing`，因为 facade 直接导入它——见偏差 2）→ 恢复 exit 0。
- [x] 4.3 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0  ✓ 治理套件 230 · 七 checker + closeout gate 全 0 · `make verify` 252。
- [x] 4.4 Confirm no existing rule changed: the checkers' outputs are identical apart from the new rule's absence on a clean tree  ✓ 既有规则语义未改：本把只在 `facade` 的编排里**追加一步**，未触碰 `imports.py` 与其余 6 步；clean tree 输出逐字不变（`Architecture governance passed for …`）。
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipts  ✓ 见下 `## Delivery Record`。

## Deviation Register

- 偏差 1（测试辅助函数漏建父目录）：`test_import_cycles.py` 的建树辅助起初直接 `write_text`，遇到 `pkg/__init__.py` 这种嵌套路径即 `FileNotFoundError`（9 条里 1 条 ERROR）。修法是先 `mkdir(parents=True, exist_ok=True)`。**教训：夹具辅助要按"任意嵌套路径"写，不能假定同层文件名。**
- 偏差 2（登记变更的失败形态与预期不同，如实记录）：移走 `cycles.py` 时实测到的是 `ModuleNotFoundError`（因为 `facade.py` 直接导入它），**不是** `path.missing`。两者都是"移走就红"，但后者才是**登记**这条守卫本身在起作用。也就是说：本把对"登记生效"的证明是间接的（文件被引用的强度更高，掩盖了登记检查）。登记检查本身在前两把（`doc_hygiene_check/rules.py`、`doc_hygiene_battery/registry.py`）已被直接证明过；本把未重复该形态。
- none: 除上述两项外无其他设计偏离。
## Delivery Record

- **外部行为**: **只增不改**——`facade.validate_project()` 的 7 步之后追加 1 步，`--imports-only` 分支同样追加；`imports.py` 与其余 6 步未触碰，clean tree 的 stdout 逐字不变（`Architecture governance passed for <root>`）与退出码 0 不变。新增的失败面只有一条：`ERROR [import.cycle] module-level import cycle in openspec/governance: …` + exit 1。真实树绿（本会话两把已把环清零）。
- **影响面**: 新增 `openspec/governance/project_architecture_check/cycles.py`（143 行）与 `openspec/tests/governance/test_import_cycles.py`（9 条）· `facade.py` +3 行（导入 + 两处调用；该文件未在体积表内）· `check_code_budgets.py`（新模块入表 143/0）· `required-paths.toml`（登记）。
- **实际跑了什么**: 治理套件 exit 0（221 → **230**）· 七个 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· **接线端到端红证**：真实树里临时种 `_cycle_probe_a.py` ↔ `_cycle_probe_b.py` → `ERROR [import.cycle] … _cycle_probe_a.py -> _cycle_probe_b.py -> _cycle_probe_a.py` exit 1 → 清理后 exit 0 · **规则级红/绿探针 6 例**：两模块互导红、三模块环红、同目录绝对导入红、函数内延迟导入绿、`TYPE_CHECKING` 绿、facade 单向再导出绿 · **登记变更实测**：移走 `cycles.py` → 立即失败 exit 1 → 恢复 0 · 体积闸与三条预算测试全过。
- **未执行的检查**: **未扩到 harness 侧**——那里有分层矩阵但同样没有环检测；本把刻意不扩大范围（一次放行一把），已在模块 docstring 与提案里写明落点 · 未检测**跨目录**的环（分层方向由既有规则管）· 未做自动修复 · 真实模型梯未跑（纯静态分析）。
