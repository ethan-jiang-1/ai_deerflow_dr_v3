# 测试资产地图

> 新增/修复行为：先定位下面的 owner 与接口，再选最小测试；不要默认从真实端到端开始。
> 本文登记现有资产与局限，不是覆盖率承诺。车道策略见 [testing-and-evaluation](../docs/testing-and-evaluation.md)，
> 研究主干见 [research-process](../docs/research-process.md)。

## 目录如何组织

```text
tests/
|-- README.md           本地图：选哪里测、样本是什么、怎样执行
|-- __init__.py         unittest 递归发现的包标记
|-- unit/
|   |-- __init__.py     离线默认门禁的包标记
|   |-- test_collection_guard.py   收集守卫：owner 标记齐全、integration 默认隔离
|   |-- domain/         Bundle/status/clarification/journal 纯规则
|   |-- engine/         validator/gate/machines 纯裁决
|   |-- runtime/        Bundle 落盘、状态读取、准入落盘、运行泵、回放、posture
|   `-- interaction/    渲染、命令面、playbook、entry 组合
|-- integration/        无包标记；smoke 独立发现
|   `-- test_*.py       框架依赖测试、真实 CLI 子进程、回放机制测试
|-- contract/           有包标记；离线接口镜像/配置/转发/链条组合测试进入 verify
`-- fixtures/
    |-- recorded/       journal 渲染 golden 样本
    `-- replay/         事件流 / 模型输出记录
```

**目录即 owner**：unit 下四个子包按被测 owner 分组，选择最小 seam 先看目录名；
`test_collection_guard.py` 守护收集合同（owner 标记、integration 隔离、默认
发现范围），新增/删除包标记都会变红。

**目录与测试职责不是同一个维度。** unit 内含真实文件系统和有限并发测试；integration 内的模型回放测试并非完整端到端。
Bundle 规则合同在 [test_bundle_domain](domain/test_bundle_domain.py)，离线接口镜像在 [test_wiring_mirror](contract/test_wiring_mirror.py)，真实 client 构造参数名对比在 [test_wiring_smoke](integration/test_wiring_smoke.py)。
目录按依赖和责任选择；需要真实框架的合同仍在 integration。录制操作已移到 [tools](../tools/README.md)，输入数据见 [fixtures](fixtures/README.md)。

[Makefile](../Makefile) 决定实际收集方式：

- `make verify` / `make test`：stdlib unittest 从 tests 发现；integration 没有包标记，因此不递归进去。
- `make smoke`：uv sync 后单独从 tests/integration 发现；使用框架环境，不需要真实 API key。
- 不要顺手给 integration 增加 `__init__.py`，否则会改变默认离线门禁。
- fixtures 是输入数据，不会自行执行；`.gitkeep` 和 `__pycache__` 不算测试。
- [proof-lanes.toml](../proof-lanes.toml) 是选中变更的回执车道声明，不负责收集测试；当前没有 `make proof` target。

## 改了什么，就先测什么

下面列出所有现存 test 文件。先运行一个文件定位红绿，再按风险扩大到 lane。

