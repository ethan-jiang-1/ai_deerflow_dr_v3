# Plan: Runtime / Test / Interaction / Agent Loop 结构与控制面重整

> 类型: 架构设计 / 可驾驭性整理 | 更新: 2026-10-05
> 状态: Phase 0–4 归档（五个 change）；Phase 5 八项已全部裁决（2026-10-05 七轮，见该节逐项记录）——两项待立 change（state 记录交付、evidence 物化）；refine 前台重跑已落地，其余维持现状已记录
> 目标: 让产品驱动者和新 Coding Agent 不必先做代码考古，就能定位运行入口、研究 loop、skill、Run Bundle、测试资产和调试工具。

## 1. 背景

当前项目是运行在 DeerFlow 2.1.0 之上的 Deep Research 应用。仓库已经完成一轮初步整理：应用、上游框架、治理和 backlog 已经有明确边界，应用内也已经出现 `runtime/interaction/`、`runtime/entry.py`、`tests/contract/` 和 `tools/` 等命名空间。

这轮整理解决了部分物理混放问题，但还没有完全解决操作者提出的核心问题：

> 一个不了解项目历史的人，能否快速回答“从哪里启动、谁驱动 agent loop、skill 如何进入、状态存在哪里、如何观察一次 run、想改变某个行为应该先测哪里”？

目前这些答案分散在多个文档、多个 `runtime` 模块和上游框架之间。文档已经能画出一条链，但代码结构、测试结构和运行证据还没有全部沿同一条主干组织起来。

本计划不是把 DeerFlow 内部复制到本项目，也不是把所有东西重命名成更多目录。它要建立一条稳定的控制面：

```text
操作者 / Coding Agent
        |
        v
应用入口与交互
  cli.py -> runtime/interaction
        |
        v
一次运行的装配
  runtime/entry.py
  config/ + client binding + checkpointer
        |
        v
宿主研究循环
  DeerFlow lead agent
  model <-> tools <-> optional subagents
        |
        v
Harness 运行控制循环
  runtime/run_engine.py
  stream -> journal -> state -> terminal/admission
        |
        v
Run Bundle
  state / checkpoint / journal / diagnostics / evidence / final
```

图中两种 loop 必须一直分开：

- **宿主 agent loop**：由 DeerFlow 驱动，负责动态决定查询、工具、skill 使用、委派和收束；本项目只通过公开 binding 接入。
- **Harness run loop**：由 `runtime/run_engine.py` 驱动，负责消费事件、有限自动续答、取消/错误/终态、journal 投影和最终报告准入。

## 2. 已确认的现状

### 2.1 应用代码层

当前应用源码的四个 canonical ownership layer 是：

```text
deep_research_harness/src/deerflow_deep_research/
├── domain/       类型、状态合同、Bundle 路径、纯规则
├── engine/       validator、admission gate、质量机器
├── agents/       当前为空，尚无 Harness 自有 bounded model role
└── runtime/      装配、框架 binding、执行、持久化、交互和诊断
```

这四层由 `project-structure` spec 和 architecture checker 约束，不能因为可读性整理而随意新增第五个 ownership layer。可在 `runtime/` 内使用职责子目录，但必须保留四层 import 方向。

目前 `runtime/` 同时包含：

- 交互：`runtime/interaction/cli.py`、`render.py`；
- 一次运行装配：`runtime/entry.py`；
- DeerFlow binding：`client.py`、`contracts/`；
- 运行控制：`run_engine.py`；
- Bundle 状态与生命周期：`bundle_state.py`、`bundle_actions.py`；
- journal、atomic write、ledger、admission；
- 诊断与配置 posture：`snapshot_middleware.py`、`subagent_posture.py`；
- fixture provider 和模型回放：`fixtures/`。

这不是随机混放，但 `runtime/` 对操作者而言仍是一个过大的“运行时黑箱”。尤其需要把“装配”“执行”“持久化”“宿主适配”“交互”从导航和物理目录上都区分出来。

