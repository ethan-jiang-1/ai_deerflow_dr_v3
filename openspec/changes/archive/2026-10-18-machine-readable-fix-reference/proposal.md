# Proposal: machine-readable-fix-reference

## Why

上一把加了"毕业翻转与实现同一把落地"的守卫，当时**明确留了一条未做的**：卡片 `修复关联` 一节点名
的 change **是否存在，无人校验**。取证确认：全库 grep 那个概念**零命中**——也就是说，一张卡可以
点名一个**从不存在的 change** 并安安静静地归档。

为什么当时没做：那张卡里 change 名是**自由文本**（"由 change `X` 落地"、正文里还可能提到**别的**
change——发现它的那把、被它前置的那把）。要让守卫去猜自由文本里的名字，判据弱且易误报。

**取证**（六张归档卡）：它们点名的 change **全部真实存在**，但其中两张卡**同时提到多个** change：

| 卡 | 正文提到的 | **修复它的那一把** |
|---|---|---|
| BUG-001 | fix-headless-plan-gate | `fix-headless-plan-gate` |
| BUG-002 | harden-backlog-next-id-guard | `harden-backlog-next-id-guard` |
| BUG-003 | cover-closeout-decisions（发现它的）· fix-closeout-fence-awareness | `fix-closeout-fence-awareness` |
| BUG-004 | share-fence-parsing | `share-fence-parsing` |
| BUG-005 | share-fence-parsing（前置）· doc-hygiene-adopts-fence-rule | `doc-hygiene-adopts-fence-rule` |
| BUG-006 | guidance-adopts-fence-rule | `guidance-adopts-fence-rule` |

**这正说明自由文本不可靠**：同一张卡里"发现它的 change"与"修它的 change"并排出现。所以本把把
"修复关联"**加一个机器可读字段**，让守卫不必猜。

## What Changes

- **卡片格式增一行**：状态行之后 `> 修复: <change-name>`。
  - **必填**：状态为 `已落修` / `已修`（修复已落地的那两种状态）。
  - **若出现（任意状态）就必须有效**：点名的 change 必须存在于 `openspec/changes/<name>`（活跃）
    或 `openspec/changes/archive/<日期>-<name>`（归档）。
  - 其余状态**不强制**也不禁止——本把不做"修复尚未落地就禁止预填"的推断（那是另一条判据，
    且会与"已提案"的现实打架）。
- **守卫落在 doc-hygiene**（账本规则的 owner）：新增 `_card_fix_reference_problems()`，
  由 `_rule_ledger_consistency` 调用；违规沿用既有形状与退出码。
- **迁移 6 张归档卡**（补字段，值取上表"修复它的那一把"）。
- **电池控制同步**：1 条负例（点名不存在的 change 必须报出）+ 1 条绿色（有效引用不报），
  清单 pin 31/12/43 → **32/13/45**。
- 体积表按实测重测（`ledger.py`/`constants.py` 可能变大）。

**不变量**：既有规则判定**只增不改** · 七 checker + closeout gate + 治理套件（255）全绿 ·
`--self-test` 契约不变 · 真实树上（迁移后）绿 · harness 面零改动。

## Capabilities

### New Capabilities

<!-- none: 卡格式与账本守卫的演进，不改任何产品 requirement。 -->

### Modified Capabilities

<!-- none: 同上。账本卡格式由 `_backlog/README.md` 与 doc-hygiene 的规则共同定义，
     本把只增一个字段与它的校验。 -->

## Impact

- **改**：`_backlog/_archived/_fixed_bugs/BUG-001..006.md`（各加一行字段）·
  `doc_hygiene_check/ledger.py`（新助手 + 接线）· `doc_hygiene_check/constants.py`（字段正则与
  必填状态集）· `doc_hygiene_battery/`（2 条控制及其构造器）·
  `openspec/tests/governance/test_doc_hygiene.py`（清单 pin）· `check_code_budgets.py`（按实测）。
- **不动**：任何产品代码 · 任何既有规则语义 · `markdown_fences`/`cycles`/`graduation` 三条新守卫 ·
  两个 checker 入口 · `--self-test`。
- **触发车道**：治理套件（含电池）· 七个门禁组件。

## Change Focus

- **Primary module / causal owner:** `_backlog/_archived/_fixed_bugs/`（卡格式）+ doc-hygiene 的
  账本规则（校验）—— 前者定义"一张已修卡要说什么"，后者保证它说的话是真的。
- **Seam classification:** deterministic-guardrail —— 卡格式 + 静态校验。
- **Question:** 把"修复关联"从自由文本变成一个**可机械解析**的字段、并加一条守卫断言它点名的
  change 存在——能否在真实树（迁移 6 张卡后）上绿、在"点名不存在的 change"上红，且不改动任何
  既有判定？
- **Necessary adjacent/external contracts:** `_backlog/README.md` 与 `_backlog/bugs/README.md`
  （answers: 卡格式与状态词表的声明位置——新增字段要写进那里）· doc-hygiene 的 `RULES` 与
  `_rule_ledger_consistency`（answers: 规则落点与既有形状）· `doc_hygiene_battery` 的清单 pin
  （answers: 新守卫必须进正典电池，pin 随之更新）· `openspec/changes/` 与 `archive/` 的目录形态
  （answers: change 存在性的判定：活跃目录名，或归档目录的日期前缀名）。
- **Evidence seam:** 六张卡的 change 存在性先期实测 · 迁移后真实树绿 · 负例（不存在的 change）
  · 绿色控制（有效引用）· 清单 pin · 变异检查 · 七 checker + closeout · 治理套件 255。
- **Not in scope:** 校验"修复尚未落地就预填"（不做推断）· 把字段用于 `issues` 面（先只做 bugs；
  取证显示那边没有同类需求）· 解析 `修复关联` 正文（字段取代那个需求）· 任何产品代码 · CAS 空转。
- **Triggered review policies:** local-context, change-admission