| 要证明的行为 / 接口 | 测试资产 | 使用的真实部分与替身 |
| --- | --- | --- |
| Bundle 路径、状态转移、澄清、journal 纯规则 | [test_bundle_domain.py](domain/test_bundle_domain.py) | 真实 domain；手工状态/调用观察，无 I/O |
| 创建、碰撞、cancel/refine、CAS、lease、journal 落盘 | [test_bundle_runtime.py](runtime/test_bundle_runtime.py) | 临时目录/真实存储；固定时刻/pin、注入 liveness；含短命进程 |
| 状态文件缺失/目录缺失分类、有限并发 rewrite | [test_state_read_diagnosis.py](runtime/test_state_read_diagnosis.py) | 临时目录/线程；patch 制造读取竞态，不证明所有跨进程/文件系统情况 |
| validator 结果、gate 数量推导、quality register 登记 | [test_admission_engine.py](engine/test_admission_engine.py) | 真实纯裁决；人工 submission/context 与文档 |
| reject 不落内容、admit/replay、账本篡改、报告路径 | [test_admission_runtime.py](runtime/test_admission_runtime.py) | 真实 validator/临时落盘/hash 链；人工产物 |
| run_research 的续答、终态、fallback、取消与最终报告 | [test_run_engine.py](runtime/test_run_engine.py) | 真实 Bundle/journal/admission；手写 stream_fn 事件，非真实 agent loop |
| 前台装配、create 顺序/缺依赖 remedy、Bundle 查找、pin 失败、无框架 help/观察错误 | [test_entry_composition.py](interaction/test_entry_composition.py) | 真入口/临时落盘/依赖阻断子进程与负例；client/saver/run_engine 协议替身，不执行模型 |
| 文案、直播事件 callback、journal tail、golden 渲染 | [test_entry_surface.py](interaction/test_entry_surface.py) | 真实 render/pump/临时文件；人工事件与 golden 样本，不执行 CLI |
| 真实 flat 事件形状进入 pump、工具名进入 journal | [test_event_stream_replay.py](runtime/test_event_stream_replay.py) | 固定记录流 + 真实 pump/落盘；不重跑模型、搜索和框架图 |
| 配置解析、本地 client mirror、thread/递归上限转发 | [test_wiring_mirror.py](contract/test_wiring_mirror.py) | 本地代码/配置；FakeClient 记录调用，不 import 真 client |
| 入口链六环的组合关系被替换、绕过或改名漏切 | [test_entry_chain.py](contract/test_entry_chain.py) | stdlib AST 源码断言，零产品 import、不锁行号；阶段内重构不误伤，不证明运行时行为 |
| 终态分类七类互斥、ambiguous 兜底、碰撞负例 | [test_diagnosis.py](unit/domain/test_diagnosis.py) | 真实纯分类器；手工 state/journal/presence 输入，无 I/O |
| diagnose 渲染短语 + 只读边界（哈希对照）+ active 不分类 | [test_entry_surface.py](unit/interaction/test_entry_surface.py)（DiagnoseSurfaceTest） | 真 Bundle/临时目录；不执行模型 |
| 框架 home pin：env 指向仓库根、子树外、pin 先于 build_client | [test_framework_home.py](contract/test_framework_home.py) | 真 pin 函数 + AST 调用顺序；不 import 框架 |
| subagent 配置 posture 与违规声明 | [test_subagent_posture.py](runtime/test_subagent_posture.py) | stdlib checker + 真实/临时配置，不执行委派 |
| COMMANDS、Makefile、CLI 动词清单一致 | [test_command_surface.py](interaction/test_command_surface.py) | 文本/正则检查，不执行命令 |
| 命令菜单路由与 playbook 完成判据登记 | [test_agent_playbook.py](interaction/test_agent_playbook.py) | 文档检查，不证明旅程真的成功 |
| 反问交互门控（TTY/env）、提示渲染、create/refine 接线 | [test_clarification_prompt.py](interaction/test_clarification_prompt.py) | patch stdin/env 的接线检查；handler 行为用假 input，不执行模型 |
| 计划闸门门控、三路 handler（确认/修订/跳过/放弃）、create-only 接线 | [test_plan_prompt.py](interaction/test_plan_prompt.py) | patch stdin/env 与假 input；不执行模型 |
| **smoke**：多轮澄清、真实 fallback、SQLite、snapshot、构造接口合同 | [test_wiring_smoke.py](integration/test_wiring_smoke.py) | 真 DeerFlowClient/图/middleware/saver；脚本模型与 fake search |
| **smoke**：create（含搜索物化）/watch/status（含 delivery 行）/refine（跑完并 admit gen2 报告）/inspect/cancel（终态负例）/diagnose（raise 模型 → model_call_failed 分类）、非法输入 | [test_cli_journey.py](integration/test_cli_journey.py) | 真 CLI 子进程/框架/落盘；检查非空报告及 ledger admit；fixture 模型，写仓库根 runs |
| **smoke**：replay_key、录制后回放、miss 诊断 | [test_replay_model.py](integration/test_replay_model.py) | langchain 消息/JSONL/替身实现；临时脚本录制，不消费真实模型样本、不跑图 |
| **smoke**：交互反问旅程（作答继续不耗预算 / 拒答回落自动应答） | [test_clarification_journey.py](integration/test_clarification_journey.py) | 真 CLI 子进程 + DEEP_RESEARCH_INTERACTIVE=1 + 管道 stdin；脚本模型伪造反问，零凭证 |
| **smoke**：计划闸门旅程（标记计划确认注入+物化 / 修订附加 / 无标记报告降级回归） | [test_plan_journey.py](integration/test_plan_journey.py) | 真 CLI 子进程 + 管道 stdin；脚本模型覆盖标记计划与 58b5440e 回归形状，零凭证 |

