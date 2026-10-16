# Proposal: share-fence-parsing

## Why

上一把修 BUG-003 时，我给 closeout 工具写了围栏解析——**但仓库里早就有一份**：
`check_project_specs.py:177` 的 `strip_fenced_code_blocks()`，被一个**门禁组件**使用。
于是同一件事有两份实现，而且**语义不同**：

| | 既有实现（specs checker） | BUG-003 的修复（closeout 工具） |
|---|---|---|
| 缩进 | `^\s*(`{3,}…)` —— **无界** | 按 §4.5 **≤3 格**（4 格是缩进代码块） |
| 反引号 info-string | 不检查 | 按 §4.5 **不得含反引号** |
| 直接测试覆盖 | **0**（`openspec/tests/` 引用 0 次） | 11 条（上一把刚建） |

复核后**差额可达且方向危险**（详见 BUG-004）：

```
3 空格缩进围栏（真围栏）              两份一致
4 空格缩进（CommonMark 缩进代码块）   旧实现**藏掉**其后的真标题
反引号 info-string 含反引号（非围栏）  旧实现**藏掉**其后的真标题
```

specs checker 用剥离结果找 `## Requirement` 标题；旧实现**多剥**，于是**看不到真实声明的
requirement**（假阴性），而它是个**门禁组件**。即 BUG-003 的镜像：那个把示例当任务，这个把
真标题当示例。

## What Changes

- **新增 `openspec/governance/markdown_fences.py`**：唯一的围栏规则（CommonMark §4.5，含 §4.4
  的缩进边界），三种形态供不同调用方使用——`fence_flags()`（每行是否属围栏）、
  `iter_outside_fences()`（只产出围栏外的行）、`strip_fenced_code_blocks()`（把围栏内容换成空行、
  **保持行号**，这是 specs checker 的既有契约）。
- **`check_project_specs.py`**：删除本地 21 行实现，改用共享模块。
- **`selected_change_closeout.py`**：删除 BUG-003 的并行实现 38 行，改用共享模块。
- **新增 `openspec/tests/governance/test_markdown_fences.py`**（19 条）：CommonMark 全部边界 +
  **BUG-004 的两条回归**（真标题不得被藏）+ `strip` 的行号保持 + 换行归一。
- **收紧体积棘轮**：`check_project_specs` 464 → **445**、`selected_change_closeout` 295 → **257**
  （两份都因删掉本地副本而变小），并为新模块加一行 **83**。**上限跟着实测值下调**，不是只加不减。
- **BUG-004 毕业翻转**与本实现同一把落地。

**不变量**：命令行契约与 `SCHEMA_VERSION` 不变 · 所有门禁与治理套件不回退 ·
`check_project_specs` 的既有断言全绿 · harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 收敛的是实现位置与一处规则正确性，不改任何 requirement 或契约面。 -->

### Modified Capabilities

<!-- none: 同上。围栏规则此前没有任何 spec 声明它——这正是两份实现能漂移的原因；本 change 把
     规则收敛到一处并写进模块文档，但**不新增 requirement**（工具内部解析不属于能力面）。 -->

## Impact

- **新增**：`openspec/governance/markdown_fences.py` · `openspec/tests/governance/test_markdown_fences.py`。
- **改**：`check_project_specs.py`（-21 行）· `selected_change_closeout.py`（-38 行）·
  `check_code_budgets.py`（两处下调 + 一行新增）· `required-paths.toml`（登记新模块）·
  BUG-004 卡片毕业（`git mv` + 索引 + 计数）。
- **不动**：两个工具的命令行契约 · `SCHEMA_VERSION` · `deerflow/` · `deep_research_harness/`。
- **触发车道**：治理套件 · 七个门禁组件（`check_project_specs` 是本 change 的语义改动受益者）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/markdown_fences.py` —— 它现在拥有
  "什么算围栏代码块"这一判定；此前该判定分散在两处且互相矛盾。
- **Seam classification:** deterministic-guardrail —— 一个门禁组件的输入解析；无模型参与。
- **Question:** 同一件事的两份实现（语义还有分歧）能否收敛为一份有规范依据、有直接测试的实现
  ——而门禁组件因此**不再漏看**真实标题、两处棘轮同时下调、既有断言全绿？
- **Necessary adjacent/external contracts:** [CommonMark §4.5](https://spec.commonmark.org/0.31.2/#fenced-code-blocks)
  与 [§4.4](https://spec.commonmark.org/0.31.2/#indented-code-blocks)（answers: 权威规则）·
  `strip_fenced_code_blocks` 的**行号保持契约**（answers: specs checker 按行号报违规，不能删行）·
  `check_code_budgets.py`（answers: 文件变小后棘轮要不要跟着降——要，否则它能悄悄长回来）·
  治理目录按名导入的约定（answers: 脚本运行时目录自动在 `sys.path`；测试显式插入）。
- **Evidence seam:** 治理套件（198 → 217）· 三次变异检查（无界缩进 2 条 / 去掉 info-string 规则
  2 条 / 闭合长度 1 条）· 体积闸与三条预算测试 · BUG-004 的两条回归测试 · doc-hygiene 的计数与索引。
- **Not in scope:** 其他治理脚本的 Markdown 解析盲区（`check_doc_hygiene` 也在逐行解析，但那是
  另一类输入）· 拆 `selected_change_closeout.py`（仍挂着，现 257 行）· 缩进代码块的跳过语义 ·
  CAS 空转。
- **Triggered review policies:** local-context, change-admission
