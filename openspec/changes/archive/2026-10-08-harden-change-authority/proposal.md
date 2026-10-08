# Proposal: Harden Change Authority

## Why

plan 裁决在案（`_backlog/plans/2026-10-08-application-corpus-adoption.md` C2）：v3 的
"驱动一下能干点但质量成问题"有两个机制级病灶——① agent 天然倾向在实现文件里
"顺手重新设计"，而偏离无常设登记处（仅 entry-surface 一次性披露先例）；② 交付记录
只写成功项，"没测的部分"最容易被生成文本的自信语气掩盖。语料（DeerFlow 应用开发
语料·卷二 02/03/04，钉定 v2.1.0）的解法是：spec 独占设计决策 + 实现工件自降权威 +
偏离登记不隐瞒 + red-green 自报 + AI 披露。本 change 按本仓形态（solo+agent、
guidance/checker 分层）落地，并把可机械的部分交给 checker。

## What Changes

- **`change-guidance/core/change-practice.md` 新增三组规则文本**：
  - **Scope rule**——实现工件（design/tasks）只排序与验证、不重新设计；设计决策
    归 owning spec/delta 与 design.md，偏离进 Deviation Register 而非顺手改；
  - **四类陈述**——引用上游/语料的结论必须标注：运行时事实 / 上游要求 / 应用仓
    建议 / 仓库自定，上游制度类条目永远标"上游参考"不冒充本仓要求；
  - **slice 收尾重读**——每个 slice 收尾跑 lint+test 并重读 spec 评审检查单
    （从 control-placement 触发泛化为常规纪律）。
- **tasks.md 常设两段（authoring 规则，自本 change 起对活跃 change 生效）**：
  - `## Deviation Register`——无偏离显式 `none: <rationale>`，有偏离逐条登记
    （偏离了什么、裁决依据、落在哪个工件）；空段即违规；
  - `## Delivery Record`——四段必填：外部行为 / 影响面 / 实际跑了什么 / **未执行的
    检查**；bug-fix 类 change 附 red-green 自问句（先红于 main 否？）；附 AI 参与
    披露段（solo+agent 裁剪版：工具、用法、责任确认一行）。
- **checker 扩展**：`check_change_guidance.py`（经 `change_guidance_kernel.py` 共享
  内核）新增 tasks.md 语法校验——活跃 change 的 tasks.md 存在时两段必须在场，
  Deviation Register 非空（`none:` 或至少一条登记），Delivery Record 四个字段标签
  在场；内容真伪仍属 apply/archive review（与 Focus Card 同哲学：checker 只关语法）。
- **负例 focused tests**：`openspec/tests/governance/` 新增测试文件——合规 fixture
  过、缺段红、空 register 红、缺四段字段红；CI unittest discover 自动纳入。
- **`openspec/config.yaml` 一字不动**（字符余量实测 0/11436）；规则正文住
  change-practice.md，机械语义住 checker——与 Focus Card 现状同构。

## Capabilities

### New Capabilities

none: 全部落在治理层（guidance 文本 + agent-owned checker + focused tests），
无规范级行为变更、无运行时面变化。

### Modified Capabilities

none: 既有 spec（含 ci-governance/doc-budgets/doc-truthfulness）的 requirement
均不变；`skip_specs: true` 已声明。governance README 对 checker 语义的登记
（checker 自有 docstring 拥有语义）是现状惯例，非 spec requirement。

## Impact

- 文件：`openspec/change-guidance/core/change-practice.md`（规则文本）、
  `openspec/governance/check_change_guidance.py` 与
  `openspec/governance/change_guidance_kernel.py`（语法校验扩展）、
  `openspec/tests/governance/` 新增测试文件、本 change 自身 `tasks.md`
  （dogfood 两段常设段）。
- 守卫：新规则必须能红（负例 fixture 直测）；既有 checker 全绿保持。
- 无代码、无运行时行为、无预算表变化、`deerflow/` gitlink 不触碰。
- 当前零活跃 change，无存量迁移；新规则自本 change 起对活跃 change 生效。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_change_guidance.py`
  与 `change-guidance/core/change-practice.md`——"变更工件必须自证权威与诚实交付"
  这一语义决策的最小 owner 是 change-guidance 治理层（规则文本住 guidance，
  机械语法住 checker，二者现状即如此分工）。
- **Seam classification:** deterministic-guardrail — 新增确定性工件语法门禁（段落在
  场、字段标签、非空 register），无认知角色、不产运行时行为。
- **Question:** 每个活跃 change 的 tasks.md 是否常设 Deviation Register 与四段
  Delivery Record，偏离是否无处可藏，且新守卫对缺段/空段/缺字段都能红？
- **Necessary adjacent/external contracts:** `change_guidance_kernel.py` 共享内核
  （answers: 扩展点复用与 Focus Card 语法哲学一致）；`openspec/tests/governance/`
  套件（answers: 负例测试落点与 CI unittest discover 发现路径）；doc-budgets
  （answers: config.yaml 0 余量故不动它，规则正文改住 change-practice.md）；
  closeout gate 聚合（answers: 新规则经既有 component checker 聚合执行，不加新 gate）。
- **Evidence seam:** 新增 focused unittest（负例 fixture → checker exit 1 并点名；
  合规 fixture → exit 0）+ 本 change 自身 tasks.md 落两段段后 checker 绿（dogfood）。
- **Not in scope:** C3 pin 修正与语料复制裁决；C6 产出质量断言面；config.yaml
  预算调整或规则改写；OpenSpec CLI 模板注入（模板归 CLI，本 change 只加规则
  与守卫）；AI 披露的多维护者签名制（solo+agent 形态不需要）。
- **Triggered review policies:** change-admission, local-context
