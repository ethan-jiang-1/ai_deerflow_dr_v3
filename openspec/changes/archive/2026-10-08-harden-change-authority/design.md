# Design

## Context

现状：Focus Card 语法由 `check_change_guidance.py` 硬编码实现（`config.yaml` 只需
含规则片段，`_validate_authoring_pointer` 验证在位），规则文本与机械语义分层——
文本住 change-guidance，语法住 checker，语义归属由 checker docstring 登记。
`openspec/config.yaml` 字符预算 11436/11436（余量 0），行预算 98/140。当前零活跃
change。`openspec/tests/governance/` 是 CI unittest discover 的治理测试家
（`python3 -m unittest discover -s openspec/tests/governance`）。

## Goals / Non-Goals

**Goals:**

- 偏离有常设登记处（无处可藏：空段即红）；
- 交付记录四段成段必填，"未执行的检查"获得与成功项同等的结构地位；
- 新守卫可红（负例 fixture 直测），语法语义分层与 Focus Card 同哲学。

**Non-Goals:**

- 不改 `openspec/config.yaml`（0 余量；ratchet 纪律下不为加规则涨预算）；
- 不做内容真伪的机器判定（四段写了什么、register 登记是否诚实，归 apply/archive
  review——checker 只关语法，与 Focus Card 的"grammar only"边界一致）；
- 不动 OpenSpec CLI 模板、不建新 gate、不建 spec capability。

## Decisions

**D1 两段常设段住 tasks.md，不住 proposal/design。**
Delivery Record 是 apply 期产物，住 proposal 会在 propose 期写死然后过期；单独
`delivery-record.md` 工件面要 checker 多管一个文件且多一份创建义务；closeout 文档
单方面要求则无 per-change 在场语法、仍靠自觉。tasks.md 是 checker 已 scoped 的
per-change 执行账本，两段随它走最短。
备选落败：proposal 常设段（时机错位）；独立工件（面变大）；仅 closeout 文档
（无机械在场性）。

**D2 checker 校验分级：存在才校验，语法才校验。**
tasks.md 不存在（plan 早期）→ 跳过新规则；存在 → `## Deviation Register` 与
`## Delivery Record` 必须在场；register 段非空（含 `none:` 行或至少一条登记）；
Delivery Record 四个字段标签在场（外部行为 / 影响面 / 实际跑了什么 / 未执行的
检查）。占位内容不判真伪。scoped 模式（gate 传 `--change`）与 standalone 扫描
（全部活跃 change）同规则。
备选落败：占位符探测（grep TODO 类标记——脆弱且制造绕过动机）；语义级校验
（越界，破坏 grammar-only 哲学）。

**D3 规则文本住 `change-practice.md`，config.yaml 不动。**
config.yaml 余量 0，涨预算需要 justification 且违背"deliberately tight"的立意；
Focus Card 的现状分工（文本在 guidance、片段指针在 config、语法在 checker）
已验证可行，新规则照抄该分工。`_validate_authoring_pointer` 只要求既有片段
在位，不动 config 即无破坏面。
备选落败：涨 config.yaml 预算加规则（可做但违背预算立意，且 98/140 行距
警戒尚远而字符已满——字符是硬约束）。

**D4 负例测试 = 新文件 `test_change_authority.py`，临时树 fixture。**
四类 case：合规（两段在场+register none+四标签）→ exit 0；缺 Deviation Register
→ 红；register 空段 → 红；缺任一 Delivery Record 字段 → 红。fixture 用 tempfile
构造最小 openspec 树，直调 checker main/内部入口，断言退出码与点名信息。归档
义务不变：新守卫在 CI unittest discover 中自动执行。

**D5 本 change 自身 tasks.md 落两段（dogfood）。**
C2 的 tasks.md 首个使用常设段：Deviation Register 登记实现期偏离（或 none），
Delivery Record 在 closeout 前填四段。守卫咬住的第一只兔子是自己。

## Alternatives

- **把四段/登记规则写进 config.yaml rules**：落败——字符余量 0/11436；行余量
  （98/140）有骗性，字符才是硬约束；涨预算违背 doc-budgets 的 ratchet 立意。
- **新规则做成独立 component checker（第七个）**：落败——closeout gate 的
  CHECKER_NAMES 聚合面、governance README 导航、CI 声明都要跟着动，为两条
  语法规则新增组件不成比例；扩展现有 change-guidance checker 语义最贴 owner。
- **register/record 住 design.md**：落败——design 是"怎么实现"，登记与交付
  记录是执行期事实；且 design 无常设结构约束的先例，tasks.md 才是逐任务
  打钩的账本。
- **red-green 自问做成全 change 必填**：落败——纯文档/纯结构 change 无
  red-green 可答；定为 bug-fix/行为类必填（本文按 change 类型裁量），避免
  仪式化空答。

## Risks / Trade-offs

- [两段常设段让小 change 模板变重] → 四段各一两行即可成段；`none:` 一行即合规；
  语料原话"小变更只有一段意图描述+验证方式"——权威唯一保留，形式随规模伸缩。
- [语法在场但内容空壳（"诚实性 theater"）] → 接受为 grammar-only 的已知边界，
  与 Focus Card 同；内容真伪由 apply/archive review 对 diff 与证据比对把关，
  本 change 不声称解决诚实性问题，只把"没测的部分"变成必填可见结构。
- [checker 扩展误伤既有流程（比如 Program 形态）] → Program/workstream 的
  tasks 结构不同，扩展规则对 Program 形态的适配在实现期验证，负例覆盖；
  发现冲突回 design 重裁不硬推。
- [change-practice.md 膨胀] → 三组规则合计控制在 ~25 行内；该文件无预算但
  有稀释风险，逐条只写"要求+一句为什么"。

## Migration Plan

零活跃 change → 无存量迁移。新规则自本 change 归档起对后续活跃 change 生效；
checker 扩展与负例测试随本 change 落地即进 CI。回滚 = revert guidance/checker/
tests 三个文件。

## Open Questions

none: 落点、分级、测试形态均已裁决；若实现期发现 Program 形态与 D2 冲突，
按 Risks 第 3 条回本 design 重裁。
