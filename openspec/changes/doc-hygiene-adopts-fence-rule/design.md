# Design

## Context

动机见 `proposal.md` — Why。塑造形态的实测事实：

| 事实 | 值 |
|---|---|
| 该文件的围栏概念 | **三种**：自建 `in_fence`（只认反引号、缩进无界）· `_allocated_numbers` 无 · `stale_markers` 无 |
| 唯一实现 | `markdown_fences.py`（上一把 change `share-fence-parsing` 建立，已被另两个工具采用） |
| 漏报探针 | 真缺陷**会**被报出；前面加一行 4 格缩进的开启符后 → **不再被报出** |
| 误报探针 | `~~~` 围栏示例 → row placement defect + `allocation implies CLS-778` |
| 电池 | 39 条控制（30 负例 + 9 绿色），清单 pin 被测试钉死 |

## Goals / Non-Goals

**Goals:** 三条扫描线改用唯一围栏规则 · 四条探针翻转 · 四条控制进电池且能红 · 全门禁不回退。

**Non-Goals:** 不写第四份围栏逻辑；不拆这两个超长文件；不动其他脚本（上两把已收敛）。

## Decisions

### D-1｜用 `fence_flags` + `zip(..., strict=True)`，而不是 `iter_outside_fences`

- **选**：三处都取 `lines` → `fence_flags(lines)` → `zip` 配对，`fenced` 为真则 `continue`。
- **为什么**：`stale_markers` 的报错里**必须带行号**；`iter_outside_fences` 会丢掉行号关联。
  `fence_flags` 一 flag 对一行，行号天然保持。
- **代价**：多一个临时列表（`lines`）。
- **换来**：行号不变、规则唯一、三处写法一致。

### D-2｜四条控制进正典电池，不清单外挂

- **选**：在 `_battery.py` 加 1 条负例 + 3 条绿色，并同步 pin（30/9/39 → 31/12/43）。
- **为什么**：doc-hygiene 的守卫就住在电池里；控制放在外面会与清单漂移，而清单正是"守卫数量
  本身被钉住"的机制。绿色控制用 `absent=(...)` 而非 `zero_violations`——因为账本夹具是**故意
  漂移**的（它自带 counter mismatch），要求全清会误伤。
- **代价**：清单 pin 与文档注释同步改动。
- **换来**：四条回归成为正典守卫的一部分，`failing_controls()` 可直接证明它们能红。

### D-3｜负例控制选"漏报"方向，而非误报

- **选**：唯一的负例是"4 格缩进开启符**不得**让检查器闭嘴"（`present=("ledger row placement
  defect",)`）。
- **为什么**：漏报是本缺陷里最严重的方向——检查器静默停止工作却返回 0。把它做成**必须命中**的
  负例，意味着任何让检查器再次失明的改动都会立刻红。
- **代价**：无。
- **换来**：P1 方向有了硬守卫。

### D-4｜上限按实测更正（第三次同一处理）

- **选**：`check_doc_hygiene.py` 895 → 901、`_battery.py` 671 → 724，各附一行理由。
- **为什么**：闸自己给的出路是"shrink it, or justify raising the ceiling with a one-line note"。
  这次加的行是**守卫本身**（4 条控制 + 夹具），缩回等于删守卫。
- **代价**：两个文件的棘轮各抬一次。
- **换来**：修复与守卫同时落地，且理由留痕。

## Risks / Trade-offs

- [改解析面可能改变其他规则的判定] → 三处都是"跳过围栏行"，只会**减少**对围栏内容的判定；
  全量治理套件（含 43 条控制）与七个 checker 全绿可证。
- [绿色控制用 `absent` 会漏掉其他问题] → 这正是意图（账本夹具故意漂移）；`absent` 只针对本控
  制关心的报错串，其他噪声不影响。
- [上限连抬两次] → 已在表内写明理由；长函数上限未动（新函数均 < 50 行）。
- [与上一把的 `markdown_fences` 语义不一致] → 不可能：本 change 直接调用它，没有第二份判定。

## Migration Plan

1. `check_doc_hygiene.py` 导入共享规则，三处改接。
2. 四条控制进电池 + pin 同步。
3. 四条探针复核（全部翻转）。
4. 两次变异检查（`failing_controls()` 必须列出对应控制）。
5. 上限更正；BUG-005 毕业翻转；门禁；归档。

**回滚**：撤销 diff；BUG-005 卡片 `mv` 回 `bugs/` 并翻回 `修就绪`。