### 2.2 用户交互入口

稳定入口是：

```text
python3 cli.py <verb>
  -> runtime/interaction/cli.py::main
  -> cmd_create / cmd_status / cmd_watch / cmd_cancel / cmd_refine / cmd_inspect
```

`cli.py` 应继续保持为 checkout 入口和极薄 launcher。命令解析、输出和 watch polling 属于 interaction；配置、Bundle lookup、pin 和前台装配属于 runtime entry；状态变更不能回流到 CLI。

六个命令的当前语义必须继续显式区分：

- `create`：创建 Bundle 并前台运行；
- `watch`：投影 journal，遇到 terminal 退出；
- `status`：读取 state、journal 摘要和 owner PID；
- `cancel`：记录取消请求，由运行控制协作终止；
- `refine`：创建下一代 active，当前不自动运行；
- `inspect`：查看 journal、已接纳产物和装配快照。

### 2.3 Agent loop 与 skill

当前真正的研究认知能力属于 DeerFlow：

```text
DeerFlowClient
  -> lead agent
  -> model calls
  -> tools
  -> optional task/subagent calls
  -> stream events
```

Harness 的 binding 在 `runtime/client.py`：

- 使用显式 config path；
- 注入 Bundle SQLite checkpointer；
- 注入 assembly snapshot middleware；
- 打开 thinking 和 native subagent；
- 关闭 plan mode；
- `available_skills=None`，即目前没有由 Harness 显式选择的 skill 清单；
- 通过 `make_stream_fn` 注入 thread id 和每次调用的 recursion limit。

`docs/skills/deep-research/` 是上游 SOP 的本地阅读快照，不是当前运行时自动加载的 Coding Agent skill，也不是修改后会自动生效的产品 prompt。运行中是否实际读取 deep-research skill，需要看 tool call、checkpoint 和 snapshot/journal 证据。

因此现状必须诚实表述为：

> Harness 接入了 DeerFlow 的通用研究能力，但没有把 deep-research skill 变成一个 Harness 自有、强制、可独立验收的运行时合同。

是否改变这一点属于产品/认知策略决策，不能在结构整理中暗中完成。

### 2.4 Run Bundle 与运行状态

每次研究的持久状态以 Bundle 为单位，路径合同由 `domain/bundle.py` 持有：

```text
scopes/d_YYYYMMDD/<bundle-id>/
├── state.json
├── checkpoint.sqlite
├── request/
│   ├── problem.txt
│   └── refine-<generation>.txt
├── work/
├── evidence/
├── final/
└── diagnostics/
    ├── journal.jsonl
    ├── assembly-snapshot.json
    └── unanswered-clarifications.json
```

`state.json` 是运行状态唯一权威；写入使用 revision CAS 和 directory lease。SQLite 保存框架 thread/checkpoint；journal 是事件投影；final 是通过 Harness admission 后的报告投影。删除 Bundle 是永久删除，Harness 没有集中式 registry 或恢复库。

这里存在一个必须持续强调的状态区别：

```text
agent stream 结束
  != Harness state = completed
  != final report 被 admission
  != 研究事实质量达标
```

当前 `run_engine` 会先写 terminal，再提交最终报告，因此“运行终态”和“交付产物”应在状态、命令输出和测试中分别表现。

### 2.5 测试资产

当前测试已经按主要 lane 分开：

```text
tests/
├── unit/          离线默认门禁；规则、本地存储、运行控制、交互投影
├── contract/      离线 framework surface/config/forwarding mirror，进入 verify
├── integration/   真 DeerFlow / CLI 子进程 / smoke，默认不进入 verify
└── fixtures/      recorded golden 与 replay 输入，不是测试 runner
```

