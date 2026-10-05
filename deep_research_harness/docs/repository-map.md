# Repo 地图：从哪里读、对象放哪里

先读 [应用 README 控制地图](../README.md)；Coding Agent 先读 [应用指南](../AGENTS.md)。本地图扩展对象归属，运行事实由代码/配置/测试拥有，精确结构登记由 manifest 拥有。无需先读归档计划或浏览整个 DeerFlow 源码。

## 四种工作面

```text
repo/
|-- deep_research_harness/
|   |-- cli.py                      稳定启动入口，转交交互实现
|   |-- config/                     模型、工具和框架配置
|   |-- src/deerflow_deep_research/
|   |   |-- domain/                 类型、纯规则、路径合同
|   |   |-- engine/                 确定性 validator 与 gate
|   |   |-- agents/                 当前仅包入口
|   |   `-- runtime/                运行、可信 I/O、装配、落盘
|   |       |-- entry.py            checkout 定位、Bundle 查找、前台装配
|   |       |-- interaction/        CLI 参数、观察/输出、共享渲染
|   |       |-- contracts/          消费的框架接口镜像
|   |       `-- fixtures/           配置可加载的模型/工具 provider 代码
|   |-- tests/
|   |   |-- unit/                   离线规则、本地落盘、适配与入口测试
|   |   |-- contract/               离线镜像/配置/转发，进入默认 verify
|   |   |-- integration/            真框架/CLI 子进程，smoke 独立发现
|   |   `-- fixtures/               golden 和 replay 输入数据
|   |-- tools/                      显式录制等开发操作，不是测试
|   |-- scopes/                     本地 Run Bundle，gitignored
|   |-- docs/                       按问题查阅的说明/地图
|   |   `-- skills/deep-research/    研究 SOP 原文快照与本地阅读入口
|   |-- playbook/                   操作步骤与完成判据
|   `-- proof-lanes.toml            回执车道声明，不是测试 runner
|-- deerflow/                       锁定上游运行时，只读
|-- OpenSpec 开发工作区             规范、变更准入与治理 checker
`-- _backlog/                       活跃计划、缺陷与历史分析
```

运行态是源码、配置及本地 Bundle；交互态在 runtime/interaction；验证态是 tests + 被消费样本，显式操作在 tools；设计规范与任务治理位于应用外。interaction 是 runtime 内的职责子目录，不是新增所有权层。

`deerflow/scripts/` 属于上游框架；其目录名不决定本应用的入口或工具位置。普通应用工作使用公开接口，不修改或深入浏览框架内部；研究能力入口见 [研究过程地图](research-process.md)。运行数据、凭证和缓存不会随 Git 自动带到新机器。

## 改什么，就找哪个 owner

| 对象 / 你要改变什么 | 直接入口 | 最小证据 |
| --- | --- | --- |
| Bundle 状态、generation、终态 | [state_machine](../src/deerflow_deep_research/domain/state_machine.py) | [Bundle 规则](../tests/unit/test_bundle_domain.py) |
| 澄清上限、journal 词汇、artifact 合同 | [clarification](../src/deerflow_deep_research/domain/clarification.py)、[journal_policy](../src/deerflow_deep_research/domain/journal_policy.py)、[admission](../src/deerflow_deep_research/domain/admission.py) | 同上及 [准入规则](../tests/unit/test_admission_engine.py) |
| 创建、取消、refine、owner 存活 | [bundle_actions](../src/deerflow_deep_research/runtime/bundle_actions.py) | [Bundle 落盘](../tests/unit/test_bundle_runtime.py) |
| state 读取/revision/目录 identity | [bundle_state](../src/deerflow_deep_research/runtime/bundle_state.py) | [读失败诊断](../tests/unit/test_state_read_diagnosis.py) |
| 产物是否合法、阶段 admit 数量 | [validator](../src/deerflow_deep_research/engine/validator.py)、[gate](../src/deerflow_deep_research/engine/gate.py)、[verdicts](../src/deerflow_deep_research/engine/verdicts.py) | [纯裁决](../tests/unit/test_admission_engine.py)；gate 不等于已接入四阶段图 |
| 准入落盘、账本、原子写入 | [admission](../src/deerflow_deep_research/runtime/admission.py)、[ledger](../src/deerflow_deep_research/runtime/ledger.py)、[atomic](../src/deerflow_deep_research/runtime/atomic.py) | [准入落盘](../tests/unit/test_admission_runtime.py) |
| stream/续答/错误/最终回答投影 | [run_engine](../src/deerflow_deep_research/runtime/run_engine.py)、[journal](../src/deerflow_deep_research/runtime/journal.py) | [运行泵](../tests/unit/test_run_engine.py)、[事件形状回放](../tests/unit/test_event_stream_replay.py) |
| checkout 定位与前台装配 | [entry](../src/deerflow_deep_research/runtime/entry.py) | [entry composition](../tests/unit/test_entry_composition.py) |
| CLI 解析、文案、直播/观察 | [interaction CLI](../src/deerflow_deep_research/runtime/interaction/cli.py)、[render](../src/deerflow_deep_research/runtime/interaction/render.py) | [渲染](../tests/unit/test_entry_surface.py)、[CLI 旅程](../tests/integration/test_cli_journey.py) |
| client 装配/checkpoint/递归上限 | [client](../src/deerflow_deep_research/runtime/client.py)、[接口镜像](../src/deerflow_deep_research/runtime/contracts/client_surface.py) | [离线合同](../tests/contract/test_wiring_mirror.py)、[真框架 smoke](../tests/integration/test_wiring_smoke.py) |
| prompt/tool 装配观测、自定义委派声明 | [snapshot](../src/deerflow_deep_research/runtime/snapshot_middleware.py)、[posture](../src/deerflow_deep_research/runtime/subagent_posture.py) | smoke 及 [posture 守卫](../tests/unit/test_subagent_posture.py) |
| 搜索、模型、摘要策略 | [base](../config/base.yaml)、[fixture](../config/fixture.yaml) | 配置/fixture smoke；真实研究质量另评审 |
| future harness model role | [agents 包](../src/deerflow_deep_research/agents/__init__.py)、[研究地图](research-process.md) | 先定义角色合同；空包不代表实现 |
| 质量机器登记、命令导航 | [machines](../src/deerflow_deep_research/engine/machines.py)、[quality register](quality-register.md)、[COMMANDS](../COMMANDS.md) | [admission engine](../tests/unit/test_admission_engine.py)、[命令面](../tests/unit/test_command_surface.py) |
| 事件录制、样本来源/消费者 | [tools](../tools/README.md)、[fixtures](../tests/fixtures/README.md) | 显式 fixture 临时录制、对应 replay 测试 |

## 按问题继续读

- 看一次 run 保存什么、终态/发布有什么限制 → [运行态总图](runtime-map.md)。
- 找 skill、lead agent、工具和实际研究证据 → [研究过程](research-process.md)。
- 选择测试文件、真实部分/替身、样本与红绿命令 → [测试地图](../tests/README.md)。
- 执行用户动词 → [命令菜单](../COMMANDS.md) 与 [playbook](../playbook/run-research.md)。

AGENTS 是开发约束，playbook 是操作者步骤，tests 是验证资产，OpenSpec/backlog 是开发治理；它们不作为运行中的研究 prompt 或节点自动执行。

## 同轮维护

新增/搬迁/删除对象时更新 owning code/test、这里的路由及结构 inventory。新增 docs 登记文档 scope，AGENTS 保持短触发路由。地图不能补出未接线能力，也不复制 state/checkpoint/ledger 成第二事实源。