CLI 旅程的 refine 断言第二代跑完且报告 admit；cancel 在旅程中是终态负例（正向接线在 unit 的 refine_foreground 文件）；仍不证明运行中中断。
真实构造合同目前对比参数**名称**；离线 contract mirror 断言不能替代真实接口对比，也不证明所有 defaults/类型/事件 schema。

## 样本数据与可配置替身分开放

| 资产 | 谁消费 / 证明什么 | 限制 |
| --- | --- | --- |
| [clarification-exhaustion.json](fixtures/recorded/clarification-exhaustion.json) | entry_surface 渲染 golden；样本自述来自脚本 run | 不执行澄清耗尽场景，也不代表真实模型行为 |
| [real-small-stream.json](fixtures/replay/real-small-stream.json) | event_stream_replay 消费；锁定记录事件形状 | 有外部内容/工具回复；不是事实正确性的标准答案，录制元信息不完整 |
| [real-model-io.jsonl](fixtures/replay/real-model-io.jsonl) | 留存模型输出样本；首个测试消费者在 [test_replay_model.py](integration/test_replay_model.py)（形状契约 + 回放机制参与） | 单条 key/output，缺原始输入/model/pin/录制命令；不能独立复核真实来源——消费点声明，只断言可断言面 |
| [real-research-journal.jsonl](fixtures/replay/real-research-journal.jsonl) | [test_behavior_profile.py](unit/engine/test_behavior_profile.py) 消费；行为画像钉样（工具选择/事件构成/时长） | 逐字提取自真实 run `5bb2c343`（2026-10-05）journal；画像钉样不证明研究质量为真 |
| [runtime/scripted](../src/deerflow_deep_research/runtime/scripted/__init__.py) | fixture 配置动态加载的 ScriptedChatModel / FakeWebSearchTool | 代码 provider，不是样本文件；最后脚本项会重复，循环上限由调用方负责 |
| [replay_model.py](../src/deerflow_deep_research/runtime/scripted/replay_model.py) | RecordingChatModel / ReplayChatModel 的内容寻址机制 | key 忽略 system 消息，输出只保存 content，不保留完整 tool_calls/usage 协议 |
| [record_stream.py](../tools/record_stream.py) | 显式记录 client.stream；不在自动收集中 | 外部调用/数据写入工具，不是安全脱敏器 |

录制真实事件时必须明确选择 `CONFIG=base`；[Makefile](../Makefile) 的 CONFIG 默认 fixture，不能仅凭 target 名认定调用了真实 API。
`make record-stream PROBLEM="..." CONFIG=base` 会调用外部 API，且**直接覆盖** [real-small-stream.json](fixtures/replay/real-small-stream.json)，另创建本地 Bundle。先读录制工具并确认覆盖意图；不要把未审查的录制当“更新快照”。
重新提交记录前检查问题、工具结果、消息、UUID、用户内容和敏感数据；去掉 volatile 字段不是秘密脱敏。
记录来源、命令、配置/pin/revision 和消费场景；历史样本缺元信息应诚实声明，不补造 provenance。
只留最小复现输入；错误日志中的 input preview 也可能包含用户内容。