开发工具已经移至 `tools/`，不应重新放回 tests。这个方向正确，但 unit 目录内部仍是扁平的大集合；新 Agent 需要读测试地图才能知道 `test_run_engine.py`、`test_entry_composition.py`、`test_bundle_runtime.py` 的边界。

### 2.6 本轮验证事实

探索时得到的最新事实：

- `deep_research_harness/make verify`：125 项测试通过；
- architecture checker：通过；
- doc hygiene：通过；
- dependency direction checker：失败，原因是 `deep_research_harness/docs/skills/deep-research/verification-receipt.json` 的历史命令文本包含 `openspec/`，被扫描器当成应用反向依赖；
- 本轮没有重新执行 `make smoke` 或真实 API run；
- 当前工作树本来就有一批未提交的整理变更，后续实施不得覆盖这些用户/前序 Agent 改动。

这个 dependency checker 失败必须作为独立的治理修复项处理，不能把它混进目录搬迁后才发现。

## 3. 目标状态

### 3.1 一个主控制地图

应用 README 继续是短入口，但需要明确只承担三件事：

1. 第一屏给出用户/Agent 的最短阅读顺序；
2. 给出完整执行 spine；
3. 把每个控制问题路由到唯一的下一份文档、代码 owner 和最小测试。

建议形成以下唯一阅读链：

```text
README.md
  -> docs/control-map.md       从输入到报告的主链、两种 loop、权威边界
  -> docs/run-bundle.md        state/checkpoint/journal/final 的持久化合同
  -> docs/research-process.md  skill、lead agent、tools、subagent 的实际证据
  -> tests/README.md            lane、样本、最小测试和不证明什么
  -> docs/local-operations.md  环境和命令坑
```

现有 `repository-map.md`、`runtime-map.md`、`runtime-architecture.md` 中重复的内容需要归并或降级为指针。不能让四份文档同时声称自己是“总图”。

`AGENTS.md` 保持短，不复制整张架构图；它只负责把不同任务路由到上述地图、owner 和命令。`COMMANDS.md` 保持命令语义唯一，不在 README、playbook、tools README 中复制另一套命令定义。

### 3.2 明确的 runtime 子目录

保留四层 ownership，不新增第五层；在 `runtime/` 内按运行职责形成可见子目录。目标形态可采用下列命名，最终名称在 OpenSpec design 中确认：

```text
runtime/
├── interaction/       用户命令、watch/status/inspect 投影、共享渲染
├── assembly/          或保留 entry.py：路径、pin、Bundle lookup、client/saver 装配
├── execution/         或保留 run_engine.py：stream 消费、续答、终态、取消/错误
├── bundle/            state、actions、journal、atomic、ledger、admission 的持久化组合
├── adapters/          DeerFlow client、contracts、snapshot、subagent posture
└── fixtures/          YAML 可加载的脚本模型、fake tool、回放 provider
```

这是一个目标职责图，不授权机械地把每个文件移动一次。迁移原则：

- 有真实的两个以上消费者或独立测试 seam 才引入新目录；
- 公开/配置消费的 import 路径需要制定 cutover；
- `domain/bundle.py` 仍是 Bundle 路径合同唯一权威；
- `engine/` 仍是确定性裁决 owner；
- 交互层不能直接写 state 或决定 admission；
- execution 层不能自己重新发明 domain terminal rules；
- adapters 层不能把 prompt 中的文字当成权限或状态 authority；
- fixtures provider 不与 `tests/fixtures` 样本混为一类。

如果实证表明新增物理目录带来的 import churn 大于可读性收益，则保留文件位置、通过 `README` 和模块命名实现最小可读结构；这个退让必须记录理由，不是默认放弃。

### 3.3 显性化 agent binding，而不是复制宿主实现

新增一份短的 binding/control reference（可作为 `docs/research-process.md` 的重写或单独 `docs/agent-binding.md`），固定回答：

