# Proposal: Refine Foreground Rerun

## Why

Phase 5 第 2 轮裁决（2026-10-05）：refine 今天只把终态 Bundle 转成 active 的下一代，
然后什么都不能执行它——`run_foreground` 只被 `cmd_create` 调用。后果是一个真实的
谎言链：refine 打印 "generation N started"，但下一代是**无主僵尸**（继承了已死的
旧 owner_pid），下一次 `status` 会把它转成 failed-resume 并在 journal 写一条
**假的 "crash_detected"**（没有任何东西跑过然后崩）。CLI 旅程测试只断言
"generation 2 active"（没接 status），所以红灯一直没亮。

## What Changes

- **`refine` 立即前台重跑**：`cmd_refine` 在 `bundle_actions.refine` 之后走
  `create` 已验证的执行链（`entry.run_foreground`），跑完该代、落到类型化终态、
  打印终态行——与 create 完全同一管道（live 渲染、 ImportError remedy 文案、
  终态输出格式）。
- **消息按代选择**（`run_engine.run_research`）：首条消息 gen 1 读
  `request/problem.txt`，gen N>1 读 `request/refine-N.txt`——重跑发送的是
  **refine 方向文档**，不是把原始问题再发一遍。
- **owner 语义修正**（`bundle_actions.refine`）：下一代 state 的 owner_pid 设为
  调用进程（与 `start` 的 action 层模式一致）——重跑期间 status 不再把活着的
  run 误判为死 owner 伪 crash。
- **梯延续**（`entry.config_name_for_composition`）：refine 不新加 `--config`
  参数，**延续 bundle 自己声明的 composition 梯**（fixture→fixture，
  all_real→base；`mixed`/未知 → 响亮失败点名）——refine 真实梯的研究不会
  意外掉到 fixture。
- **spec delta**：entry-surface "Six verbs" requirement MODIFIED——refine 子句
  从"require non-empty direction text and enter the next generation"扩为
  "...and then drive the run engine in the foreground over that generation's
  direction document, ending at a typed terminal state"；补一个 refine 执行场景。
  run-bundle spec 的状态机语义（terminal→active→terminal 转移本身）**不变**。
- **文档同轮**：COMMANDS（refine 行）、control-map（动词表 + 从未实现清单移除
  "refine 自动重跑"）、run-bundle.md 生命周期、playbook 两处、tests/README 两处
  （旅程断言描述 + "未覆盖"清单）。