## 新资产放哪里

| 新资产的责任 | 放置规则 |
| --- | --- |
| stdlib 纯规则、本地可信落盘、注入 stream 的确定性行为 | 优先扩展已有 unit owner 目录中的文件；新 owner 才建 `unit/<owner>/` 子包（需配 `__init__.py`，collection guard 会检查） |
| 需要 DeerFlow/langchain 环境、真实图/checkpointer 或 CLI 子进程 | 扩展对应 integration 文件；新文件仍由 smoke 单独发现 |
| 离线接口镜像/配置/转发合同 | 放 contract 并进入 verify；需要真实框架的比较仍放 integration |
| 显式录制/诊断操作 | 放 [tools](../tools/README.md)，不与自动测试混放 |
| 最小输入/记录样本 | 按消费方式放 fixtures/recorded 或 fixtures/replay；登记消费者与来源，不把样本当测试 |
| YAML 可加载的模型/工具替身 | 放 runtime/scripted；样本和配置加载代码分开，保持框架公开接口 |
| 结构/spec/发现规则 checker 的测试 | 留在其治理 owner；不让应用默认门禁依赖治理工作区 |

## 补测试的最短路径

本节应用现有红绿纪律，不授权新的产品接口或行为。

1. 找到 changed decision 的 owner：纯规则、可信落盘、stream 适配、真实绑定，还是 CLI 旅程。
2. 在 owning change 里写清**被测接口、预期可观察结果、不证明什么**；新增接口须先确认，不靠文件名猜。
3. 先在上表最近的资产里增加一个最小反例，运行一个测试并确认是预期原因变红。
4. 只实现使该例变绿的改动，再加下一个行为切片；不要一次写完所有猜想测试。
5. 跑该 owner 的测试文件，再跑 `make verify`；触及框架绑定或 CLI 时加 `make smoke`。
6. 只有问题明确依赖模型行为/外部工具，才选真实梯；记录配置、费用/时长与局限。新守卫做负例控制，回执新于最后改动。

执行位置是应用目录：

```bash
# 单个离线文件
PYTHONPATH=src python3 -m unittest tests.unit.runtime.test_run_engine -v
# 单个合同文件
PYTHONPATH=src python3 -m unittest tests.contract.test_wiring_mirror -v
# 单个测试（下面是现存例子）
PYTHONPATH=src python3 -m unittest tests.unit.domain.test_bundle_domain.BundleContractTest -v
# 单个集成文件：不要 import integration 当包
UV_CACHE_DIR="$PWD/../.uv-cache" uv run --no-sync python -m unittest discover -s tests/integration -p 'test_wiring_smoke.py' -v
# 最后扩大验证
make verify
make smoke
```

首次集成执行先 `uv sync`。只看返回 0 不够：检查测试真的被发现、是否 skip；缺框架的跳过不能算已验证绑定。
CLI smoke 会留下 gitignored Run Bundle，运行前知晓此副作用；不要清理用户旧数据。

## 目前没有证明的事情

- 真实模型的研究充分性、引文真实性、工具选择、token/延迟质量没有自动化统计验收。
- 真实模型 JSONL 尚未接入完整图回放；事件流回放也不证明新模型能再生成同样的过程。
- CLI journey 不覆盖 active watch 持续观察、in-flight cancel；refine 再执行至完成已覆盖。这些若成为需求，先明确合同。
- CAS/lease 与 rewrite 测试是本地有限实验，不是多用户 worker / 跨机器恢复证明。
- 治理 checker 的测试另在仓库治理面；应用 verify 不 import 它们。发布冷启动仍是一条独立证据，不由测试目录名自动提供。

不以文件数、测试数或目录完备度代替这些行为证据。新增/搬迁/删除资产时同步本表和实际 lane，别悄悄扩大默认门禁。