| 问题 | 必须能直接找到 |
| --- | --- |
| 谁驱动研究 loop？ | DeerFlow lead agent；源码属于只读上游 |
| Harness 接在哪？ | `runtime` 的 client/adapter 与 `make_stream_fn` |
| 传入了什么？ | config path、model、checkpointer、thread id、middleware、recursion limit |
| skill 由谁选择？ | 当前由 DeerFlow 的 native surface 处理，Harness 未强制指定 deep-research |
| 子代理由谁决定？ | lead agent 按需使用 native task；Harness 当前只记录 posture 和事件 |
| 谁决定终态？ | Harness domain rules + `run_engine` |
| 如何证明实际发生？ | assembly snapshot、journal、checkpoint、final disposition |
| 如何替换/模拟？ | `stream_fn` seam、scripted model、fake search、event replay |

### 3.4 测试目录和验证菜单

测试结构要同时表达两个维度：**运行成本/依赖 lane** 和 **被测 owner**。目标组织建议：

```text
tests/
├── unit/
│   ├── domain/       Bundle/status/clarification/journal pure rules
│   ├── engine/       validator/gate/machines/admission decisions
│   ├── runtime/      Bundle persistence/run engine/stream replay
│   └── interaction/  renderer/command/playbook/entry composition
├── contract/         DeerFlow client surface/config/forwarding mirror
├── integration/      real framework, CLI subprocess, smoke-only replay
└── fixtures/
    ├── recorded/     golden rendering samples
    └── replay/       event/model input records
```

迁移前必须确认 unittest discovery 语义，保留 `integration/` 无 package marker 的隔离意图，比较迁移前后完整 test IDs，并设置一个能变红的 discovery negative control。

测试 README 应由“文件清单”升级为“验证菜单”：

```text
我要改变什么 -> 先测哪个 seam -> 命令 -> 证明什么 -> 不证明什么 -> 必要时扩大到哪个 lane
```

### 3.5 调试、录制、观测与测试资产完全分家

目标职责如下：

- 产品交互：`runtime/interaction/`；
- 运行诊断与持久证据：Run Bundle 的 `diagnostics/`；
- 显式开发操作：`tools/`；
- 自动断言：`tests/`；
- 测试输入数据：`tests/fixtures/`；
- 研究 SOP 参考快照：`docs/skills/`；
- 治理设计与准入：仓库根 `openspec/`；
- 上游运行框架：`deerflow/`，只读。

不能建立一个同时放启动、部署、录制、测试和诊断的通用 `scripts/` 目录。

## 4. 分阶段实施路线

### Phase 0：冻结现状与修复红灯

**目的**：在任何搬迁前，形成可比较的基线。

工作：

- 保存当前 git revision、工作树状态、架构 inventory 和现有 test IDs；
- 明确哪些改动属于前序整理，实施 change 不覆盖它们；
- 修复或调整 verification receipt / dependency checker 的误报，使“治理命令记录”不被当成应用 import；
- 重跑 `make verify`、architecture、doc hygiene 和 dependency direction；
- 记录 `make smoke` 是否执行、是否 skip、为何未执行。

完成判据：治理 closeout 中所有适用 checker 为 0；若 checker 设计本身需要改，先单独建立治理 change，不在运行目录迁移中夹带。

### Phase 1：建立唯一控制地图

**目的**：先让人和 Agent 能正确理解现状，再开始物理移动。

工作：

- 合并/重写重复的 runtime/repository/architecture 地图；
- 补齐两种 loop 的图示和职责表；
- 补齐 skill “声明可用”和“运行中实际加载”的差异；
- 补齐 Run Bundle 生命周期和 artifact ownership；
- 把每个操作者问题绑定到一个代码 owner、一个测试 seam 和一条命令；
- 对每条“当前未实现”明确写出它不是现状，尤其是 skill 强制、refine 自动重跑、多用户 worker 和真实研究质量评估。

