# Proposal: extract-doc-hygiene-test-battery

## Why

`check_doc_hygiene.py`（1196 行）的规则面是健康的：九条机械规则各自成函数，
一条目录范围规则（`_rule_docs_scope`）。问题在**它的证据面被内联进了产品模块**——
`_self_test()`（`check_doc_hygiene.py:727`，442 行）内嵌 31 条负例控制，
这正是 `test-evidence-policy` 要求的"守卫必须能变红"。

代价有三条，都可直测：

1. **证据不可发现**：31 条负例只有 `--self-test` 一条通道；CI 的
   `python3 -m unittest discover -s openspec/tests/governance` 根本看不见它们，
   该 1196 行模块**没有对应的 unittest 文件**。
2. **变更成本被放大**：九条规则直接读 30 个模块级常量，`violations()`
   （`:713`）手列九个调用；加一条规则 = 改调度 + 改常量表 + 改内联电池。
   这正是把模块推到 1196 行的变更模式。
3. **测试夹具与产品代码同址**：`MARKER_ALLOWLIST`（`:376`）在 self-test 里被就地
   改写再还原——一条规则读的全局量，被测试过程改。

现在做，是因为它是唯一一条**零行为风险**的高收益切口：改动全在
`openspec/governance/`（治理脚本的内部结构不被任何 spec 的 requirement 管辖），
且它同时是后续阶段（拆三座大山、加体积守卫）的前置——不先把规则与夹具的接缝
做出来，后面的拆分没有落点。

## What Changes

- **规则注册表化**（`check_doc_hygiene.py`）：`violations()` 从手列九个调用改为
  遍历一个冻结的 `RULES` 元组；每条规则成为可单独调用的
  `check(scope) -> list[str]`，`scope` 携带根路径与声明表，**规则不再直接读模块级全局量**。
- **31 条负例控制抽出为可发现的 unittest**：新增
  `openspec/tests/governance/test_doc_hygiene.py`，按规则分组成 `TestCase`；
  CI 既有的 discover 命令因此**首次真正跑到这份电池**。
- **`--self-test` 保留为薄委托（行为不变）**：命令、stdout 文本
  （`doc-hygiene self-test passed.`）、退出码全部不变；实现改为遍历**同一份**
  负例注册表，模块内不留第二份断言代码。
- **九条规则各配一条正向/负向验收**：`test_doc_hygiene.py` 另含"干净夹具零违规"
  与每规则的靶向负例，使今后的规则改动有就地证据。
- **登记与文档同步**：`openspec/governance/README.md` 第 18/68-69 行更新为
  "负例电池现已进
  `unittest discover -s openspec/tests/governance`，`--self-test` 是其薄委托入口"；
  新测试文件落在既有 `openspec/tests/governance/` 目录声明下（`required-paths.toml:187`），
  **无新增注册路径**。

**不变量（本 change 的验收核心）**：31 条负例断言标识逐条对应（少一条即判回归）；
`--self-test` 的 stdout 与退出码逐字不变；`check_doc_hygiene.py` 的 plain 模式退出码
与违规文本不变。

## Capabilities

### New Capabilities

<!-- none: 治理 checker 的内部结构不被任何 capability 的 requirement 管辖——本 change
     不改变任何可观察行为，也不新增契约面。按 rules 的要求，不为凑 validates 发明需求。 -->

### Modified Capabilities

<!-- none: 同上。doc-truthfulness 的 "The rule proves it can fail (self-test)" scenario
     描述的是可观察行为（checker 构建临时树并证明能红），本 change 保持该行为不变，
     只改电池的存放位置与调用形态。 -->

## Impact

- **改**：`openspec/governance/check_doc_hygiene.py`（拆分 scope/注册表/薄委托；
  文件体量下降，规则语义零变化）。
- **新增**：`openspec/tests/governance/test_doc_hygiene.py`。
- **文档**：`openspec/governance/README.md`（第 18、68-69 行的自述同步）。
- **登记**：无新增 required-path；`project-structure.toml` 与生成块（`AGENTS.md`）不动
  ——本 change 不增删改任何登记路径。
- **CI/hook**：命令字符串与所在文件 `check_doc_hygiene.py` **不变**，因此
  `.github/workflows/governance.yml:54` 与 `.githooks/pre-commit:10` 零改动；
  `check_ci_governance.py` 声明的 canonical 命令集不受影响。
- **边界**：不修改、不深读 `deerflow/` gitlink；不触碰 `deep_research_harness/`
  的任何源码或测试；不改任何 `openspec/specs/` 主干。
- **触发车道**：`python3 -m unittest discover -s openspec/tests/governance`（治理套件）
  与 `check_project_gate.py --phase closeout`；harness 的 `make verify` 与 `make smoke`
  不受影响（本 change 不含 harness 文件）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` ——
  文档层卫生守卫本身；它拥有"规则如何被调度"与"守卫如何证明自己能红"这两个决定。
- **Seam classification:** deterministic-guardrail —— 纯机械判定引擎，无模型参与；
  本 change 只改它的内部结构，不改任何判定语义。
- **Question:** 442 行内联负例电池能否整体变成 `unittest discover` 真正跑得到的测试文件，
  同时保持 `--self-test` 的 CLI 契约（命令、stdout、退出码）与 31 条断言标识逐条不变？
- **Necessary adjacent/external contracts:** `openspec/specs/doc-truthfulness/spec.md`
  （answers: 守卫"能变红"的可观察行为在本 change 后是否仍成立——该 spec 的 Scenario
  "The rule proves it can fail (self-test)" 以 `--self-test` 为证据入口，故该命令必须
  存活且语义不变）；`openspec/governance/README.md`（answers: checker 的角色自述
  ——standalone / 非 gate 组件 / 非 `make verify` 目标——是否被抽测试改变？答：不变，
  仅补一句电池位置）；`.github/workflows/governance.yml` 与 `.githooks/pre-commit`
  （answers: 精确路径与退出码契约是否保持？答：不变，故零改动）；
  `openspec/governance/required-paths.toml`（answers: 是否新增需登记的路径？答：新文件
  落在既有目录声明下，无新增）。显式排除 `check_project_gate.py`（answers: 是否需把
  doc-hygiene 纳入 gate 组件清单？答：不需要——它保持 gate 之外的独立检查，本 change
  不改变这个既定选择）。
- **Evidence seam:** 六条门禁退出码直测（治理套件 / `--self-test` / plain /
  closeout gate / architecture）＋ 31 条负例断言标识的逐条对账 ＋
  `unittest discover` 报告的用例数（基线 99 methods，本 change 后必须 ≥ 99 + 31）。
- **Not in scope:** 拆文件（三座大山拆分是下一阶段）；代码体积预算守卫
  （`code-budgets` capability，第三阶段）；179 行 `_rule_ledger_consistency` 的内部分解；
  `change_guidance_kernel.py` 的 ~157 行死码清偿；任何 `deep_research_harness/` 改动；
  任何 DeerFlow 侧边界。
- **Triggered review policies:** local-context, authority-and-projections, change-admission
