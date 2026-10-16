# Design

## Context

动机见 `proposal.md` — Why。这里只记塑造形态的实测事实与硬约束。

**`pump.py` 的现状（450 行 / 11 个顶层函数）**

| 函数 | 行数 | 职责 |
|---|---|---|
| `_consume_turn` | 112 | 流→观测适配（values 快照优先、messages-tuple 回退、journal 聚合） |
| `_drive` | 131 | 驱动循环：计划闸 / 澄清 / 取消 / 错误回退 / 收尾，五种策略串在一个 while |
| `run_research` | 41 | 公共入口：读状态、选消息、异常兜底 |
| `_record_delivery` | 26 | 交付事实（**契约锁定**） |
| `_submit_final_report` | 21 | 最终报告提交（**契约锁定**） |
| `tail_journal` | 25 | watch 工具（测试调用公共名） |
| `_journal` / `_now_iso` / `_msg_field` / `_json_arguments` / `_is_framework_clarification_echo` | 2–7 | 微助手 |

**四条硬约束**

1. **测试一行不改**（本 change 的核心不变量）。`tests/` 下的文件一个字节都不动；红了就是
   实现错了，不许把测试改绿。
2. **契约测试 AST 锁定两个私有名**：`tests/contract/test_entry_chain.py:146-162` 解析
   `runtime/pump.py`，要求其中存在 `_record_delivery` 与 `_submit_final_report`，且前者
   调用后者、后者调用 `submit_artifact`。→ 这两个名**必须留在 `pump.py`**，且必须保持
   "前者调用后者"的调用形状。
3. **`pump.py` 必须是模块而非包**：同一文件的路径常量（如测试侧的
   `runtime/pump.py`）与 `runtime/__init__.py` 的 docstring 都指着它；改成包会破坏路径
   契约（阶段 2 的教训：入口路径是承重的）。
4. **公共名可达**：测试只用 `pump.run_research` 与 `pump.tail_journal` 两个名字，
   零私有名（已 grep 确认）；`assembly.py:156` 用 `pump.run_research`，
   `interaction/cli.py:176` 用 `pump.tail_journal`。两者必须继续从 `pump` 可达。

## Goals / Non-Goals

**Goals:**

1. 四个职责各有其模块与名字；`_drive` 从 131 行降到 ≤60，参数从 8 个降到 ≤4。
2. 终端事件名与组合/config 词汇各自收敛为**一张声明**，四处消费者改为读它。
3. journal 事件名集合与顺序、终端转移结果、四张注册表现有取值集合**逐字不变**。
4. `make verify` 与 `make smoke` 在**测试零改动**下全绿。

**Non-Goals:**

- 不改任何终端转移、准入、澄清/计划闸的**行为**。
- 不动 `domain/state_machine.py` 的规则表。
- 不碰 `deerflow/`、`openspec/governance/`、测试目录重排（后者属阶段 5）。
- 不为"更漂亮"而引入新依赖或抽象层。

## Decisions

### D-1｜`pump.py` 保留为模块，实现移入 `runtime/pump_parts/`

- **选**：`pump.py` 保留 `run_research`（入口）、`tail_journal`（测试可达）与两个委托壳
  `_record_delivery` / `_submit_final_report`；实现移入 `runtime/pump_parts/`
  （`turn.py` / `gates.py` / `deliver.py` / `journal.py`）。
- **为什么委托壳而不是整体搬走**：约束 2 的 AST 断言要求 `pump.py` 里存在这两个函数体，
  且 `_record_delivery` 的函数体里出现 `_submit_final_report` 这个**调用名**。委托壳满足
  两点（壳里调用同名实现——实现函数名不变，只是模块变了）。
- **代价**：`pump.py` 里留两个一行的壳。
- **换来**：契约不改、测试不改，而实现可以自由组织。
- 备选：把契约测试改指向新模块——否决（违反约束 1，且契约测试的存在正是为了锁住这条链）。

### D-2｜`tail_journal` 的实现移入 `bundle/journal.py`，`pump` 侧重新导出

- **选**：`tail_journal` 的正文放 `runtime/bundle/journal.py`（journal I/O 的既有归属），
  `pump.py` 里 `from .bundle.journal import tail_journal` 使公共名继续可达。
- **代价**：多一次导入跳转。
- **换来**：watch 工具离开运行泵，"pump" 名副其实；契约测试与 `cli.py` 均不受影响。
- 备选：留在 `pump.py`——否决：正是 proposal 指出的"泵里塞了 watch 工具"。

### D-3｜终端事件协议：domain 一张声明表，四处消费者读它

- **选**：`domain/` 新增 `outcomes.py`，声明**唯一**的结局表（事件名 + 由它派生的分类
  标签 + 可读文案）。写方（pump）、分类器（`diagnosis.classify`）、渲染（`render`）、
  状态→事件映射（`cli`）全部改为查这张表；`classify` 的 7 分支 if 链改为遍历表项。
- **为什么加"文案"**：渲染侧现在自带 7 处文案，与事件名一一对应；把文案放进同一行声明，
  加一个结局就只改一行。