完成判据：一个新 Agent 只读 README、控制地图和测试 README，能够找到 create、run loop、skill 证据、Bundle 状态和最小测试；链接检查通过；文档不引入第二套业务规则。

### Phase 2：runtime 子职责整理

**目的**：降低 `runtime/` 的认知宽度和文件查找成本。

工作：

- 以 import graph 和测试 seam 为证据决定哪些文件实际迁移；
- 优先整理 Bundle persistence、execution loop 和 DeerFlow adapters 三组；
- 保留 `entry.py` 或建立命名明确的 assembly seam；
- 更新所有 active imports、config provider path、path inventory 和 architecture guard；
- 对内部路径采用直接 cutover，不保留没有真实消费者的兼容 shim；
- 为每个迁移文件补模块 docstring，说明 interface、输入、输出和副作用，不把地图写成第二权威。

完成判据：源码目录能从名字直接区分 interaction、assembly、execution、persistence 和 adapters；四层 import governance 通过；原有 CLI 和 Bundle schema 不变；迁移前后测试 ID 只发生登记过的前缀变化。

### Phase 3：测试资产重排

**目的**：让“先测哪里”在目录层面可见，而不是必须查完整文件表。

工作：

- 将 unit 测试按 domain/engine/runtime/interaction owner 分组；
- 保持 contract 单独且继续进入 `make verify`；
- 保持 integration 不加入 package marker，继续由 `make smoke` 独立收集；
- 将 fixture 样本、fixture provider、recording tool 的三种角色分别登记；
- 更新 Makefile、COMMANDS、测试 README 和 proof lane selector；
- 加入 collection guard：unit/contract 必须被默认 gate 发现，integration 必须保持默认排除。

完成判据：每个现有测试文件在一个 owner 下有明确归属；`make verify` 和 `make smoke` 收集范围可通过命令输出证明；新 guard 能通过 planted failure 变红；测试文档不声称 fixture 证明真实研究质量。

### Phase 4：显性化 agent binding 与 Run Bundle

**目的**：让研究策略、宿主 loop、Harness 控制和运行证据不再混成“一个 agent”。

工作：

- 建立 binding map：host lead agent、model/tool/subagent、Harness adapter、run engine；
- 记录每个 binding knob 的 owner、实际默认值和测试证据；
- 对 skill 采用“声明 / 实际加载 / 质量评估”三列状态表；
- 为 Bundle 建立稳定的 artifact map，区分 request、state、checkpoint、journal、diagnostics、evidence、final；
- 为 `status` / `watch` / `inspect` 明确观察范围与不能推出的结论；
- 让 assembly snapshot、journal 和 final admission 的关联在一次 run 中可追踪。

完成判据：不读上游实现也能说明 binding；不读源码也能根据 Bundle 目录知道去哪里看证据；所有声明能力都有“如何验证实际发生”的入口。

### Phase 5：行为决策另行立项

以下事项不在结构整理中偷做，分别需要产品/规范决策和独立 OpenSpec change。
**2026-10-05 七轮裁决结果**（操作者逐项拍板）：

- deep-research skill 是否强制加载、版本如何锁定、怎样验收实际执行；
  **裁决：维持现状**（`available_skills=None`，可观察不保证；三列状态表 + 判断方法已交付）
- `refine` 是创建待运行 generation，还是立即前台重跑；
  **裁决：立即前台重跑**（复用 create 执行链；消除"下一代僵尸 + status 伪 crash 记录"——已落地 `refine-foreground-rerun`）
- active/watch/cancel 的跨进程 worker 语义；
  **裁决：维持前台模型**（单机前台 CLI；worker 仅在服务化立项时作为子任务）
- `completed` 与 final admission 是否合并或建立更强终态合同；
  **裁决：正交模型**（进程 status 与交付 disposition 分开记，交付事实进 state.json，终态规则不动——待立 change）
