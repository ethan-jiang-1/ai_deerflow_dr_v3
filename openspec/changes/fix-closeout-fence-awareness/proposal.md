# Proposal: fix-closeout-fence-awareness

## Why

修复 **BUG-003**（`_backlog/_archived/_fixed_bugs/BUG-003-…`）。`_unchecked_task_labels()`
逐行匹配 checkbox，**没有代码块感知**，于是围栏代码块里的示例被当成真任务；经
`_validate_review()` 放大后，review 可以引用一个只作为示例存在于围栏里的标签，工具会把它
当作真正的未勾任务接受——**回执"证明"了一件并非任务的事**。

上一把 `cover-closeout-decisions` 发现它时无权改工具，按仓规第 4 条**就地锁定**（两条为反转
而写的测试）并交还裁决。卡片给过两条路：修解析，或文档禁止。

**选修解析**，理由是仓规自己给的：CLS-025 卡明确否决过"先不设守卫、靠人工棘轮"（理由
"1473 行就是这么长出来的"），而"tasks.md 不许出现围栏 checkbox 示例"正是一条没有机器守卫的
约定；且那两条锁定测试本就是为反转而写，失败优先点已就位。

## What Changes

- **`_iter_outside_code_fences()`**：按 [CommonMark 0.31.2 §4.5](https://spec.commonmark.org/0.31.2/#fenced-code-blocks)
  实现围栏感知——开启需 3 个以上反引号或波浪号、缩进不超过 3 格、可带 info string（**反引号
  围栏的 info string 不得含反引号**）；闭合需**同字符且不短于**开启、其后只允许空白；
  **未闭合则余下全部视为代码**（故是单趟行走，不是找配对行）。
- **`_unchecked_task_labels()`** 改为在其输出上匹配。
- **反转** `FencedCodeBlockTest`（原锁定测试）为 11 条覆盖：闭合 / 未闭合 / 波浪号 /
  闭合更短不闭合 / 闭合带尾随文字不闭合 / info string / 闭合后可继续扫描 /
  **`_validate_review` 现对围栏标签返回 `unknown-unchecked-task`**。
- **体积上限 256 → 295**（实测值），表内一行写明理由——闸自己给的合法出路是
  "shrink it, or justify raising the ceiling with a one-line note"。

**一处刻意的范围决定**：四空格缩进是**缩进代码块**（CommonMark 4.4），但**不跳过**——
`tasks.md` 的任务项合法地可以缩进四格（嵌套）。只跳过围栏，并由一条测试锁定该边界。

**不变量**：命令行契约与 `SCHEMA_VERSION` 不变 · 证据数据模式不变 · harness 面零改动 ·
`check_code_budgets.py` 的长函数上限不变（新函数 < 50 行）。

## Capabilities

### New Capabilities

<!-- none: 修的是一个工具内部的解析盲区，不改任何 requirement 或契约面。 -->

### Modified Capabilities

<!-- none: 同上。 -->

## Impact

- **改**：`openspec/governance/selected_change_closeout.py`（+围栏感知）·
  `openspec/governance/check_code_budgets.py`（上限 256 → 295 + 理由）·
  `openspec/tests/governance/test_closeout_decisions.py`（锁定测试反转为 11 条覆盖）·
  卡片翻 `已修` 并 `git mv` 入 `_archived/_fixed_bugs/` + 两处索引与计数声明同步。
- **不动**：命令行契约 · `SCHEMA_VERSION` · `deerflow/` · `deep_research_harness/` 全部。
- **触发车道**：治理套件 · 七个门禁组件（含体积闸，它是本 change 的主要关卡）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/selected_change_closeout.py` —— 它拥有
  "哪些行算任务"这一判定；本 change 修正它的解析面。
- **Seam classification:** deterministic-guardrail —— 一个校验器的输入解析；无模型参与。
- **Question:** 一个把"示例"当"任务"的解析器，能否在不改命令行契约、不改证据模式的前提下
  获得围栏感知——而反转后的测试能证明修复前会红、修复后为绿？
- **Necessary adjacent/external contracts:** [CommonMark §4.5](https://spec.commonmark.org/0.31.2/#fenced-code-blocks)
  （answers: 围栏的权威规则）· `check_code_budgets.py`（answers: 加了行怎么办——它的错误信息
  自己写明两条出路）· `test_closeout_decisions.py` 的两条锁定测试（answers: 反转点在哪）。
- **Evidence seam:** 治理套件（190 → 198）· 围栏变异检查（对围栏失明 → 9 条失败）·
  体积闸退出码 · `--help` 与子命令退出码 · `git diff --stat -- deep_research_harness/` 为空。
- **Not in scope:** 拆这个 295 行的文件（已登记为 follow-up）· 缩进代码块的跳过（刻意不做，
  见上）· CAS 空转 · 其他解析器。
- **Triggered review policies:** local-context, change-admission
