# Proposal: Narrow Skill Surface

## Why

实测（本地 runs/d_20261007 两个 bundle 的 assembly-snapshot）：`available_skills=None`
时框架把全部约 30 个 skill 的目录索引（名称+描述+路径，XML 段）注入 system prompt
（33589 字节、163 处 skill 提及）——每次研究运行都背着播客生成、PPT、多啦A梦模板等
无关 skill 的上下文噪音与 token 成本，还扩大了 agent 的注意力面。声明槽已在
a8fe53a 就绪（config 声明 → assembly 解析 → binding 透传，缺省 None 行为不变）；
B1 用它把研究运行的可见目录收窄到 `deep-research` 一个。

## What Changes

- **两梯声明窄面**：`config/base.yaml` 与 `config/fixture.yaml` 声明
  `skills: [deep-research]`——真实研究与 fixture 演练一律只看到 deep-research 索引；
  agent 是否加载/遵循该 skill 仍由 agent 决定（收窄可见面 ≠ 强制使用）。
- **config-as-contract 守卫**：`tests/contract/test_skill_declaration.py` 增断言——
  base 与 fixture 各自声明恰为 `["deep-research"]`（窄面决策被机械钉住，改声明必红）。
- **窄索引旅程证据（零凭证）**：`tests/integration/test_cli_journey.py` 增断言——
  fixture create 后 snapshot 的 system prompt 含 `deep-research` 且**不含**
  无关 skill（如 `podcast-generation`）；这是"声明真的收窄了模型可见面"的端到端证明，
  同时是声明名失效（框架静默丢弃/找不到）的确定性绊线。
- **不动**：`resolve_skills` 语义（缺省仍严格 None）、binding 透传、skill 正文加载机制
  （渐进披露）、tool posture 执法（框架 skill_tool_policy）、admission、诊断分类。
  **不做**强制加载（agent 用不用方法论仍是它自己的决定——那是未来的质量问题不是接线问题）。

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `deerflow-wiring`: MODIFIED——"Skill selection is declared, not implicit" 从"缺省未接线"
  升级为"两梯声明窄研究面"：base/fixture 各自声明恰为 `deep-research`；缺省声明的
  未接线姿态保持；守卫扩为同时钉住各梯的声明姿态。

## Impact

- 修改：`config/base.yaml`、`config/fixture.yaml`（声明段从注释变为实声明）、
  `tests/contract/test_skill_declaration.py`（+守卫）、
  `tests/integration/test_cli_journey.py`（+窄索引断言）、
  `docs/research-process.md` 与 `docs/control-map.md`（skill 面事实更正：None=全目录
  索引已可见；两梯现声明窄面；"强制加载"仍未实现且不在本 change）。
- 触发 lane：`make verify`（config/contract）与 `make smoke`（旅程 + snapshot）。
- **边界声明**：不修改、不深读 `deerflow/` gitlink；`available_skills` 是已在 contract
  mirror 登记的公开构造参数。所述行为均为本 change 范围，非现状。

## Change Focus

- **Primary module / causal owner:** 两梯 config 的 skill 声明语义——"研究运行只看
  deep-research"这个模型可见面的决策；binding 透传与解析已由前序 change 落地。
- **Seam classification:** cognitive-program — 改变的是注入 system prompt 的 skill
  目录索引（模型可见上下文），机制虽是 config 声明，语义是认知面收窄；不强制使用、
  不触 tool 执法、不改 admission。
- **Question:** 把两梯的可见 skill 目录收窄到 deep-research 后，能否用零凭证证据
  （config-as-contract + 真实 CLI 旅程的窄索引断言）机械证明收窄生效，且 fixture
  演练链路（装配/状态/准入/报告）全程不回归？
- **Necessary adjacent/external contracts:** deerflow-wiring spec（answers: 声明姿态
  从缺省未接线升级为两梯窄面的规范权威）；node-agent profile（answers: 模型可见
  上下文变更的信任边界、tool 执法归属与失败界的认知合同）；delivery-lanes
  （answers: config+contract 变更走 verify、旅程走 smoke）。
- **Evidence seam:** contract 守卫红绿（先红：声明未落时断言 base 声明恰为
  deep-research 必失败）；smoke 旅程窄索引断言（deep-research 在、无关 skill 不在）；
  verify/smoke 全绿 + test ID 对照。
- **Not in scope:** 强制加载/方法论遵循质量（真实梯评审，另立项）；声明面宽度调整
  （加更多 skill = 另一 change）；skill 正文内容修改；subagent 的 skill 面。
- **Triggered review policies:** node-agent-workflow-integrity, local-context, change-admission, deerflow-downstream-boundary

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| lead agent 的 system prompt 中注入的 skill 目录索引（名称+描述+路径） | node-agent | agent 可见与可选加载的 skill 目录被收窄为 deep-research；是否加载、是否遵循方法论仍是 agent 的决定，本 change 不强制、不注入正文 | skill 名单来自 checked-in 两梯 config（操作者权威）；skill 正文来自 pin 住的仓库根框架投影（repo 信任、manifest 双签名）；研究问题文本仍是分隔的不可信内容，本 change 不触碰 | 框架 skill_tool_policy middleware 运行时执法 per-skill 工具过滤；声明不授予任何工具/权限/路由，只收窄 middleware 可见的目录 | 无 candidate admission 变更：最终报告准入仍是 engine validator/gate + runtime admission（不变） | 声明名失效（框架静默丢弃/找不到）：旅程的窄索引断言即绊线，变红即暴露；框架侧注入异常落既有 diagnose 分类（model_call_failed/framework_crash） | config-as-contract 单测钉两梯声明恰为 [deep-research]；fixture 旅程断言 snapshot 索引含 deep-research、不含无关 skill（零凭证） |