- evidence 是否由每次搜索自动物化；
  **裁决：完整物化到独立目录**（evidence/ 合同不动；引用复核从不可能变可直读——待立 change）
- 多用户服务、worker、认证、备份恢复和部署面；
  **裁决：维持源码两件套形态**（单机单操作者；服务化需要真实多用户驱动再按 Program 形式立项）
- 真实模型研究质量、引用真实性、充分性和统计评估；
  **裁决：未立项**（R4 物化是可人工复核的地基；自动化评估仍是更远的独立议题）
- Harness 是否新增自有 bounded agent role 并填充 `agents/`。
  **裁决：维持空层 deferred**（allowlist 记录在案；出现真实驱动按 LLM-Node 门立项，不违反 Expansion Gate）

## 5. 变更边界与不变量

必须保留：

- `deerflow/` gitlink 不修改、不作为普通排查对象；
- `python3 cli.py <verb>` 六个公开命令及其当前语义；
- `scopes/d_YYYYMMDD/<bundle-id>/` 的 persisted path 和 Bundle schema，除非另有 migration change；
- `state.json` 单一运行状态 authority、revision CAS 和 lease 检查；
- fixture zero-credential smoke 与 base 显式真实梯的区分；
- unit/contract 默认门禁和 integration smoke 分离；
- root `AGENTS.md`、应用 `AGENTS.md` 的短路由职责；
- OpenSpec 作为规范语义和架构变更的准入通道。

不应做：

- 为了显示 agent loop 而复制 DeerFlow lead agent 或 skill loader；
- 把本地 SOP 快照宣称为当前运行时 skill；
- 把所有测试都塞进 e2e；
- 把 debug recording 当自动测试或自动更新 fixture；
- 把 `scopes/` 运行数据提交进 Git；
- 把 README、地图、AGENTS、tests README 变成相互矛盾的多套 authority；
- 在同一 change 中顺手实现 refine、worker、真实质量 gate 等产品语义。

## 6. 风险与取舍

| 风险 | 缓解 |
| --- | --- |
| 物理搬迁破坏 unittest discovery | 迁移前后列出完整 test IDs；保留 integration 无 package marker；加入 discovery negative control |
| runtime 子目录变多反而增加认知负担 | 只有存在真实职责群和测试 seam 才拆；README 只保留一张控制地图 |
| 文档与代码再次漂移 | 代码/配置/测试保持权威；地图只做路由；链接、命令和结构 checker 进入收口门禁 |
| skill 快照被误认为运行配置 | 文档固定标注 runtime_active；要求 snapshot/checkpoint/tool evidence 才能声称实际加载 |
| `completed` 被误读为质量通过 | 命令和 Bundle map 分离 terminal、admission 和 quality；加针对性测试与示例 |
| 迁移触碰内部 import 消费者 | 先 grep active consumers；内部路径直接 cutover；配置 provider path 单独做兼容审查 |
| 治理 checker 扫描文档历史命令而误报 | 修复扫描边界或 receipt 表达方式；增加负例和正例，避免放宽真正的依赖检查 |
| 现有工作树改动被覆盖 | Phase 0 保存 membership；逐文件读现状；不使用 destructive git 命令；实施 change 继承前序改动 |
| 把“可观察”误当成“可证明” | 每个 lane 写 `covers` 与 `does not prove`；真实研究质量继续显式标记 UNVERIFIED |

## 7. OpenSpec 拆分建议

本 plan 不直接授权改代码。进入实施时建议拆成以下顺序，每次只放行一个 change：

1. **governance receipt / dependency-direction 修复**：先让当前 closeout 红灯有明确 owner 和负例。
2. **operator control map**：合并文档、补两种 loop、Bundle 和 skill evidence map。
3. **runtime responsibility reorganization**：只处理经过 import/test 证据确认的物理目录搬迁。
4. **test asset reorganization**：按 owner 重排 unit，保持 verify/smoke discovery 合同。
5. **agent binding / run evidence observability**：只增加可观察性和文档合同，不改变 skill 选择或产品质量语义。

