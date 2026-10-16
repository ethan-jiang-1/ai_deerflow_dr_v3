# Proposal: doc-hygiene-adopts-fence-rule

## Why

修复 **BUG-005**（P1）。`check_doc_hygiene.py` 守护账本索引与计数，但它的逐行 Markdown 解析里
有**三种不同的围栏概念**（自建开关只认反引号且缩进无界、两处**完全没有**围栏感知）——而仓库里
上一把刚建立了唯一实现 `markdown_fences.py`。四条探针实测的后果：

| 方向 | 探针 | 结果 |
|---|---|---|
| **漏报（P1）** | 真缺陷前放一行 **4 空格缩进的 ```**（CommonMark §4.4 是缩进代码块，非围栏） | 真缺陷**不再被报出**——检查器认为围栏开启，跳过文件余下部分 |
| 误报 | 账本索引里 **`~~~` 围栏**内的孤立行 | 报 row placement defect |
| 误报 | 同一围栏内示例的 `CLS-777` | `_allocated_numbers` 把示例编号算作**已分配**，要求把真声明改成没人分配过的号 |
| 误报 | 受管文件里围栏内引用真实陈旧标记 | 报 stale marker——而在围栏里引用禁用标记是**合法文档写法** |

**漏报方向严格劣于 BUG-003/BUG-004**：那两个是判错，这个让检查器**不判**且返回 0，使用者不会
知道它已停止检查。

## What Changes

- **三处改接共享规则**（不写第四份）：`stale_markers` 与 `_allocated_numbers` 跳过围栏行
  （用 `fence_flags` 并**保留行号**——行号要出现在报错里）；`_ledger_roster_problems` 删除自建
  `in_fence`，改用同一份 `fence_flags`。
- **四条控制进正典电池**（`_battery.py`）：1 条负例（4 格缩进开启符**不得**让检查器闭嘴）
  + 3 条绿色（`~~~` 围栏示例不算账本行 · 围栏内示例编号不分配 · 围栏内引用标记不算陈旧）。
  清单 pin 同步：30/9/39 → **31/12/43**。
- **体积上限随实测更正**：`check_doc_hygiene.py` 895 → **901**、`_battery.py` 671 → **724**
  （各附一行理由）。

**不变量**：命令行契约与 `SCHEMA_VERSION` 不变 · 治理套件与全部门禁不回退 · 探针四条结论**全部
翻转** · harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 修的是门禁内部解析，不改任何 requirement 或契约面。 -->

### Modified Capabilities

<!-- none: 同上。围栏规则本身仍未被 spec 声明（工具内部解析不属能力面）；本 change 只是让第三个
     工具也采用那唯一实现。 -->

## Impact

- **改**：`check_doc_hygiene.py`（三处 + 共享导入，+6 行）· `_battery.py`（+4 控制与夹具）·
  `check_code_budgets.py`（两处上限）· `test_doc_hygiene.py`（清单 pin）·
  BUG-005 卡片毕业（`mv` + 索引 + 计数）。
- **不动**：doc-hygiene 的规则集与命令行 · `SCHEMA_VERSION` · `deerflow/` ·
  `deep_research_harness/`。
- **触发车道**：治理套件（含 43 条电池控制）· 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` —— 它拥有
  "账本索引/计数/标记是否合规"这些判定；本 change 修正它的**输入解析**。
- **Seam classification:** deterministic-guardrail —— 门禁的解析面；无模型参与。
- **Question:** 一个会因一行普通 Markdown 而**静默停止检查**的门禁，能否改为采用唯一那份围栏
  规则——而四条探针结论翻转、新增四条控制能红、既有 39 条控制与全部门禁不回退？
- **Necessary adjacent/external contracts:** `markdown_fences.py`（answers: 唯一实现，上一把建立）·
  `_battery.py` 的 `NegativeCase`/`case_holds` 语义（answers: `present` 必须命中、`absent` 不得命中、
  `zero_violations` 全清）· 清单 pin（answers: 控制数被测试钉死，必须同步）·
  `check_code_budgets.py`（answers: 加行后怎么办——更正上限并附理由）。
- **Evidence seam:** 四条探针的前后对照 · `failing_controls()` 的变异检查 · 治理套件（217 → 221）·
  七个 checker + closeout gate · 体积闸与三条预算测试。
- **Not in scope:** 拆 `check_doc_hygiene.py`（901 行）与 `_battery.py`（724 行）·
  其他治理脚本的同类盲区（`check_project_specs` 与 closeout 工具上一把已收敛）· CAS 空转。
- **Triggered review policies:** local-context, change-admission
