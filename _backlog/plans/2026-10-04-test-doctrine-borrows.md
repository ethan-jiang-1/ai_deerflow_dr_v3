# Plan: test-doctrine-borrows（测试思想借鉴的两把落地）

> 类型: 设计 | 更新: 2026-10-04
> 来源: `adopt-test-doctrine` 的评估（digest：`/Users/bowhead/deer-flow/_digest/test-strategy/`）；承接 docs/testing-and-evaluation.md 的借鉴队列。

## 背景 / 现状

DeerFlow 自测体系的 digest 已消化：我们与"一句话策略"骨架一致，缺两件可借鉴的机制件——
**级 2 内容寻址回放**与**技能测试面**。其余（时长分片、Playwright 车道、monocle）按规模
门槛有意不借。

## 决策 / 方案（两把 change 的设计草案）

**第一把 `replay-chat-model`（内容寻址回放）**
- `runtime/fixtures/replay.py`：按 caller + 归一化输入哈希索引的录制回放模型——
  录一次真实运行（EASA 简报真跑已在案，重录一次带 key），fixture 存
  `tests/fixtures/replay/`；归一化剥掉日期/UUID/路径/系统提醒块，**system prompt 整个
  剔出匹配键**（提示词是频繁编辑的实现细节，不是被测契约——digest 的最关键决定）。
- miss 响亮失败（已知哈希清单 + 输入预览）；回放 fixture 无 key 进 CI smoke。
- 价值：把"real 梯"的最贵证据变成永久零成本 fixture——报告落 final/、澄清续答、
  fallback 守卫都可在**真实形状**上回归，而不再依赖假设形状的 fake 事件。

**第二把 `skill-review-surface`（技能测试面）**
- 借鉴框架的 SkillScan/review/waiver 机制，服务"拎出 deep-research 换名换 trigger"的
  定制路径：定制技能落位后过一次确定性 review（analyzer 零 LLM），waiver 信任边界按
  框架先例（逐字段精确匹配、带过期、blocker 不可豁免、不能自授权）。
- 证据：定制技能的 review 冒烟（落位→扫描→waiver 边界）。

**次序**：第一把先（独立于技能定制也有价值）；第二把跟技能定制需求一起。

## 风险 / 取舍

- [归一化遗漏易变源] → miss 的响亮清单 + 输入预览是诊断面；规则按证据增补。
- [技能 review 机制借用过重] → 只取 analyzer 调用与 waiver 边界，不搬全套豁免清单。

## 落地关联

两把 change 依次入线（各自全管道）。落地后 `docs/testing-and-evaluation.md` 的阶梯表
与借鉴队列同步收口，本 plan 关闭（CLS-010）。
