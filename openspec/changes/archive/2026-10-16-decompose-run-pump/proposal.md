# Proposal: decompose-run-pump

## Why

`deep_research_harness/src/deerflow_deep_research/runtime/pump.py` 是应用侧唯一的结构胖点：
450 行里塞了**四个互不相干的职责**——单个回合的流→观测适配（`_consume_turn` 112 行）、
计划闸与澄清策略、交付提交（`_record_delivery` / `_submit_final_report`）、以及一个 watch
工具（`tail_journal` 25 行）；驱动循环 `_drive`（131 行、8 个位置参数）把五种策略串在
一个 while 里。

同时，**终端事件名是一条未注册的字符串协议**，散在四处共 31 个点：写方
`pump.py`（14）、分类器 `domain/diagnosis.py`（8，其中 `classify` 是 7 分支 if 链）、
渲染 `runtime/interaction/render.py`（7）、状态→事件映射 `interaction/cli.py`（2）。
加一个新结局要改四个文件，而没有任何一处声明"合法结局集合"是什么。

第三处：**同一份组合/config 词汇有四张表**——`domain/bundle.py:36` 的
`COMPOSITIONS = ("fixture", "mixed", "all_real")`、`runtime/assembly.py:71` 的
`{"fixture": "fixture", "all_real": "base"}`、`runtime/adapters/client.py:16` 的
`CONFIG_NAMES = ("base", "fixture", "record")`、`interaction/cli.py:278` 的 argparse
`choices=["fixture", "base", "record"]`。四张表可以互相矛盾而无人报警（`mixed` 已在
assembly 里是"声明但未接线"的抛错值）。

现在做，是因为治理侧三个阶段（1–3）已把"可搜、可改、有守卫"的模式立住，应用侧这处
债是同一场收敛的最后一块；且它的验收边界可以做得极硬——**测试零改动**。

## What Changes

- **`pump.py` 拆为「薄模块 + 子包」**：`runtime/pump.py` 保留公共入口
  （`run_research`、`tail_journal`）与**契约测试锁定的两个名**
  （`_record_delivery`、`_submit_final_report`——它们改为委托壳），实现移入
  `runtime/pump_parts/`：`turn.py`（流→观测适配 + `TurnOutcome` 类型化返回）、
  `gates.py`（计划闸 + 澄清策略）、`deliver.py`（交付提交实现）、`journal.py`
  （`tail_journal` 与 journal 写入助手）。
- **终端事件协议收敛为一张 domain 表**：`domain/` 新增结局声明（事件名 + 分类 +
  可读文案的单一来源），写方/分类器/渲染/状态映射四处改为读它；`diagnosis.classify`
  的 7 分支 if 链改为查表。
- **四张组合注册表收敛为一张**：`domain/bundle.py` 拥有唯一声明，其余三处派生
  （`assembly` 的梯子映射、`client` 的 config 名单、`cli` 的 argparse choices）；
  `mixed` 的"声明但未接线"姿态显式写在唯一声明旁。
- **类型化回合结果**：`_consume_turn` 的 5 元组返回改为 `TurnOutcome`
  （typed dataclass），`_drive` 的参数从 8 个位置参数降到 3–4 个；`_drive` 拆为
  计划闸步 / 澄清步 / 收尾步三个具名函数。

**不变量（本 change 的验收核心，比前三个阶段更严）**：`make verify` 与 `make smoke`
**不改一行测试而全绿**；journal 事件名集合与**顺序**逐字不变；终端转移结果不变；
四张注册表现有取值集合不变（含 `mixed` 的抛错行为）。

## Capabilities

### New Capabilities

<!-- none: 本 change 只重组既有实现，不新增可观察行为；终端结局集合已由 run-bundle /
     run-admission 的既有 requirement 约束，收敛的是它的**声明位置**而非语义。 -->

### Modified Capabilities

<!-- none: 行为零变化。四张注册表与终端事件名的收敛不改变任何现有取值、失败面或转移；
     若 apply 中发现某处收敛必然改变可观察行为（例如 `mixed` 的抛错时机），记入
     Deviation Register 并停在 propose 边界请 owner 裁决。 -->

## Impact

- **改**：`runtime/pump.py`（450 → 薄模块）；`domain/diagnosis.py`（分类改查表）；
  `runtime/interaction/render.py`、`interaction/cli.py`（读声明表）；
  `domain/bundle.py`、`runtime/assembly.py`、`runtime/adapters/client.py`
  （注册表派生）；`runtime/bundle/journal.py`（接收 `tail_journal` 的落点候选）。
- **新增**：`runtime/pump_parts/`（4 模块）。
- **登记**：`required-paths.toml` 增子包与其模块。
- **不动**：`tests/` **一行不改**（硬约束）；`deerflow/` gitlink；
  `openspec/governance/`；任何 spec 主干。
