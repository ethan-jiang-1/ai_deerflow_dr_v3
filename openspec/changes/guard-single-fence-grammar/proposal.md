# Proposal: guard-single-fence-grammar

## Why

围栏语法在这条线上被**手写了五次**：BUG-003（closeout 工具的解析）· BUG-004（specs checker 的
`strip_fenced_code_blocks`）· BUG-005（doc-hygiene 的三种围栏概念）· BUG-006（change-guidance 的
四处逐行解析）· 以及 BUG-003 修复当时又新写的一份。**每一次都是同一件事的第二次实现**，每一次都
带来一类误判（把示例当任务 / 把真标题当示例 / 静默失明 / 误拒合规 change）。

前几把把四家收敛到唯一实现 `markdown_fences.py`，并为此写了直接测试。**但"只有一处实现"这件事
本身没有守卫**——第六次仍可以照写不误，而且写法与已修的那些一样自然。

## What Changes

- **新增 `project_architecture_check/markdown_grammar.py`**：一条规则——治理侧除规范实现
  （`markdown_fences.py`）外，**不得在检测位置使用含 3 个以上连续反引号或波浪号的字符串字面量**。

  "检测位置"是本规则的关键，也是**取证得到的**：
  - 朴素版"代码里出现反引号字面量即违规"会在真实树上报 **7 处假阳性**——它们全在
    `doc_hygiene_battery/fixtures.py`，是**构造夹具树用的被测内容**（文档片段），不是检测逻辑。
    会叫狼的守卫最后会被关掉。
  - 收窄到**检测位置**（正则/搜索/切分类调用的实参、`in` / `not in` 的左操作数）后，真实树
    **0 处**命中，而手写围栏谓词的三种真实形态全部落网：
    `re.compile(...)` 的 pattern、`line.startswith("```")`、`"```" in line`。

- **接进既有编排**：`facade.validate_project()` 追加一步（沿用 `ContractViolation` 形状）。
- **新增直接测试**：三种手写形态各自被报出；"把围栏当内容写进夹具"与"调用 `markdown_fences`"
  不被报；规范实现自身豁免；真实树绿。
- **体积表按实测重测 + `required-paths.toml` 登记**。

**不变量**：既有 checker 判定**只增不改**（新规则是新的一步）· 七个 checker + closeout gate +
治理套件（241）全绿 · `--self-test` 契约不变 · harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 加的是架构守卫的一步，不改任何 requirement 或产品契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **新增**：`project_architecture_check/markdown_grammar.py` · 其直接测试。
- **改**：`project_architecture_check/facade.py`（追加一步）· `check_code_budgets.py`（新模块入表）·
  `required-paths.toml`（登记）。
- **不动**：`markdown_fences.py`（规范实现，被显式豁免）· `imports.py` / `cycles.py` 与其余既有规则 ·
  任何一个被检查的文件。
- **触发车道**：治理套件 · 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/project_architecture_check/markdown_grammar.py`
  —— 它拥有"围栏语法是否只有一处实现"这一判定；此前该判定**不存在**。
- **Seam classification:** deterministic-guardrail —— 纯静态分析。
- **Question:** 一条"围栏语法只许一处实现"的守卫，能否在真实树上**零误报**（不把夹具内容当违规）、
  而把三种手写的检测形态**全部**报出——且不改变任何既有判定？
- **Necessary adjacent/external contracts:** `markdown_fences.py`（answers: 规范实现，规则豁免它）·
  `doc_hygiene_battery/fixtures.py`（answers: 合法的"内容"用法，规则必须不碰）·
  `project_architecture_check/facade.py`（answers: 编排与违规形状）·
  `check_code_budgets.py`（answers: 新模块入表）。
- **Evidence seam:** 先期扫描（朴素版 7 处假阳性、收窄后 0 处）· 三种手写形态的红例 ·
  内容用法与规范实现调用的绿例 · 真实树绿 · 七 checker + closeout · 治理套件 241。
- **Not in scope:** 改 `markdown_fences.py` · 改已修的四家 · 检测**非**检测位置的反引号用法
  （那正是 7 处假阳性的来源）· 跨语言（只做 Python AST）· CAS 空转。
- **Triggered review policies:** local-context, change-admission
