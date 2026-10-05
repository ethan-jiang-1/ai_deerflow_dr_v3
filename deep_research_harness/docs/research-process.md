# Deep Research 研究过程：直接看这些对象

> 这里暴露的是本项目正在借用的研究过程，不是另造一条静态图。
> 方法论、装配代码、运行证据是三个不同对象：skill 要求什么，不等于模型每次都遵守。

## 最短阅读路径

| 你的问题 | 点这里 | 它是什么 |
| --- | --- | --- |
| 研究方法到底写在哪？ | [本地 SOP 阅读入口](skills/deep-research/README.md)、[完整 SKILL.md](skills/deep-research/SKILL.md) | Harness 中的原文快照，含来源 pin/hash；运行时仍由框架加载，不是本仓 coding-agent skill |
| 谁让 lead agent 跑起来？ | [本应用 client binding](../src/deerflow_deep_research/runtime/adapters/client.py#L68) | 构造嵌入式 DeerFlowClient，注入 checkpointer 与 snapshot middleware |
| 哪些认知能力打开了？ | [binding defaults](../src/deerflow_deep_research/runtime/adapters/contracts/client_surface.py#L32) | thinking/subagent 开启、plan mode 关闭、available_skills=None；并非强制每次调用 deep-research |
| 使用什么模型和 Web 工具？ | [base.yaml](../config/base.yaml)、[fixture.yaml](../config/fixture.yaml) | 真实梯与脚本梯的具体 provider/tool 声明 |
| 如何委派子代理？ | [框架说明](../../deerflow/backend/AGENTS.md#architecture)、[本应用 posture](../src/deerflow_deep_research/runtime/adapters/subagent_posture.py) | 框架提供 task 委派，本应用当前没有声明 custom subagent 类型 |
| 研究结果如何回到应用？ | [run_research](../src/deerflow_deep_research/runtime/run_engine.py#L203) | 消费 stream，处理续答/失败/取消，投影最后回答到报告准入 |
| 这次模型看到了什么？ | [snapshot middleware](../src/deerflow_deep_research/runtime/adapters/snapshot_middleware.py#L16) | 第一次模型调用的 system prompt、可见工具、模型名、pin |

上游说明的 [lead_agent 目录定位](../../deerflow/backend/AGENTS.md#project-structure) 指向
[agent.py](../../deerflow/backend/packages/harness/deerflow/agents/lead_agent/agent.py) 和
[prompt.py](../../deerflow/backend/packages/harness/deerflow/agents/lead_agent/prompt.py)。
这是定位链接，不表示本次重新审计了其内部实现。日常应用工作先看本应用绑定和公开说明；只有明确的 prompt-builder / 兼容性问题才按应用 coding guide 的授权范围深入，不修改上游。

## skill 的三列状态

skill 在本项目里是三个不同的对象，不能混为一谈：

| 状态列 | 当前值 | 证据 / 入口 |
| --- | --- | --- |
| **声明可用** | 框架 native surface 可加载；本地 [SOP 快照](skills/deep-research/README.md) 仅供阅读（含来源 pin/hash） | 快照不是运行时配置，改它不改变行为 |
| **运行中实际加载** | 不强制：binding 传 `available_skills=None`，lead agent 自行决定 | 要证明实际加载，看工具调用记录 + checkpoint 消息 + [snapshot](../src/deerflow_deep_research/runtime/adapters/snapshot_middleware.py)；方法见下节 |
| **质量评估** | 无自动化统计评估（引文真实性、充分性、覆盖度）；每次搜索已物化到 [diagnostics/searches/](run-bundle.md) 可直读复核 | 显式 base 真实梯 + 人工评审（引用核对用 searches/ 文件）；fixture 结果不证明研究质量 |

把 skill 变成强制、可验收的运行时合同是独立的产品/认知策略决策（2026-10-05
计划 Phase 5），不在当前实现内。

## binding knobs：实际默认值与证据

每个装配旋钮的实际值、裁决处与锁定它的测试（守卫
[test_binding_doc_guard](../tests/unit/runtime/test_binding_doc_guard.py)
锁本表值与代码常量一致）：

| knob | 实际默认值 | 裁决 owner | 测试证据 |
| --- | --- | --- | --- |
| `config_path` | 显式解析 checked-in config（`base`/`fixture`），拒绝框架自动发现；env 钉 `DEER_FLOW_CONFIG_PATH` | [adapters/client](../src/deerflow_deep_research/runtime/adapters/client.py) `resolve_config_path` | [mirror](../tests/contract/test_wiring_mirror.py) 配置解析负例 |
| `checkpointer` | Bundle SQLite，经框架自有工厂 `SqliteSaver.from_conn_string + setup` | [adapters/client](../src/deerflow_deep_research/runtime/adapters/client.py) `bundle_checkpointer`（seam 镜像：[contracts](../src/deerflow_deep_research/runtime/adapters/contracts/client_surface.py) `CHECKPOINTER_SEAM`） | [smoke](../tests/integration/test_wiring_smoke.py)（真 saver 多轮） |
| `model_name` | `None`（用 config 声明的模型）；可显式覆盖 | [adapters/client](../src/deerflow_deep_research/runtime/adapters/client.py) `build_client` | [mirror](../tests/contract/test_wiring_mirror.py) |
| `thinking_enabled` | `thinking_enabled=True` | [contracts/client_surface](../src/deerflow_deep_research/runtime/adapters/contracts/client_surface.py) `CONSUMED_DEFAULTS` | [mirror](../tests/contract/test_wiring_mirror.py) binding-defaults 断言 |
| `subagent_enabled` | `subagent_enabled=True` | 同上 | mirror + [posture 守卫](../tests/unit/runtime/test_subagent_posture.py) |
| `plan_mode` | `plan_mode=False` | 同上 | mirror |
| `available_skills` | `available_skills=None`（完整 skill 面，不强制选择） | 同上 | mirror |
| `middlewares` | 空；`snapshot_dir` 给定时注入 assembly-snapshot middleware（第一位） | [adapters/client](../src/deerflow_deep_research/runtime/adapters/client.py) `build_client` | [smoke](../tests/integration/test_wiring_smoke.py)（snapshot 落盘） |
| `thread_id` | state.json 的 thread；per-call 注入 | [adapters/client](../src/deerflow_deep_research/runtime/adapters/client.py) `make_stream_fn` | mirror 转发断言 |
| `recursion_limit` | `recursion_limit=1000`（per-call 覆盖；AppConfig 顶层 `300` **不被**嵌入式路径消费——疤痕） | [adapters/client](../src/deerflow_deep_research/runtime/adapters/client.py) `DEEP_RESEARCH_RECURSION_LIMIT` | mirror `CONSUMED_STREAM_KWARGS` + 转发断言 |

改任何一个 knob：先改事实源（CONSUMED_DEFAULTS / client 常量），同步本表
（守卫会红逼你同步），再跑 mirror + smoke。

## 方法论长什么样

下面是 [本地 skill 原文快照](skills/deep-research/SKILL.md#research-methodology) 的中文导航，不是独立 prompt 或硬 gate；[SOP 阅读入口](skills/deep-research/README.md) 解释了来源、加载和未来调整边界：

```text
研究问题
    |
    v
Broad Exploration       广度探索：搜索背景，识别维度、观点、参与方
    |
    v
Deep Dive               深挖：定向查询、换问法、抓全文、追引用
    |
    v
Diversity & Validation  补齐事实数据、案例、专家观点、趋势、对比、反对意见
    |
    v
Synthesis Check         综合前检查：多角度、全文、多源、时效、权威性
    |                   不够就继续研究，不是固定执行一次
    v
综合回答 / 内容产出
```

这些是模型遵循的研究要求，不是 Python 状态转换，也不保证每次恰好四个阶段。
lead agent 动态选择查询、工具、委派与收束；subagent 是可用选项，不是每次都必须出现。
Harness 没有自动把 skill 的“3–5 个角度”等检查变成可阻断的机器规则。

## 实际执行与控制谁负责

```text
cli create → runtime/interaction/cli.py
  -> Bundle → runtime/entry.run_foreground → SQLite checkpointer
  -> build_client(config, subagent_enabled=True, available_skills=None)
  -> make_stream_fn(thread_id, recursion_limit=1000)
  -> DeerFlow lead agent <-> 模型、工具、按需委派
  -> stream events -> run_engine -> 状态 / journal / 最后回答准入
```

嵌入式 stream 的有效递归上限以 [make_stream_fn](../src/deerflow_deep_research/runtime/adapters/client.py#L18) 的 per-call 参数为准。
配置顶层虽然写着 `300`，当前 binding 注入 `1000`；不要只改 YAML 就以为改变了此路径。
这是图步数上限，不等于搜索次数、token 预算或研究充分程度。

“模型提议、代码裁决”目前具体落在 [产物 validator](../src/deerflow_deep_research/engine/validator.py)
和 [submit_artifact](../src/deerflow_deep_research/runtime/bundle/admission.py)。
validator 检查 kind、文件名、producer、非空和重复 hash，**不验证引文真实、观点全面或事实正确**。
本应用也没有把每次搜索结果自动提交成 evidence artifact；不能把有 journal/checkpoint 理解成“已建立完整证据库”。
[gate](../src/deerflow_deep_research/engine/gate.py) 已可按 admit 数量推导 pass/blocked，但当前 run_engine 不把它作为四阶段调度图。

## 怎样看到某一次真的发生了什么

从 [命令菜单](../COMMANDS.md) 执行 `status` / `inspect`，保留 bundle id；用 [Bundle 路径合同](../src/deerflow_deep_research/domain/bundle.py) 找到该运行。
每个 Bundle 内对象的权属（谁写、是什么、能看出什么、不能推出什么）见
[Run Bundle 地图](run-bundle.md)；下面是认知侧的判断方法：

判断 skill 加载：先看是否出现读取 deep-research 原文的工具调用及结果；journal 只有名称时，再看 checkpoint 消息。
判断委派：看 task 调用和 subagent 事件/结果；仅有 subagent_enabled=True 不足以证明实际委派。
判断完成：status 的 `delivery:` 行直接回答交付（admitted/rejected/no-answer；未记录时用 journal disposition + final/ 文件 belt）；run_engine 先写终态再经 CAS 补写交付事实，空回答记 no-answer，重复内容记 rejected。
判断质量：再评审引用、交叉验证、范围、假设与不确定性——报告声称的来源可在 diagnostics/searches/ 的可直读记录里核对；fixture 的直接回答不能证明真实研究。

## 改什么、测什么

- 改绑定/配置：先 [mirror 单元测试](../tests/contract/test_wiring_mirror.py)，再 [真实框架 fixture smoke](../tests/integration/test_wiring_smoke.py)。
- 改 stream 适配/终态：先 [run_engine 测试](../tests/unit/runtime/test_run_engine.py)，真实形状问题再用 [事件回放测试](../tests/unit/runtime/test_event_stream_replay.py)。
- 改模型研究策略：先明确是产品自有角色还是上游方法论；不能顺手改只读 skill。真实效果需显式真实梯观察，不靠脚本模型证明。
- 新增证据/质量 gate：这是产品合同与接线变更，不是多写一条 doc；走 owning change 并确认被测接口。

完整的测试选择和样本说明见 [测试资产地图](../tests/README.md)。
