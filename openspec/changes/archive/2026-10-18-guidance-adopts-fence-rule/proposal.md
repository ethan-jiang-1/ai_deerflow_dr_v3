# Proposal: guidance-adopts-fence-rule

## Why

修复 **BUG-006**（P1）。`check_change_guidance.py` 是 closeout 门禁的组件之一，它解析 proposal 的
**章节与表格**时逐行匹配、**无代码块感知**。三条探针实测（可直接运行）：

| 探针 | 机制 | 后果 |
|---|---|---|
| **A** | 围栏内的 `## Example Heading` 让 `_section_after_heading()` **提前截断章节** | 章节只剩 4 行，其后的 `- **Evidence seam:**` 不在章节内 ⇒ **合法 change 被报"缺字段"** |
| B | `_validate_workflow_outcome_review()` 把围栏内的表格示例收进 `table_lines`，它成为 `table_lines[0]`（表头） | 表头比对失败 ⇒ 假拒绝 |
| C | `proposals.py` 用 `re.findall(r"^## Program Focus\s*$", …)` 计标题 | 围栏内出现该标题即 `program_count == 1` ⇒ **普通 change 被当作 program 模式** |

方向以**假拒绝**为主："一个完全合规、只是在示例里放了标题或表格的 change 会被门禁挡下"。
这与 BUG-003/004/005 同根——**同一件事（什么算结构）被逐行匹配反复重写**，而没有复用唯一那份
围栏规则（`markdown_fences.py`，已由 closeout 工具、specs checker、doc-hygiene 三家采用）。

## What Changes

- **三处改接共享围栏规则**（不写第二份）：
  - `helpers._section_after_heading()`：找"下一个章节标题"时跳过围栏内的行——**这是探针 A 的根因，
    也是最重的一处**（它影响所有按章节切片的检查）。
  - `reviews` 的表格行收集：只收围栏外的行。
  - `proposals` 的两处标题计数：只在围栏外计数。
- **一并评估 `guidance.py` 的 `> authority:` 计数**（同为逐行正则、且要求恰好 1 条）：若可达即同修，
  否则记入未执行。
- **新增直接测试**：三例（章节不截断、围栏表格不计入、program 计数为 0）+ 合法形态不误报，
  并做**变异检查**（把围栏规则换回逐行匹配 ⇒ 测试必须红）。

**不变量**：既有判定语义**只增不改**——真实树上结果逐字不变（七个 checker + closeout gate 全绿）·
治理套件（236，含 43 条电池控制）只增不减 · `--self-test` 契约不变 · harness 面零改动 ·
**门禁对"真实、合规的 change"的判定不变**（这才是本把的要点：修的是假拒绝）。

## Capabilities

### New Capabilities

<!-- none: 修的是门禁的输入解析，不改任何 requirement 或契约面。 -->

### Modified Capabilities

<!-- none: 同上。围栏规则本身仍未被 spec 声明（工具内部解析不属能力面）；本把只是让第四个工具
     也采用那唯一实现。 -->

## Impact

- **改**：`change_guidance_check/helpers.py` · `reviews.py` · `proposals.py`（三处改接；可能含
  `guidance.py`）· 新增测试文件 · `check_code_budgets.py`（受影响文件的上限按实测重测）。
- **不动**：既有规则的判定语义与消息文本 · `SCHEMA_VERSION` 类常量 · 两个 checker 入口 ·
  `deerflow/` · `deep_research_harness/`。
- **触发车道**：治理套件 · 七个门禁组件（change-guidance 自身是主关卡）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/change_guidance_check/` —— 它拥有"一个
  change 的 proposal/design 是否合规"这一判定；本把修正它的**输入解析**。
- **Seam classification:** deterministic-guardrail —— 门禁的解析面；无模型参与。
- **Question:** 一个会因示例里的标题/表格而**误拒合规 change** 的门禁，能否改为采用唯一那份围栏
  规则——而三条探针翻转、真实树上既有判定不变、新增测试能红？
- **Necessary adjacent/external contracts:** `markdown_fences.py`（answers: 唯一实现）·
  `test_doc_hygiene.py` 式的清单 pin（answers: 本把不新增控制，故 pin 不动；新增的是直接测试）·
  `check_code_budgets.py`（answers: 改动文件的上限跟实测值）。
- **Evidence seam:** 三条探针的前后对照 · 端到端（在真实 change 的 proposal 里种一个围栏标题 →
  门禁是否误拒）· 治理套件 · 七 checker + closeout · 变异检查。
- **Not in scope:** 改写任何规则语义或消息文本 · 把围栏规则**声明进 spec**（仍是工具内部解析）·
  其他治理脚本 · CAS 空转。
- **Triggered review policies:** local-context, change-admission
