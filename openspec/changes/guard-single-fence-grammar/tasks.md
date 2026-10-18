# Tasks

## 1. Evidence first

- [x] 1.1 Scan the governance tree for code-level (non-docstring) string literals containing a run of three or more backticks or tildes; record where they are and what they are for  ✓ 代码级（非 docstring）含 3+ 反引号/波浪号的字面量：**7 处**，全部在 `doc_hygiene_battery/fixtures.py`，且都是**夹具内容**（构造临时树用的文档片段）。
- [x] 1.2 Confirm the naive rule would be a wolf-crier: count how many of those literals a "any fence literal in code" rule would flag (expected: 7, all fixture content)  ✓ 朴素判据「凡代码里有围栏字面量即违规」会在真实树报 **7 处假阳性**——会叫狼的守卫最后会被关掉，所以判据必须区分「内容」与「谓词」。
- [x] 1.3 Narrow the criterion to detection positions (regex/search/split call arguments, and the left operand of `in`) and confirm the real tree is then clean (expected: 0)  ✓ 收窄到**检测位置**（正则/搜索/切分类调用的实参、`in`/`not in` 的左操作数）后，真实树 **0 处**命中。

## 2. The rule

- [x] 2.1 Add `project_architecture_check/markdown_grammar.py`: parse each governance module, collect fence-bearing literals outside docstrings, and flag the ones used in a detection position  ✓ `markdown_grammar.py`（119 行）：解析 → 收集非 docstring 的围栏字面量 → 只报检测位置上的那些。
- [x] 2.2 Exempt the canonical implementation by name, as a named constant, and report `ContractViolation("markdown.grammar_duplicated", ...)` with the file, the line, and a pointer to the canonical module  ✓ 豁免写成具名常量 `EXEMPT_MODULES`；违规为 `ContractViolation("markdown.grammar_duplicated", …)`，详情带文件:行号与指向规范实现的指引。
- [x] 2.3 Document the deliberate boundary in the module docstring: fence literals used as *content* (fixtures, messages) are out of scope — that is where the false positives came from  ✓ 模块 docstring 写明刻意边界：**内容**用法（夹具、消息、docstring）不在范围内——那正是 7 处假阳性的来源。
- [x] 2.4 Wire it into `validate_project()`  ✓ 接进 `validate_project()`。**刻意未接进 `--imports-only`**：该 flag 的语义是「只验证 manifest 与**导入**契约」，而本规则是**源码结构**规则（`cycles` 属导入属性故两侧都跑）——已写进代码注释。

## 3. Prove it both ways

- [x] 3.1 Red cases: `re.compile` with a fence pattern, `.startswith("```")`, and `"```" in line` are each reported  ✓ 三种手写形态全部报出：`re.compile` 的 pattern · `line.strip().startswith("```")` · `"```" in line`（另加波浪号一例）。
- [x] 3.2 Green cases: a fence literal used as fixture content, a call to the canonical module, and the canonical module itself are not reported  ✓ 三种合法形态不被报：夹具式内容字面量 · 调用 `markdown_fences` · docstring 里描述围栏。
- [x] 3.3 The real governance tree is clean, and the canonical module's own literals never trip the rule  ✓ 真实治理树绿；规范实现自身的字面量（它**必须**含有该模式）由豁免处理。
- [x] 3.4 Mutation check: disable the detection-position test (flag every fence literal) and verify the green cases fail; restore byte-identically  ✓ **变异检查**：取消检测位置判据（凡围栏字面量即报）→ 绿例立刻 **2 条 ERROR** → 恢复后与备份**字节一致**、9 条全过。

## 4. Ratchet, registration, closeout

- [x] 4.1 Add the new module to the budget table at its measured value; verify the budget checker and its three tests pass  ✓ `markdown_grammar.py` 119/0 入表；闸与三条预算测试全过。
- [x] 4.2 Register it in `required-paths.toml`; verify the architecture checker exits 0  ✓ 已登记；架构 checker exit 0。
- [x] 4.3 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0  ✓ 治理套件 241 → **250** 全绿 · 七 checker + closeout gate 全 0 · `make verify` 252。
- [x] 4.4 Confirm no existing judgement changed and the application side is untouched  ✓ 既有判定只增不改（`imports.py`/`cycles.py` 与其余 7 步未触碰）；harness 面零改动（diff 为空）。
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipts  ✓ 见下 `## Delivery Record`。

## Delivery Record

- **外部行为**: **只增不改**——`validate_project()` 的 7 步之后追加 1 步；`imports.py`、`cycles.py` 与其余步骤未触碰，clean tree 的 stdout 与退出码逐字不变。新增失败面只有一条：`ERROR [markdown.grammar_duplicated] <文件>:<行号> hand-rolls the fence grammar; use openspec/governance/markdown_fences.py` + exit 1。真实树绿。
- **影响面**: 新增 `project_architecture_check/markdown_grammar.py`（119 行）与 `openspec/tests/governance/test_markdown_grammar.py`（9 条）· `facade.py` +2 行 · `check_code_budgets.py`（新模块入表 119/0）· `required-paths.toml`（登记）。
- **实际跑了什么**: **先期扫描**（朴素判据 7 处假阳性 / 收窄后 0 处）· 治理套件 exit 0（241 → **250**）· 七 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· **红例 4 条 + 绿例 3 条**逐条实测 · **真实树绿** · **变异检查**：取消检测位置判据 → 2 条 ERROR → 恢复后字节一致 · 体积闸与三条预算测试全过 · harness 改动行数 0。
- **未执行的检查**: 只做 **Python**（AST）；非 Python 的围栏语法不在范围内 · **非**检测位置的反引号用法**刻意不管**（正是 7 处假阳性的来源，已写进 docstring）· 规则只作用于 `openspec/governance/`，未检查 `openspec/tests/**`（测试里合法地含有围栏字面量）· 真实模型梯未跑（纯静态分析）。

## Deviation Register

- 偏差 1（**规则第一次运行就抓到了它自己**）：`markdown_grammar.py` 里 `("```" in node.value or "~~~" in node.value)` 是它自己检测用的字面量，**恰好构成它要禁止的形态** ⇒ 真实树 exit 1 报自己。这是机制在正常工作（检测器必然包含它要检测的模式），解法是显式的**两文件豁免**（规范实现 + 规则自身）并在注释里写明这是诚实的解法，而不是把判据弄松到抓不到自家人。
- 偏差 2（接线断言失败，且差点蒙混过关）：`validate_no_import_cycles(root)` 在 `facade.py` 里出现**两次**，我按「仅一次」写断言 ⇒ 失败、接线未生效。**危险点在于真实树随后仍然 exit 0**（因为规则根本没跑），是**红/绿探针**把它揭出来的。教训：断言失败后要确认「改动到底有没有生效」，不能只看后续检查是否通过。
- 偏差 3（刻意不加进 `--imports-only`，就地写明）：该 flag 语义是「只验证 manifest 与导入契约」，而本规则是源码结构规则。这是语义判断而非遗漏，已写进代码注释与 design。
- none: 除上述三项外无其他设计偏离。
