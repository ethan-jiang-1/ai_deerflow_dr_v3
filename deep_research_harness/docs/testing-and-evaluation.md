# Testing and Evaluation（测试思想与车道）

> 找测试文件、接口、样本来源与最小红绿命令，先读 [测试资产地图](../tests/README.md)。本文是车道策略参考。
>
> 车道纪律参照已消化的测试战略分析；本文不以测试数或目录位置代替行为证据。

## 一句话策略

**离线确定性是默认（stdlib gate，UV_OFFLINE 兼容）；真实边界是显式 opt-in（fixture 梯默认、base 梯带 key）；测契约不测智能（模型提议、代码裁决）；每个新守卫都能变红；门禁自身也要被测试。**

## Lanes 与各自"不证明什么"

| Lane | 命令 | 覆盖 | **不证明什么** |
| --- | --- | --- | --- |
| Application unit gate | `make verify`（stdlib，UV_OFFLINE=1 兼容） | domain 纯规则、runtime 物化（CAS/lease/journal/删除语义）、admission、mirror/配置解析、subagent posture | 不证明真实模型行为、不证明跨进程协议 |
| Integration smoke | `make smoke`（需 uv sync；CI 已接入） | 嵌入式 client + sync saver 多轮 + 有界澄清续答 + checkpoint 可读 + 装配快照 + CLI 全旅程 + 契约对比真实面 + **报告落 final/** | 不证明真实模型的研究质量（脚本模型钉死输出） |
| Real ladder（真实外部 API） | `make create PROBLEM="…" CONFIG=base`（需 key；显式 opt-in） | 真模型/agent 循环/token；skill 可用，实际加载看 checkpoint 证据 | 慢、花钱、非确定——永不进默认 CI；单次通过不构成统计结论 |
| 发布冷启动 | `git clone --recursive` → `uv sync` → `make verify` → fixture `make create` | 发布面没有偷偷依赖开发工作区；随行代码与兄弟布局完整 | 不证明真实 API 质量、多用户服务能力 |
| Governance checks（非 harness lane） | 聚合治理门禁（repo 根治理目录 README） | 结构/需求/specs/指导/依赖方向 | 不证明产品运行时行为 |

## 三种质量对象

1. **研究引擎质量**：角度是否充分、事实是否有来源、报告是否有洞察——由真实梯 +
   评审负责，当前**没有自动化统计评估**。
2. **Harness 控制质量**：状态诚实、失败可见、证据经 validator、ledger 可验证、
   运行可检查——由 unit + smoke 负责，大部分可离线确定性验证。
3. **发布质量**：全新环境能否按发布说明跑起来——由冷启动 lane 负责；它证明
   "能启动并完成 fixture"，不冒充研究质量验收。

## 最小车道选择

不要从真实端到端开始；按问题选最小车道，再按风险扩大：

```text
规则 / 状态 / 文件 / 准入问题      → make verify
DeerFlow 接线 / 事件 / checkpoint → make smoke
真实模型 / skill / 外部工具质量    → base 真实梯（显式 opt-in）
发布布局 / 新机器冷启动           → 冷启动 lane
代码结构 / 依赖方向 / 发布面       → governance checker
```

## 确定性 LLM 替身阶梯（借鉴 DeerFlow 四级谱系，按需补齐）

| 级 | 状态 | 机制 | 用途 |
| --- | --- | --- | --- |
| 1 剧本模型 | ✅ [ScriptedChatModel](../src/deerflow_deep_research/runtime/scripted/__init__.py) + `DEERFLOW_FAKE_SCRIPT` | 预编程消息（含 tool_calls 与 raise），框架 smoke 保留真图/中间件/checkpointer | 零凭证验证绑定/入口合同，不证明研究质量 |
| 2 记录事件流回放 | ✅ [事件记录](../tests/fixtures/replay/real-small-stream.json) + [回放测试](../tests/unit/runtime/test_event_stream_replay.py) | 记录形状经真实 Harness pump 回放，不重跑模型/工具 | 锁定 flat chunk 适配与 journal 回归 |
| 3 内容寻址模型回放 | ✅ [机制实现](../src/deerflow_deep_research/runtime/scripted/replay_model.py) + [机制测试](../tests/integration/test_replay_model.py) | 临时脚本录制/回放与 miss 诊断；[留存模型样本](../tests/fixtures/replay/real-model-io.jsonl) 已有首个测试消费者（形状契约 + 回放机制参与，来源限制在消费点声明） | 不保留完整模型协议；尚无真实模型记录接入图的旅程证明 |
| 4 行为断言（live 面） | ✅ [behavior_profile](../src/deerflow_deep_research/engine/behavior_profile.py) + [断言测试](../tests/unit/engine/test_behavior_profile.py)（[真实 journal fixture](../tests/fixtures/replay/real-research-journal.jsonl)） | 纯派生自真实 run 的 journal：工具选择计数、事件构成、时长跨度，对照声明期望、违规点名；注册机器 `behavior-profile` | 显式 opt-in 的质量观察：**观察非准入**（不产准入码、不进 gate）；**token 不断言**——journal 无结构化字段，解析内容字符串即伪造维度（test-evidence spec 在案） |

替身选型纪律（借鉴）：**替身只替换"贵的与不确定的"（模型、时间、外部凭证），不替换"被测语义本身"**——无 fake-redis 类的先例，我们同样无假 checkpointer。

## 纪律（每条都有钉子）

- TDD：每个新守卫/修复**红先行**，回执入 tasks（偏离必须显式披露——on_event 与 subagent-posture 两例在案）。
- 负例控制：引入违规→看红→还原→看绿；**门禁自身也要能变红**（gate 红证明在案）。
- "不证明什么"成文：每个 lane/守卫声明自己不覆盖的空间，由别的 lane 接手。
- fail-closed：扫描不了的形状、解析不了的配置、缺的必填字段——一律响亮失败点名，不静默。
- scar-tissue：真实事故留疤成测试（error-fallback 守卫、澄清回声排除均由此而来）。

## 借鉴队列（已收口）

队列已全部处置；全对照修订与逐项结论见 issue 卡 CLS-010（`_backlog/_archived/_settled_issues/2026-10-04-test-doctrine-borrows.md`）。
