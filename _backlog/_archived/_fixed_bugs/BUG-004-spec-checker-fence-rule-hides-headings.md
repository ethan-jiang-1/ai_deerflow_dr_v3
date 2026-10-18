# BUG-004: specs 门禁的围栏剥离会藏掉真标题（围栏规则偏离 CommonMark）

> 严重级别: P2 | 发现: 2026-10-16 | 状态: 已修
> 修复: share-fence-parsing

## 症状

`check_project_specs.py` 用 `strip_fenced_code_blocks()` 把围栏内容清空，以免示例里的 `##`
被当成 requirement 标题。但它对**什么算围栏**的判定比 CommonMark 宽，于是出现**反方向**的错误：

> 一段 CommonMark 认定为**真标题**的 `## …`，被它当成围栏内容清空 → 门禁**看不到**那条真实
> 声明的 requirement（假阴性）。

即 BUG-003 的镜像：BUG-003 把"示例"当"任务"，本缺陷把"真标题"当"示例"。

## 根因

`check_project_specs.py:177` 的 `strip_fenced_code_blocks()` 与 CommonMark §4.5 有两处偏离，
两处都**偏向"更容易认为这是围栏"**：

| 偏离 | 既有实现 | CommonMark | 后果 |
|---|---|---|---|
| 缩进 | `^\s*(`{3,}…)` —— **无界** | §4.5 最多 3 格；**4 格是缩进代码块**（§4.4） | 4 格缩进的 ``` 被当成围栏开启，其后**未缩进的 `## 标题` 被一并清空** |
| 反引号 info-string | 不检查 | 反引号围栏的 info-string **不得含反引号**，否则该行不是围栏 | ```` ``` foo`bar ```` 被当成围栏，其后标题被清空 |

实测（2026-10-16，两实现同输入对比）：

```
3 空格缩进围栏（真围栏）            既有:隐藏=True  规范式:隐藏=True   一致
4 空格缩进（CommonMark 缩进代码块）  既有:隐藏=True  规范式:隐藏=False  **不一致**
反引号 info-string 含反引号（非围栏） 既有:隐藏=True  规范式:隐藏=False  **不一致**
```

## 复现

```python
import importlib.util
spec = importlib.util.spec_from_file_location("cps", "openspec/governance/check_project_specs.py")
cps = importlib.util.module_from_spec(spec); spec.loader.exec_module(cps)
text = "    ```\n## Requirement: 真实声明\n    ```\n"
print(cps.strip_fenced_code_blocks(text))   # 标题行被清空 —— 但 CommonMark 说它是真标题
```

同一文件里的 `strip_fenced_code_blocks` **零直接测试覆盖**（`openspec/tests/` 引用 0 次），
所以这条偏离此前无人看守。

## 修好判据

采纳 CommonMark §4.5/§4.4 的严格规则，并让**两处围栏解析共用同一实现**：

1. 共享实现按规范判围栏：≤3 格缩进、反引号围栏的 info-string 不得含反引号、闭合同字符且
   不短于开启、闭合后仅空白、未闭合则余下全为代码。
2. 上面两例的标题**不再被隐藏**（可执行判据：两例的 `##` 都出现在剥离结果里）。
3. 该实现有**直接单元测试**（含全部 CommonMark 边界）且**变异检查能红**。
4. 所有门禁与治理套件不回退；`check_project_specs` 的既有断言全绿。

证据 owner：治理侧（`check_project_specs.py` 与治理套件）。

## 修复关联

**已修**，由 change `share-fence-parsing` 落地：围栏规则收敛到唯一的
`openspec/governance/markdown_fences.py`（CommonMark 4.5 + 4.4 的缩进边界），
`check_project_specs.py` 与 `selected_change_closeout.py` 都改用它，两份本地副本删除
（−21 行 / −38 行）。

**判据证据**：
- 判据 1/2（两例真标题不再被藏）→ `test_markdown_fences.py` 的两条回归测试直接断言
- 判据 3（直接测试 + 变异能红）→ 19 条直接测试（此前该解析器覆盖率为 0）；三次变异检查：
  缩进改回**无界**（正是本缺陷的规则）→ 2 条失败；去掉反引号 info-string 规则 → 2 条失败；
  去掉"闭合不短于开启" → 1 条失败
- 判据 4（门禁不回退）→ 治理套件 198 → 217 全绿 · 七个 checker + closeout gate 全 0 ·
  `check_project_specs.py` 直接运行 exit 0

**棘轮也随之收紧**：`check_project_specs` 464 → 445（删掉本地副本的实测值），
`selected_change_closeout` 295 → 257，新模块入表 83。