- **不变**：六动词集合、状态机规则、准入语义、cancel 机制、fresh_context
  API 变体（其 seed document 的运行侧消费仍是 slim-restart 留下的未接线状态，
  不在本 change 偷做）。

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `entry-surface`: the six-verbs requirement's refine clause gains foreground
  execution semantics (drive the run engine over the generation's direction
  document, continuing the bundle's composition ladder); one new scenario.

## Impact

- 代码：`run_engine.py`（消息选择）、`bundle/bundle_actions.py`（owner_pid）、
  `entry.py`（composition→config 映射）、`interaction/cli.py`（cmd_refine 执行
  接线 + remedy 文案）。
- 测试：新增 unit 红（run_engine 消息选择、映射函数、owner_pid、cmd 接线——
  新文件 `tests/unit/interaction/test_refine_foreground.py`）；扩展
  `test_run_engine.py`、`test_bundle_runtime.py`；旅程测试 refine 段改为断言
  完成与 gen2 报告（refine 子进程注入不同 `DEERFLOW_FAKE_SCRIPT` 避免
  重复 hash 拒收）；`_cli` 增加环境注入参数。
- 触发双 lane：verify（src/tests 变更）+ smoke（cli.py/interaction/journey 变更）。
- 不触碰：domain 状态机规则、engine、admission 语义、config 文件、`deerflow/`。

## Change Focus

- **Primary module / causal owner:** `runtime/interaction/cli.py::cmd_refine` 的执行接线——refine 的可观察行为归交互层委托；消息选择与 owner 语义是其下游 owning seam 的配套修正。
- **Seam classification:** wiring — 把已验证的 create 执行链接到 refine 路径；无新认知面、无新状态规则、无准入变化（框架错误→failed-resume 等既有语义自动延伸覆盖）。
- **Question:** refine 打印的 "generation N started" 能否变成全真——创建下一代并当场跑完、消息是该代方向文档、owner 是活进程、报告经既有准入落盘——且六动词集合与状态机规则零变化？
- **Necessary adjacent/external contracts:** entry-surface（answers: 六动词 requirement 的 refine 子句 MODIFIED；EV2 旅程证据义务随断言扩展）；run-bundle（answers: 状态机转移语义不变，owner_pid 归 action 层与 start 模式一致）；deerflow-wiring（answers: 执行链复用 run_foreground，composition 梯延续映射 fixture/all_real；mixed 响亮失败）；delivery-lanes（answers: 双 lane 欠账——verify+smoke）。
- **Evidence seam:** unit 红×4（消息选择/映射/owner/接线）+ 旅程红（现状 refine 后 active，新断言 completed 失败）先行入回执；实现后 verify 全绿 + smoke 旅程绿（含 gen2 报告 admit）；治理全套。
- **Not in scope:** fresh_context seed document 的运行侧消费；refine 的 `--config` 覆盖参数（梯延续即合同）；worker/后台执行（第 5 轮已裁维持前台）；`mixed` 梯接线。
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

认知不因果：本 change 不新增任何模型可见面；执行链、消息文档与 owner 语义全部是确定性接线。

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| refine 的下一代执行方式（不跑 → 前台跑完） | Human judgment（Phase 5 第 2 轮裁决 B；拒绝僵尸+伪 crash） | cmd_refine → run_foreground 接线；终态仍由 run_engine/domain 规则裁决 | non-bypassable | 框架错误→failed-resume、cancel 协作终止等既有语义自动延伸；恢复 = revert | "started" 谎言与 status 伪 crash 记录被消除，无新状态规则 | 旅程红→绿（completed + report-gen2 admit）；unit 接线红→绿 |
| 重跑发送的消息（problem → 该代方向文档） | 无认知候选（机械文档选择） | run_engine 按 state.generation 选 request 文档；缺文件响亮失败 | non-bypassable | 不静默回退 problem.txt——回退即谎言 | 任何未来调用方自动获得正确消息，无需各自拼装 | run_engine 消息选择测试红→绿 |
| 下一代 owner（死 pid 继承 → 调用进程） | 无认知候选 | bundle_actions.refine 设 owner_pid=os.getpid()（与 start 同模式） | bounded-repair | 重跑期间 status 探活所见即真 | 伪 crash_detected journal 条目不再产生 | owner 断言红→绿 |
| 执行梯选择（新增 --config → 延续 composition） | Human judgment（延续比显式重选更安全：真实梯 refine 不会意外掉到 fixture） | entry.config_name_for_composition 纯映射；mixed/未知响亮失败 | non-bypassable | 梯不匹配的 bundle 无法静默换梯 | 少一个 CLI 参数面；两梯语义与 bundle 声明一致 | 映射表驱动测试红→绿 |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| 重跑中框架错误（ImportError / stream 异常） | run_engine 既有兜底 | 同 create：ImportError → remedy 文案退出；异常 → failed-resume + journal framework_error | failed-resume（类型化，非伪 crash） | uv sync 后再 refine，或 inspect 查 journal | 旅程/单测既有 framework_error 路径；remedy 文案断言 |
| gen>1 但 refine-N.txt 缺失 | run_engine 文档选择 | 不恢复——读取即 FileNotFoundError 响亮失败（带路径） | 无终态写入（尚未进入 drive） | 修复 bundle 目录或重新 refine | 单测缺文件负例 |
| gen2 回答与 gen1 完全相同 | admission validator（重复 hash） | 不恢复——拒绝是正确裁决 | completed + 未交付（正交事实） | 换方向 refine；重复本身即信号 | validator 既有重复负例；旅程用不同回答覆盖健康路径 |
| refine 期间用户 cancel | run_engine 检查点观察（既有） | 既有 cancel 语义自动延伸 | cancelled | inspect 查原因后重新 refine | 既有 cancel 测试路径 |
