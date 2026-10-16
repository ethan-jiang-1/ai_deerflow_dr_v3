# BUG-005: doc-hygiene 的逐行解析有三种围栏概念，可误报、且可**静默失明**

> 严重级别: P1 | 发现: 2026-10-16 | 状态: 已修

## 症状

`check_doc_hygiene.py` 是守护账本索引与计数的门禁。它对 Markdown 的逐行解析里存在**三种不同的
围栏概念**，其中两种与 CommonMark 不符，后果分三个方向（全部已用探针实测）：

| # | 方向 | 探针 | 实测结果 |
|---|---|---|---|
| 1 | **漏报（最严重）** | 在一处**真缺陷**前放一行 **4 空格缩进的 ```**（CommonMark §4.4 视为**缩进代码块**，非围栏） | 真缺陷**不再被报出**——`_ledger_roster_problems` 认为围栏已开启，**跳过文件余下部分** |
| 2 | 误报 | 在账本索引 README 放一个 **`~~~` 围栏**、内含孤立表格行 | 报 `ledger row placement defect`（朴素检测只认 ```） |
| 3 | 误报（另一机制） | 同一 `~~~` 围栏内含一行 `CLS-777` 的示例索引行 | 报 `next-ID declaration disagrees … allocation implies CLS-778`——`_allocated_numbers` **完全没有围栏感知**，把示例编号算作"已分配"，于是要求把真声明改成没人分配过的号 |
| 4 | 误报 | 在受管文件放 `~~~` 围栏、内含真实陈旧标记 `(skeleton)` | 报 `stale narrative marker '(skeleton)' at AGENTS.md:6`——`stale_markers` 无围栏感知，而**在围栏里引用禁用标记是合法文档写法** |

方向 1 严格劣于 BUG-003/BUG-004：那两个是**判错**，这个让检查器**不判**——而且门禁返回 0，
使用者不会知道它已经停止检查。

## 根因

同一件事（什么算围栏代码块）在该文件里有**三种实现**：

| 位置 | 实现 | 与 CommonMark 的差 |
|---|---|---|
| `_ledger_roster_problems`（~627） | 自建 `in_fence` 开关，`raw.strip().startswith("```")` | **只认 ```**（不认 `~~~`）；缩进**无界**（4 格也当围栏 → 方向 1 的漏报）；不实现反引号 info-string 规则 |
| `_allocated_numbers`（~563） | **无** | 围栏行照读 → 方向 3 |
| `stale_markers`（~815） | **无** | 围栏行照读 → 方向 4 |

而仓库里**已经有**唯一实现 `openspec/governance/markdown_fences.py`（CommonMark §4.5 + §4.4，
上一把 change `share-fence-parsing` 刚建立并被两个工具采用）。本缺陷是那次收敛**没有覆盖到这里**。

## 复现

全部可执行（`openspec/governance/_battery.py` 暴露 `build_clean_fixture` / `_ledger_repo` /
`run_rule` 供探针使用）：

```python
import sys, tempfile; from pathlib import Path
sys.path.insert(0, "openspec/governance")
import _battery as B
ORPHAN = "| CLS-777 | 2026-10-01 | [x](x) | orphan row |"
TARGET = "_backlog/_archived/_settled_issues/README.md"

def probe(prefix: str):
    td = tempfile.TemporaryDirectory(); root = Path(td.name); B._ledger_repo(root)
    p = root / TARGET
    p.write_text(p.read_text(encoding="utf-8") + "\n" + prefix + ORPHAN + "\n", encoding="utf-8")
    hits = [x for x in (B.run_rule("ledger_consistency", root) or []) if "row placement" in x]
    td.cleanup(); return hits

print("真缺陷直接放：", probe(""))              # 报出
print("前面加 4 格缩进 ```：", probe("    ```\n\n"))  # **不报** —— 漏报
```

## 修好判据

让 doc-hygiene **采用那唯一一份围栏规则**（不写第四份）：

1. `stale_markers` 与 `_allocated_numbers` 跳过围栏行（用 `markdown_fences.fence_flags` 并保留
   行号——行号要出现在报错里）。
2. `_ledger_roster_problems` 删除自建 `in_fence`，改用同一份 `fence_flags`。
3. 四条探针的结论**全部翻转**：方向 1 的真缺陷**恢复被报出**；方向 2/3/4 的围栏示例**不再触发**。
4. 直接测试覆盖这四条，且**变异检查能红**（例如把 `fence_flags` 换回"只认 ```+无界缩进"）。
5. 所有门禁与治理套件（217，含 `_battery.py` 的 39 条控制）不回退。

证据 owner：治理侧（`check_doc_hygiene.py` 与治理套件）。

## 修复关联

**已修**，由 change `doc-hygiene-adopts-fence-rule` 落地：`check_doc_hygiene.py` 的三条扫描线
改用唯一那份围栏规则 `markdown_fences.py`——`_allocated_numbers` 与 `stale_markers` 跳过围栏行
（**保留行号**，行号要出现在报错里），`_ledger_roster_problems` 删除自建 `in_fence`（第三份围栏
概念就此消失）。仓库里不再有第二份围栏判定。

**判据证据**：
- 判据 3（四条探针结论**全部翻转**）→ 逐条实测：方向 1 真缺陷**恢复被报出**；方向 2/3/4 的围栏
  示例**不再触发**
- 判据 4（直接测试 + 变异能红）→ 四条控制进正典电池（1 负例 + 3 绿色），清单 pin 30/9/39 →
  **31/12/43**；两次变异检查：把 roster 规则改回**朴素围栏开关** → `failing_controls()` 列出
  **两条**账本控制（`an indented fence opener hid a real ledger defect` 与
  `a tilde-fenced example read as a ledger row`）；去掉标记扫描的围栏跳过 → 列出
  `a fenced marker quote reported as stale`；两次均恢复且与备份**字节一致**
- 判据 5（不回退）→ 治理套件 217 → **221** 全绿（含电池 43 条控制）· 七个 checker + closeout
  gate 全 0 · `make verify` 252

**棘轮随之更正**：`check_doc_hygiene.py` 895 → 901、`_battery.py` 671 → 724（各附一行理由）。
