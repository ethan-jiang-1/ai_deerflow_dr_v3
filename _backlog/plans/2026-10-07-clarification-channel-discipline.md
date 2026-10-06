# Plan: clarification-channel-discipline — 反问与计划确认的通道纪律

> 类型: 设计 | 更新: 2026-10-07

## 背景 / 现状

2026-10-07 真梯动态 review（bundle `runs/d_20261006/5128f695-e418-4173-b89e-f023b55aa9fe`，
completed g1/rev5，exit 0）炸出三个同根现象：

1. **反问通道走私计划确认**：模型把"请确认是否按此计划执行"连同全文计划塞进
   `ask_clarification`，而不是走 `<research-plan>` 计划闸门。headless 自动应答放行，
   代价：auto_proceed 预算烧掉 2/2（journal `auto_continuation` count 1/2→2/2），
   计划文本被完整重摆 2 遍。我们造了计划闸门正门，模型走的是窗。
2. **兄弟调用丢弃**：反问与 `web_search` 同轮时，框架 `ClarificationMiddleware` 按设计
   丢弃同轮兄弟工具调用（stderr: "dropping … so the turn can interrupt"）——本轮 3 个
   搜索被扔、下轮重发，检索工作白做一遍。丢弃本身是 deerflow 语义（用户答前不许跑工作），
   根因是现象 1 的通道混淆放大了它。
3. **静默吸收无可观测痕迹**：auto_proceed 预算耗尽后，第三轮模型仍发出 2 个
   `ask_clarification`，这次未被拦截、被 answered 集合吸收，`unanswered_ask_clarification`
   判 False 直接走完成路径——journal 对这 2 次反问**零事件**。对"证据高于感觉"的产品，
   交互史重建出现黑洞。

正面基线：fixture 演练（bundle `1a2b82c1`，`DEEP_RESEARCH_INTERACTIVE=1` 管道喂答）证明
`plan_gate_degraded` 诚实降级路径正常入账、不硬拦。**UNVERIFIED**：真人 TTY 下模型对
`<research-plan>` 标记的遵从率——headless 跑不出该路径，需驾驭者亲手 TTY 验收提供基线。

## 决策 / 方案

app 侧双管齐下（`deerflow/` 只读，框架中间件不在修改范围）：

1. **提示词/契约层**：反问契约明确"提问轮只携带 `ask_clarification`，不同轮携带其他
   工具调用"；计划确认必须走 `<research-plan>` 标记通道。`PLAN_REQUEST_SUFFIX` 已有
   "如需先澄清问题，请直接提问，获得回答后请再次输出带标记的研究计划"的雏形，需复查其
   覆盖面（headless 自动应答轮次是否同样受约束）。
2. **引擎层**：`run_engine` 对"未被检测出的 ask_clarification"（落在 answered 集合内的
   反问）补一条 journal 事件（如 `clarification_absorbed`），消除静默吸收，使交互史
   可完整重建。

否决过的备选：改框架中间件让兄弟调用先执行（违反只读边界）；把丢弃改为缓冲重放
（框架语义，不可控且复杂度不值）。

## 风险 / 取舍

- [提示词约束对模型遵从率不保证] → 沿用 plan marker 同款"诚实降级"哲学：不硬拦，
  只留事件痕迹；遵从率由真梯复验测量。
- [answered 反问的检测依赖框架事件形状] → 域层已有 `TerminalObservation` 纯函数模式
  （`domain/clarification.py`），扩展而非另起；LLM-Node Authoring Gate：本卡主体是
  deterministic guardrail + wiring，非认知改动，不造新 prompt 能力。
- [journal 新事件类型需过治理 checker] → 沿用 `lifecycle` category，红绿先行。
- [先修提示词可能改变反问频率] → TTY 验收基线先行，避免无基线调参。

## 落地关联

尚未立 OpenSpec change。实施时走 proposal（含 Change Focus）→ design/tasks → 红绿 →
门禁 → sync → archive。验收判据：真梯重跑后 journal 能完整重建全部交互轮（含被吸收的
反问），且不再出现"计划确认走私反问通道"导致的重复摆计划与预算空烧。
