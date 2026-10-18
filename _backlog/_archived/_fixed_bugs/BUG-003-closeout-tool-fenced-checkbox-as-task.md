# BUG-003: closeout 工具把围栏代码块里的 checkbox 当成真任务

> 严重级别: P2 | 发现: 2026-10-16 | 状态: 已修
> 修复: fix-closeout-fence-awareness

## 症状

`openspec/governance/selected_change_closeout.py` 的 `_unchecked_task_labels()` 把
**围栏代码块里的 checkbox 行**也收集为"未勾任务"。该结果被 `_validate_review()` 用作
`task_references` 的**子集校验基准**，于是：

> 一份 review 可以引用一个**只作为示例存在于代码块里**的标签，而工具会把它当作
> 真正的未勾任务接受——回执因此"证明"了一件并非任务的事。

影响面：closeout 证据的健全性（不是崩溃、不是数据损坏）。触发需要两个条件同时成立：
被审 change 的 `tasks.md` 里存在围栏内的 checkbox 示例 **且** review 恰好引用该标签。

## 根因

`UNCHECKED_TASK_LINE = re.compile(r"^\s*(?:[-*+])\s+\[ \]\s+(.+?)\s*$")` 是**逐行**匹配，
解析器**没有代码块感知**——它不知道自己在不在围栏内。`_validate_review()` 只做
`set(references).issubset(_unchecked_task_labels(change_root))`，因此继承了这个盲区。

根因确认证据：新增的
`openspec/tests/governance/test_closeout_decisions.py::FencedCheckboxDefectTest`
（两条）——它们**锁定**当前行为而非修复，注释写明后果与修好后的反转方式；
`cover-closeout-decisions` 的 Delivery Record 也记了这条。

## 复现

```python
import sys; sys.path.insert(0, "openspec/governance")
import selected_change_closeout as tool, tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "tasks.md").write_text("```\n- [ ] fenced example\n```\n", encoding="utf-8")
    print(tool._unchecked_task_labels(root))   # {'fenced example'} —— 但它不是任务
```

经 `_validate_review` 放大（同一测试文件里有这条）：

```python
payload, problem = tool._validate_review(
    {"disposition": "review-required", "task_references": ["fenced example"]},
    root, root / "closeout-evidence" / "review.json")
# problem is None —— 围栏里的示例被当作合法任务引用接受
```

## 修好判据

二选一，由 owner 拍板：

1. **修解析**：`_unchecked_task_labels` 跳过围栏区间（`^```" 开合配对）。判据 = 反转
   `FencedCheckboxDefectTest` 的两条断言（改为"围栏示例**不**被收集"、`_validate_review`
   对围栏标签返回 `unknown-unchecked-task`），且治理套件全绿、命令行契约不变。
2. **文档禁止**：明确"`tasks.md` 内不得出现围栏 checkbox 示例"，写进
   `openspec/governance/selected-change-closeout.md`。判据 = 文档落地 + 一条守卫或人工检查
   说明为何不需要解析层修复（须写明理由，不能只是"约定"）。

证据 owner：治理侧（`check_project_gate.py --phase closeout` 与治理套件）。

## 修复关联

**已修**，走选项 1（修解析），由 change `fix-closeout-fence-awareness` 落地：
`_iter_outside_code_fences()` 提供 CommonMark 4.5 的围栏感知——开启围栏需 3 个以上
反引号或波浪号、缩进不超过 3 格、可带 info string（反引号围栏的 info string 不得含反引号）；
闭合需**同字符且不短于**开启、其后只允许空白；**未闭合则余下全部视为代码**。

发现于 `cover-closeout-decisions`（归档 `2026-10-16-cover-closeout-decisions`）——那一把的授权
是"补覆盖、不改工具"，故按仓规第 4 条就地锁定并交还裁决；本卡与实现同一把完成毕业翻转。

**判据证据**：`FencedCheckboxDefectTest` 的两条锁定测试已**反转为**
`FencedCodeBlockTest`（11 条，含未闭合 / 波浪号 / 闭合更短 / 闭合带尾随文字 / info string /
四空格缩进代码块不按围栏处理），并断言 `_validate_review` 对围栏标签返回
`unknown-unchecked-task` · **变异检查**：让解析器对围栏失明 → 9 条失败；恢复 → 全过 ·
治理套件 190 → 198 全绿 · 体积上限按实测值由 256 更正为 295（表内附理由）。

**一处刻意的范围决定**：四空格缩进是"缩进代码块"（CommonMark 4.4），但**不**跳过——`tasks.md`
里的任务项合法地可以缩进四格（嵌套）。只有围栏被跳过，并由一条测试锁定这个边界。