- **代价**：domain 多一个模块与一张表。
- **换来**：加一个新结局从"改 4 个文件"变为"改 1 行"；且"合法结局集合"第一次有声明面。
- 备选：把表放 runtime——否决：结局名是 domain 词汇（`state_machine` 的规则产出它们），
  放 runtime 会让 domain 的消费者反向依赖 runtime。

### D-4｜组合/config 词汇：`domain/bundle.py` 唯一声明，三处派生

- **选**：`bundle.py` 的声明扩为"composition → (config 名, 是否已接线)"的唯一表；
  `assembly.config_name_for_composition` 查它、`client.CONFIG_NAMES` 从中派生、
  `cli` 的 argparse `choices` 也从中派生。
- **`mixed` 的姿态**：它在表里显式标注"声明但未接线"，`assembly` 继续对它抛错——
  **抛错行为与文案逐字不变**（这是现有的、被测试覆盖的行为）。
- **代价**：三处从"自带常量"变为"派生表达式"。
- **换来**：四张表不可能再互相矛盾；`--config` 的可选值不再可能与装配面脱节。
- 备选：把表放 runtime/assembly——否决：composition 是 bundle 的领域词汇
  （`BundleState.composition` 的取值），声明应随它。

### D-5｜类型化 `TurnOutcome`，`_drive` 拆三步

- **选**：`pump_parts/turn.py` 定义冻结的 `TurnOutcome`（tool_calls / answered /
  stop_reason / fallback_error_type / final_text），`_consume_turn` 返回它而不是 5 元组；
  `_drive` 拆为 `_plan_gate_step` / `_clarification_step` / `_finish` 三个具名函数，
  参数从 8 个位置参数降到 3–4 个（handle、stream_fn、outcome、hooks 打包）。
- **代价**：一个新类型；`_drive` 的循环体变成三次调用。
- **换来**：五种策略各有名字与落点；返回形状自带字段名（现在是位置元组，读代码要数位置）。
- 备选：维持元组——否决：这是修 `_consume_turn` 可读性的主要收益。

## Alternatives

- **A-1 把 `pump.py` 改成包（`runtime/pump/`）**：路径常量与 `runtime/__init__` docstring
  都指着 `pump.py`；阶段 2 的教训是承重路径不可动。否。
- **A-2 让契约测试改指向新模块**：违反"测试零改动"这一本 change 的核心不变量，而该契约
  的存在意义正是锁住这条链。否。
- **A-3 顺手把 `domain/state_machine.py` 的规则表也"现代化"**：那是终端语义的 owner，
  本 change 只改**调用形状**。否。
- **A-4 把四张注册表收敛到 runtime 而非 domain**：会让 domain 的消费者反向依赖 runtime
  （违反导入矩阵）。否。
- **A-5 借机给 journal 条目加字段（如 turn 序号）**：跨面词汇的演进要加可选字段并配契约
  测试（config 的 rules.design 要求）；本 change 的边界是"位置不变"，加字段属另一件事。否。

## Risks / Trade-offs

- [拆分让某一处 journal 事件名或顺序变了] → 硬证据：既有测试对事件名与顺序有精确断言
  （`test_run_engine` 多处 `assertIn` 与顺序断言），加上 `make smoke` 的旅程；任务里另加
  一次"journal 序列前后逐字对照"。
- [委托壳被后续维护者当成"应该删掉的重复"] → 壳上写明契约来源与为何不能删（指向契约测试
  与行号），并让 `_record_delivery` 的壳体**只有一行**，一眼看出是委托。
- [四张注册表派生后某处取值集合变了] → 任务里对四处逐一对账（含 CLI `--help` 的
  `choices` 输出与 `assembly` 对 `mixed` 的抛错文案）。
- [`_drive` 拆分改变循环控制流（continue/return 语义）] → 拆分只做"提取具名步骤"，
  每个步骤返回"是否继续 + 是否终结"的显式信号，**不重排**任何分支顺序；`make smoke`
  的完整旅程与 `test_run_engine` 的终端用例是判据。
- [新子包违反导入矩阵] → `check_project_architecture.py` 会逐行扫 harness 源码根；
  `pump_parts` 属 runtime 层，只允许 domain/engine/agents 与白名单外部命名空间。
- [本 change 是 harness 面，回滚成本高于前三阶段] → 每步一个提交、每步以"verify 绿"为
  边界；任一步红即回滚该步 diff，不留半成品。

## Migration Plan

按 5 步推进，每步以"该步结束时的树 + `make verify` 绿"为提交边界；`make smoke` 在涉及
组合/终端面的步骤后跑。

1. `pump_parts/turn.py` + `TurnOutcome`：`_consume_turn` 迁入并改返回类型（`_drive` 适配）。
2. `pump_parts/gates.py`：计划闸与澄清策略从 `_drive` 提出为具名步骤。
3. `pump_parts/deliver.py` + 两个委托壳（契约锁定）。
4. `bundle/journal.py` 接收 `tail_journal`，`pump` 重新导出。
5. 终端事件声明表（`domain/outcomes.py`）+ 四处消费者改读；组合表收敛到
   `domain/bundle.py` + 三处派生；`required-paths.toml` 登记；全门禁 +
   `git diff --stat -- tests/` 为空 + `make smoke`。

**回滚**：本 change 不产生运行时状态、不迁移数据；回滚 = 撤销该步 diff（新文件删除、
登记条目随同撤销）。