每个 change 的 proposal 必须写清：

- primary causal owner；
- 是否涉及 persisted/public/cross-boundary surface；
- preserved contracts 和 cutover；
- red-green 测试 seam；
- 迁移失败时的恢复方式；
- 完成后哪个文档、checker、runner 和 receipt 证明它真的落地。

## 8. 验收清单

### 操作者验收

- [ ] 从应用 README 能在三跳内找到稳定启动命令。
- [ ] 能画出“交互 -> 装配 -> DeerFlow loop -> Harness loop -> Bundle”的主链。
- [ ] 能明确说出哪个 loop 属于 DeerFlow、哪个属于 Harness。
- [ ] 能知道 skill 是参考快照、可用表面还是实际加载证据。
- [ ] 能根据一个 Bundle 找到 state、checkpoint、journal、snapshot、evidence 和 final。
- [ ] 能用 `status`、`watch`、`inspect` 分别观察不同信息，而不把它们当质量证明。
- [ ] 能针对状态、binding、stream、admission、交互选择最小测试，而不是先跑真实 E2E。

### Coding Agent 验收

- [ ] 新 Agent 读取 `AGENTS.md` 和应用 README 后能进入唯一控制地图。
- [ ] 改纯规则、运行控制、binding、交互、测试资产时各有明确 owner 和最小命令。
- [ ] 目录名能表达 interaction、assembly、execution、persistence、adapter、fixture 的职责。
- [ ] 没有需要浏览整个 DeerFlow 源码才能理解 Harness 自己的 seam。
- [ ] 没有重复的命令词汇、Bundle path authority 或测试收集规则。

### 机器验收

- [ ] `make verify` exit 0，且 unit + contract 的收集范围有新鲜输出。
- [ ] `make smoke` exit 0；无测试被意外 skip；真实框架合同仍执行。
- [ ] architecture checker exit 0，四层 ownership 和 import direction 不漂移。
- [x] dependency direction checker exit 0，receipt/历史文本不产生误报。（2026-10-05 经 `exempt-receipts-from-dependency-guard` 落地：结构化回执豁免 + gitignore 锚定 + 回执跟踪登记）
- [ ] doc hygiene 和 link/command consistency checks exit 0。
- [ ] `git diff --check` exit 0。
- [ ] `git diff --exit-code HEAD -- deerflow` exit 0。
- [ ] 测试 discovery 的 planted negative control 能变红后恢复为绿。
- [ ] 新鲜 receipt 记录命令、退出码、revision 和已知 UNVERIFIED 空间。

## 9. 落地关联

本文件是 `_backlog` 的分析和决策记录，不是运行时规范，也不是直接实施授权。实际行为和结构变更应分别进入对应 OpenSpec change：

- `project-structure`：结构 inventory、目录种类、import layering 和 architecture guard；
- `entry-surface`：CLI 公共入口和六动词行为；
- `deerflow-wiring`：client、skill surface、checkpoint、事件形状和 binding contract；
- `run-bundle`：Bundle path、state、journal、checkpoint 和生命周期；
- `run-admission`：validator、gate、ledger、final report admission；
- `delivery-lanes`：verify、smoke、receipt 和测试证据；
- `doc-truthfulness`：文档与声明层的一致性。

首个实施前提是先由人确认：

1. 这次是否只做结构/可观察性，不改变 skill 选择和产品行为；
2. runtime 子目录是否接受物理迁移，还是先以控制地图和测试菜单收敛；
3. `completed`、final admission、研究质量三者是否继续保持独立；
4. 当前 dependency-direction 红灯由治理层如何修复。

结论：本项目不需要把所有功能变成端到端测试；需要把每一个重要控制点变成一个可定位、可调用、可观察、可验证的深模块 seam。目录重整服务于这个目标，而不是目标本身。
