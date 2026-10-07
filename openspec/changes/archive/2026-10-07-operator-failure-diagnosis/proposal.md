# Proposal: Operator Failure Diagnosis

## Why

一次运行落在 `failed-resume` 后，操作者要自己翻三处文件做关联才能回答"断在哪"：
`state.json`（终态 + delivery 三态）、`diagnostics/journal.jsonl`（终态事件的原因字段）、
以及 `diagnostics/searches/` / `assembly-snapshot.json` / `unanswered-clarifications.json`
（失败前后的证据）。`status` 和 `inspect` 只陈列不分类——六类终态原因（模型调用失败/
框架崩溃/框架停止/澄清耗尽/取消/owner 死亡转移）加上"完成但未交付"共七种情形，全部
靠人脑对表。操作者唯一的快速验证手段因此仍然偏端到端：看到失败，不知道是配置错、
凭证错、还是 harness 控制 bug，只能重跑整场。

## What Changes

- **新增第七个动词 `diagnose <bundle_id>`**：读 Bundle 持久事实（state、journal、
  diagnostics 目录存在性），渲染一份**分类诊断**——终态类别、拥有该失败条件的链条环节、
  该类别的具体证据文件指针。是投影：不修改 state/journal/任何 Bundle 工件。
- **新增纯分类器 `domain/diagnosis.py`**：typed 输入（BundleState + journal 终态事件 +
  diagnostics 文件存在性）→ typed 诊断结果（类别 + 环节 + 证据指针）。零 I/O、零框架
  import，分类规则是本次变更的语义核心。
- **`diagnose` 覆盖的类别**（与 pump 终态事件一一对应，外加一个被动转移）：模型调用失败
  （`llm_error_fallback`，带 error_type）、框架崩溃（`framework_error`，带异常名）、框架
  主动停止（`stop_reason`）、澄清耗尽（指向 unanswered-clarifications.json）、操作者取消
  （`run_cancelled`）、owner 死亡转移（active 状态 + 死 PID，无终态 journal——最隐蔽类）、
  完成但未交付（completed 且 delivery 为 None/rejected——belt 检查）；active 运行不分类，
  如实报告"仍在运行"。
- **渲染走共享 vocabulary**：`interaction/render.py` 增诊断行渲染，与 status/watch 共用
  phrase 风格；COMMANDS.md 登记第七动词。
- **不变**：六动词既有语义、state machine 规则、pump 终态判定、admission、任何 Bundle
  路径合同。diagnose 只读，不改发现合同与收集合同。

## Capabilities

### New Capabilities

<!-- none: 动词面与分类规则都落在既有 capability -->

### Modified Capabilities

- `entry-surface`: MODIFIED——"Six verbs mirror the state machine and observation layers"
  扩为七动词（新增 `diagnose` 及其分类合同与只读边界）；存续 requirement 文本与既有
  scenario 逐字保留。

## Impact

- 新增：`src/deerflow_deep_research/domain/diagnosis.py`（纯分类器 + typed 合同）、
  `tests/unit/domain/test_diagnosis.py`（七类覆盖 + 非分类负例）。
- 修改：`runtime/interaction/cli.py`（`cmd_diagnose` + argparse 注册）、
  `runtime/interaction/render.py`（诊断渲染）、`tests/unit/interaction/test_entry_surface.py`
  或新文件（渲染 + verb 面测试）、`COMMANDS.md`（动词菜单）、
  `tests/unit/interaction/test_command_surface.py`（三处动词清单一致性会自动变红驱动同步）。
- integration：`tests/integration/test_cli_journey.py` 增一段——用既有 raising fixture
  model 跑一次 create 到 failed-resume，然后 `diagnose` 输出模型调用失败类别
  （零凭证，走 smoke）。
- 登记：`openspec/governance/required-paths.toml`（diagnosis.py + 两个测试文件）、
  `deep_research_harness/AGENTS.md` 无需改（路由已覆盖）。
- 触发 lane：`make verify`（src+tests）与 `make smoke`（interaction 变更 + 新旅程）。
- **边界声明**：不修改、不深读 `deerflow/` gitlink；diagnose 是人读投影，不成为生命周期
  权威（state/journal 仍是唯一事实源）——投影不得进入写许可或身份比较。所述行为均为
  本 change 范围，非现状。

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/domain/diagnosis.py` 的
  分类规则——七类终态的判定与证据指针是这个变更唯一的语义决策；verb 与渲染是它的投影面。
- **Seam classification:** wiring — 把已持久化的事实组合成人读投影；分类器虽是 typed 纯
  函数，但不创建控制权、不拦截任何流、不裁决准入（裁决语义仍在 engine），故非
  deterministic-guardrail。
- **Question:** 七类终态（含无终态 journal 的 owner 死亡转移）能否被一个零 I/O 纯分类器
  唯一判定，且 `diagnose` 动词在不触碰 state/journal 写路径、不复制状态权威的前提下，
  把"断在哪 + 下一步看什么"压缩成一条命令？
- **Necessary adjacent/external contracts:** entry-surface spec（answers: 六动词集合扩为
  七的规范权威与存续文本）；domain/state_machine + journal_policy（answers: 终态与 journal
  词汇是分类器的输入合同，分类器不得重定义它们）；run-bundle 路径合同
  （answers: 证据指针指向的 diagnostics 文件名由 domain/bundle.py 拥有，分类器只引用）。
- **Evidence seam:** 单测红绿在 `tests/unit/domain/test_diagnosis.py`（每类一个真实形状
  输入，owner 死亡类用死 PID 构造）；verb 面与渲染在 unit interaction；集成旅程用
  raising fixture model 走真 CLI 子进程（smoke 车道，零凭证）。命令面一致性由既有
  `test_command_surface` 守卫自动变红驱动三处同步。
- **Not in scope:** 修复任何失败本身；重试/恢复自动化；checkpoint.sqlite 的解析（仍属
  框架 checkpointer）；`watch`/`status`/`inspect` 的行为改动；真实模型质量评估。
- **Triggered review policies:** local-context, agent-information-map, authority-and-projections, change-admission
