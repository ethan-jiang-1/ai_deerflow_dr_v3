# BUG-006: change-guidance 门禁的章节解析无围栏感知（可误拒合法 change、可误判表单模式）

> 严重级别: P1 | 发现: 2026-10-17 | 状态: 已修

## 症状

`check_change_guidance.py`（closeout 门禁的组件之一）解析 proposal / design 的**章节与表格**时
逐行匹配、**无代码块感知**。三条探针实测（均可直接运行）：

| 探针 | 机制 | 后果 |
|---|---|---|
| **A** | 围栏内的 `## Example Heading` 让 `helpers._section_after_heading()` **提前截断章节** | 章节只剩 4 行、其后的 `- **Evidence seam:**` **不在章节内** ⇒ 合法 change 被报"缺字段"（**假拒绝**） |
| B | `reviews._validate_workflow_outcome_review()` 把**围栏内的表格示例**也收进 `table_lines`，它成为 `table_lines[0]`（**表头**） | 表头比对失败 ⇒ 假拒绝 |
| C | `proposals.py` 用 `re.findall(r"^## Program Focus\s*$", proposal, MULTILINE)` 计标题 | 围栏内出现该标题即 `program_count == 1` ⇒ **普通 change 被当作 program 模式**（假阳性） |

方向以**假拒绝**为主——即"一个完全合规、只是在示例里放了标题/表格的 change 会被门禁挡下"。
这与 BUG-003/004/005 同根：**同一件事（什么算结构）被逐行匹配反复重写，而没有复用唯一那份围栏规则**
（`markdown_fences.py`，已由三个工具采用）。

## 根因

| 位置 | 实现 | 与结构感知的差 |
|---|---|---|
| `helpers.py:46 _section_after_heading` | `re.search(rf"^#{{1,{n}}} (?!#)", proposal[start:], MULTILINE)` | 围栏内的 `##` 会被当成下一个章节标题，**章节被截断** |
| `reviews.py:58` | `[line for line in section.splitlines() if _table_cells(line) is not None]` | 围栏内的表格行被当成真表格行 |
| `proposals.py:448-449` | `re.findall(r"^## Program Focus\s*$" / r"^### Workstream Focus:", …)` | 围栏内的标题被计入 |
| `guidance.py:114` | `re.findall(r"^> authority:.*$", …, MULTILINE)` + 要求恰好 1 条 | 围栏内引用该行即计数失真（**未单独探针，见"未执行"**） |

## 复现

```python
import re, sys
sys.path.insert(0, "openspec/governance")
from change_guidance_check import helpers
proposal = ("## Change Focus\n\n- **Primary module:** x\n\n"
            "```\n## Example Heading Inside A Fence\n```\n\n- **Evidence seam:** y\n")
m = re.search(r"^## Change Focus\s*$", proposal, flags=re.MULTILINE)
section = helpers._section_after_heading(proposal, m, maximum_level=2)
print("Evidence seam" in section)   # False —— 但它在 proposal 里确实存在
```

## 修好判据

1. 三处（`_section_after_heading` 的标题搜索、`reviews` 的表格行收集、`proposals` 的标题计数）
   改为**跳过围栏代码块内的行**，复用唯一实现 `markdown_fences.fence_flags`。
2. 探针 A/B/C 的结论**全部翻转**：章节不再被截断（`Evidence seam` 在章节内）、围栏表格不计入、
   `program_count` 为 0。
3. 直接测试覆盖三例，且**变异检查能红**（例如把围栏规则换回逐行匹配）。
4. 不变量：七个 checker + closeout gate + 治理套件（236）全绿；既有判定语义**只增不改**
   （真实树上结果不变）。
5. `guidance.py:114` 的 `> authority:` 计数一并评估（同为逐行正则）。

证据 owner：治理侧（`check_change_guidance.py` 与治理套件）。

## 修复关联

**已修**，由 change `guidance-adopts-fence-rule` 落地：四处逐行解析改接唯一围栏规则
`markdown_fences.py`——`helpers` 新增 `_without_fences()`（遮蔽围栏行、**保持行数**，既有正则
一行不改地作用在遮蔽后的文本上），`_section_after_heading()` 改为**行遍历**（唯一按偏移切片的地方，
遮蔽会改变行长故不能照搬），`reviews` 的表格行收集、`proposals` 的标题计数、`guidance` 的
`> authority:` 计数三处改接遮蔽。

**判据证据**：
- 判据 2（三条探针**全部翻转**）→ 逐条实测：章节不再被截断（`Evidence seam` 在章节内）· 表格行
  仍为 3 条且首行是真表头 · `program_count` 为 0。
- **端到端**：在合规 proposal 里种入围栏标题——修复前 `[focus.field_missing]` exit 1，
  修复后 `Change Guidance governance passed.` exit 0。**假拒绝消失**。
- 判据 3（直接测试 + 变异能红）→ 新增 5 条直接测试；**变异检查**：把 `_without_fences()` 变成
  恒等函数 → 2 条失败 → 恢复后与备份**字节一致**。
- 判据 4（不回退）→ 治理套件 236 → **241** 全绿（含端到端植入负例）· 七 checker + closeout gate
  全 0 · 真实树既有判定逐字不变。

**两处附带修复**：`test_project_gate.py` 的手维护依赖闭包补入 `markdown_fences.py`（否则拷贝树
`ModuleNotFoundError`）；三处体积上限按实测更正（462/408/248）。

**一处诚实标注**：`guidance.py` 的 `> authority:` 计数**未单独做端到端探针**，判据是机制同构
（同一函数、同一形状、同一后果，与探针 C 一致）。
