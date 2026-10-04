# Testing and Evaluation（测试思想与车道）

> 本文是"怎么测"问题的第一答处（参照 DeerFlow 自测体系的 digest：`/Users/bowhead/deer-flow/_digest/test-strategy/`，本仓沿用其纪律并按 v3 规模裁剪）。纪律不在口头——每条规矩都有钉住它的测试或在账的借鉴项。

## 一句话策略

**离线确定性是默认（stdlib gate，UV_OFFLINE 兼容）；真实边界是显式 opt-in（fixture 梯默认、base 梯带 key）；测契约不测智能（模型提议、代码裁决）；每个新守卫都能变红；门禁自身也要被测试。**

## Lanes 与各自"不证明什么"

| Lane | 命令 | 覆盖 | **不证明什么** |
| --- | --- | --- | --- |
| Application unit gate | `make verify`（stdlib，UV_OFFLINE=1 兼容） | domain 纯规则、runtime 物化（CAS/lease/journal/删除语义）、admission、mirror/配置解析、subagent posture | 不证明真实模型行为、不证明跨进程协议 |
| Integration smoke | `make smoke`（需 uv sync；CI 已接入） | 嵌入式 client + sync saver 多轮 + 有界澄清续答 + checkpoint 可读 + 装配快照 + CLI 全旅程 + 契约对比真实面 + **报告落 final/** | 不证明真实模型的研究质量（脚本模型钉死输出） |
| Real ladder（真实外部 API） | `make create … --config base`（需 key；显式 opt-in） | 真模型、真 skill、真 agent 循环、真 token 消耗 | 慢、花钱、非确定——永不进默认 CI；单次通过不构成统计结论 |
| Governance checks（非 harness lane） | 聚合治理门禁（repo 根治理目录 README） | 结构/需求/specs/指导/依赖方向 | 不证明产品运行时行为 |

## 确定性 LLM 替身阶梯（借鉴 DeerFlow 四级谱系，按需补齐）

| 级 | 状态 | 机制 | 用途 |
| --- | --- | --- | --- |
| 1 剧本模型 | ✅ `runtime/fixtures.ScriptedChatModel`（BaseChatModel 子类 + `DEERFLOW_FAKE_SCRIPT`） | 预编程消息序列（含 tool_calls 与 raise 动作），真图真中间件真 checkpointer 照跑 | 验证引擎/绑定/入口的行为契约（毫秒级、零 fixture） |
| 2 内容寻址回放 | 📋 借鉴队列（plan 卡 `test-doctrine-borrows`） | 录一次真实运行（caller+归一化输入哈希索引，system prompt 剔出键），此后零 key 确定性回放 | 把最贵的证据（真跑产出）变成永久 fixture；防 fake-green |
| 3 行为断言（live 面） | ⬜ 未规划 | 对真实运行的 trace 断言（工具选择/token/时长） | 显式 opt-in 的质量观察 |

替身选型纪律（借鉴）：**替身只替换"贵的与不确定的"（模型、时间、外部凭证），不替换"被测语义本身"**——无 fake-redis 类的先例，我们同样无假 checkpointer。

## 纪律（每条都有钉子）

- TDD：每个新守卫/修复**红先行**，回执入 tasks（偏离必须显式披露——on_event 与 subagent-posture 两例在案）。
- 负例控制：引入违规→看红→还原→看绿；**门禁自身也要能变红**（gate 红证明在案）。
- "不证明什么"成文：每个 lane/守卫声明自己不覆盖的空间，由别的 lane 接手。
- fail-closed：扫描不了的形状、解析不了的配置、缺的必填字段——一律响亮失败点名，不静默。
- scar-tissue：真实事故留疤成测试（error-fallback 守卫、澄清回声排除均由此而来）。

## 借鉴队列（挂钩在账，不靠唠叨）

| 借鉴项 | 来源 digest | 承载 | 状态 |
| --- | --- | --- | --- |
| 内容寻址 ReplayChatModel（级 2） | `test-strategy/02-deterministic-llm.md` | plan 卡 `test-doctrine-borrows` | 📋 排队 |
| 技能测试面（SkillScan/review/waiver） | `test-strategy/08-upper-layer-apps.md` §三 | 同上 plan 卡（服务技能定制） | 📋 排队 |
| 时长基线分片 | `test-strategy/05-speed-isolation.md` | 未借鉴（90 测试未到规模）；测试数过百再议 | ⏸ 规模门槛 |
| 崩溃模拟离线习语（不杀进程重建状态） | `test-strategy/07-durable-and-recovery.md` §二 | 部分已用（死子进程/直构状态）；其余按需 | ⏸ 部分在用 |

## 已知限制

见 [`known-limitations.md`](known-limitations.md)（LLM fallback 守卫后的框架行为记录、CI UNVERIFIED-until-push 已收口、checkpoint 体积已由 delta 模式修复——存留 patch 版本告诫）。