- **触发车道**：`make verify`（单元门禁）与 `make smoke`（集成，真框架组装 + 脚本模型）；
  治理侧 `check_project_architecture.py`（导入矩阵：新子包必须遵守
  `domain ← engine ← runtime` 方向与 `[imports]` 白名单）。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/pump.py`
  —— 它拥有"一回合怎么被消费、结局怎么被决定、交付怎么被提交"这三个决定。
- **Seam classification:** wiring —— 组合与流适配的重组；终端转移规则本身属
  `domain/state_machine.py`（本 change 不动其语义）。
- **Question:** 450 行的运行泵能否拆成「薄模块 + 职责子包」、并把散在四处的终端事件协议
  与四张组合注册表各自收敛为一张声明——而 **`make verify` 与 `make smoke` 在不改任何
  测试文件的前提下全绿**、journal 事件名与顺序逐字不变？
- **Necessary adjacent/external contracts:** `tests/contract/test_entry_chain.py`
  （answers: 契约测试用 AST 锁定 `runtime/pump.py` 里的 `_record_delivery` 与
  `_submit_final_report`，并要求前者调用后者、后者调用 `submit_artifact`；测试不改，
  故这两个名必须留在 `pump.py` 且保持原调用形状——实现可移入子模块，入口留委托壳）；
  `tests/unit/runtime/test_run_engine.py` 与 `test_event_stream_replay.py`
  （answers: 只用 `pump.run_research` 这一公共入口，故内部可自由重组；但它们对 journal
  事件名有精确断言，故事件名与顺序是硬约束）；`tests/unit/interaction/test_entry_surface.py`
  （answers: 用 `pump.tail_journal`，故该名必须保留）；`runtime/state_machine` 与
  `bundle/ledger` 的既有契约（answers: 终端转移与准入语义不动，只改调用形状）。
- **Evidence seam:** `UV_OFFLINE=1 make verify`（离线单元门禁，含 5 个直接驱动 pump 的
  测试文件）· `make smoke`（集成：真框架组装 + 脚本模型驱动的全旅程）·
  `git diff --stat -- tests/` 为空（测试零改动的机器证明）· journal 事件序列的
  前后逐字对照（用既有测试夹具与一次真实回放）。
- **Not in scope:** 任何终端转移语义、准入语义、journal 条目字段的修改；`domain/state_machine.py`
  的规则表；澄清/计划闸的**行为**（只改它们的代码位置与返回形状）；harness 的 CLI 动词语义；
  测试目录的重排与改名（属阶段 5）；`validate_owner_alive` 之类域外工具。
- **Triggered review policies:** workflow-outcome-review, control-placement, local-context, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| 流形状变化（框架换事件家族） | `runtime/pump_parts/turn.py`（唯一的流→观测适配点） | 既有"快照优先、chunk 回退"姿态不变；本 change 不改判定 | 保持原样（不改终端转移） | 无新动作 | 既有 31 处事件重放测试 + 绿野夹具回放 |
| 流中途抛错 | `run_research` 的异常面（框架/流错误） | 既有 `failed-resume` 转移不变 | 保持原样 | 无新动作 | `test_run_engine` 的 framework_error 用例 + `make smoke` |
| 交付提交（空答复/被拒/准入） | `_submit_final_report` → ledger 准入（hold point） | 既有 admit/replay/rejected/no-answer 映射不变 | 保持原样 | 无新动作 | 契约测试 link 4（AST 锁）+ `test_run_engine` 交付用例 |
| 澄清/计划闸被绕过 | `runtime/pump_parts/gates.py` | 既有 journal 记录面不变（absorbed / degraded / skipped） | 保持原样 | 无新动作 | `test_run_engine` 澄清与计划用例 + 吸收事件回归 |

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| 一回合的观测如何从流中得出 | 无（纯机械适配） | `domain/clarification.py` 的检测谓词（不改） | non-bypassable | journal 事件名与顺序逐字不变 | 5 元组返回 → 类型化 `TurnOutcome`，去掉 8 个位置参数 | `test_run_engine` + `test_event_stream_replay` |
| 终端结局的合法集合 | 无 | `domain/state_machine.py` 的规则（不改）；新增的只是一张**声明表** | advisory | 转移语义零变化 | 四处字符串协议 → 一张表；4 个改动点 → 1 个 | 四处消费者逐字对照 + `make smoke` |
| 组合/config 词汇 | 无 | `domain/bundle.py`（唯一声明） | advisory | `mixed` 的抛错姿态不变 | 4 张表 → 1 张 | 四张表现有取值集合对照 + CLI `--help` 输出 |
