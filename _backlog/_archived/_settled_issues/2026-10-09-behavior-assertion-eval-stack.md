# Issue: 行为断言 eval 栈 —— 研究质量的机器可断言面（替身阶梯级 4）

> 立卡: 2026-10-09 ｜ 关闭: 2026-10-10 ｜ 状态: 已结 ｜ 类型: Task ｜ 毕业门: 已过 → establish-behavior-assertion-lane ｜ 可关闭: 是

**问题与期望结果：** [triggers.md](../triggers.md)「行为断言 eval 栈」行**已触发**（CLS-020/CLS-017
裁决③判定"需要断言研究质量本身时"条件满足；本卡按删行规则消费该行，句子留在 owner 卡
CLS-010/CLS-017）。驾驭者裁决③在案：质量第一指摄 = **产出质量**——测试资产是约束机制，
"我们生产的内容是对的"是终点。现状：产出质量的机器断言面只有三个点；替身阶梯级 4
（行为断言 live 面）未规划；留存模型样本无测试消费者；test-evidence 的 owning main spec
至今未建（governance README 与 CLS-017:114 双处在案）。期望：级 4 有 owning spec 与第一台
机器资产，研究行为面可断言、可红绿。**常设授权（2026-10-09）**：propose 后不必等拍板，
直接 apply→archive→提交到干净收口。

**当前情况（2026-10-09 盘点）：**
- 已有断言面三件：`report_structure_violation`（validator 结构契约）、物化计数
  （11=6+5 + 未配对不物化负例）、`source-traceability`（URL 有记录支撑，6/6；证支撑不证为真）。
- 替身阶梯 1–3 ✅（剧本模型 / 事件流回放 / 内容寻址回放）；**级 4 ⬜ 未规划**（车道表定义：
  "对真实运行的 trace 断言（工具选择/token/时长），显式 opt-in 的质量观察"）。
- `tests/fixtures/replay/real-model-io.jsonl`：1 行 key/output，缺 input/model/pin/录制命令，
  不能独立复核来源（tests/README:84 在案），无测试消费者。
- `runs/` 存 2026-10-03..07 真实 bundle；journal 形状（最大 34 事件实证）：`model_tool_call.calls`
  携带工具名（web_search/web_fetch/task/ask_clarification）、`ts` 可算时长、`subagent_event`
  为委派流——**工具选择与时长干净可派生；token 无结构化字段**（仅藏于内容字符串）。
- CLS-017 遗留裁决维持：E（完整图回放）立项才动（需录制承诺：费用+脱敏）；F（陈述级接地）
  首轮不进（语义裁决点 + agents/ bounded role）；G（方差）显式不做。
- CLS-017:114 诫命：产出质量面超出 run-admission 骨架承载时**先立 owning spec**——行为断言
  是质量观察不是 run 准入，超出该骨架，故先立 `test-evidence`。

**未决问题：** 无需人裁决的悬空项——级 4 断言维度按证据自决（工具选择+时长+事件构成；
token 待干净生产者，如实登记限制）；owning spec 先立（CLS-017:114 诫命适用）；E/F/G 维持
既有裁决；常设授权已覆盖拍板边界。

**下一步：** 已收口：change 归档为 `openspec/changes/archive/2026-10-10-establish-behavior-assertion-lane/`
（`test-evidence` 进主干，13 能力 +4 requirements；behavior-profile 机器 + 真实 journal 钉样
+ 留存样本首个消费者全落地，make verify 0/249、负例控制红绿在案）。本卡按 ritual 关闭为
CLS-020，去向 = establish-behavior-assertion-lane。

## 方案与取舍

首片四件（一把 change，全用现存资产、零模型面、零运行时接线改动）：

| # | 件 | 形态 |
|---|---|---|
| 1 | 新 capability spec **`test-evidence`**（owning main spec） | 证据阶梯诚实边界纪律（每级声明不证明什么）+ 级 4 行为断言语义（纯派生自真实 journal、观察非准入、封闭事件词表） |
| 2 | `engine/behavior_profile.py` 纯模块 + 注册机器 | 从 journal.jsonl 派生行为画像（工具选择计数、事件构成、时长跨度）；`DECLARED_MACHINES` + quality-register 双侧同步（漂移测试主闸，同 source-traceability 先例） |
| 3 | fixture 钉样断言 | 从真实 bundle 提取 journal fixture（同 real-small-stream.json 先例，runs/ 不入库）：画像=声明值钉样；负例——零搜索调用的退化研究被点名 → 红 |
| 4 | real-model-io.jsonl 首个测试消费者 | 回放断言（输出=记录 output），测试内如实注明来源不可独立复核的既有限制 |

**不进首片（裁决在案维持）**：E 完整图回放（等录制承诺）；F 接地抽样（语义裁决 + agents/
bounded role，首轮不进）；G 方差（显式不做）；token 维度断言（journal 无结构化字段——待干净
生产者，如实登记为级 4 限制）；CLI live 面（entry-surface 六动词不动；对 live bundle 跑画像
的入口属后续触发）。

## 验收标准

| 行为 | 缝类 | 通过/失败信号 | 证据 owner |
|---|---|---|---|
| 画像机器注册↔账同步 | deterministic-guardrail | `DECLARED_MACHINES` ↔ quality-register 漂移测试：删行/加行 → 红 | unit |
| 真实 journal 画像钉样 | deterministic-guardrail | 画像字段 = 声明值（工具计数/事件构成/时长）；改数 → 红 | unit |
| 退化研究负例 | deterministic-guardrail | 零 `web_search`/`web_fetch` 调用的 journal → 画像点名违反面 → 红 | unit |
| 留存样本被消费 | deterministic-guardrail | ReplayChatModel 消费 real-model-io.jsonl：输出 = 记录 output；来源限制注明 | integration |
| 阶梯表同步 | wiring | testing-and-evaluation 级 4 ⬜→✅（含限制列：token 不断言、观察非准入） | doc 检查 + review |

## 落地关联

OpenSpec change **establish-behavior-assertion-lane**（新 capability `test-evidence`；常设授权下
propose→apply→archive 连续执行）。本卡随 change 吸收关闭，去向登记，CLS-020。

## 关闭条件

做：change archive + 全门禁绿 + 本卡迁 `_archived/_settled_issues/`（CLS-020，去向 =
establish-behavior-assertion-lane）。
