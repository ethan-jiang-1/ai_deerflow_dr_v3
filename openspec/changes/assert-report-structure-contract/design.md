# Design

## Context

validator 是有序纯规则（首错即停），当前六码全形状级；final_report 与 evidence
共用同一规则尾。探针（2026-10-08）：replay fixture 真实报告 6 标题/有 Sources/
3083 字符天然合规；smoke/旅程脚本与两处单测的 final_report fixture 是短句空壳，
阻断契约下必须先升级 fixture。`hash_mismatch` 无生产者（全仓仅定义与闭集断言两
处引用）。

## Goals / Non-Goals

**Goals:**

- final_report 的编码/标题/Sources/长度四方面成为准入裁决的一部分；
- 码集变更（死码出、新码入）在 spec、代码、闭集断言三处同步；
- 全部现存旅程与真实报告在契约下保持绿。

**Non-Goals:**

- 不做 Sources 节内容的语义核验（A 面机器管"有记录支撑"）；
- 不做内容质量评分（200 字符是结构地板）；
- 不动 hold point / ledger / gate 的权力结构。

## Decisions

**D1 结构规则挂在 validator 有序尾部、仅对 final_report 生效。**
顺序：既有规则（kind/filename/provenance/empty/duplicate）之后、ok 之前。evidence
类内容不受结构约束（scoping 负例钉住）——evidence 是调研笔记，强加报告结构是
错层。编码检查最先（decode 失败无法继续读文本）。
备选落败：独立结构 validator 机器（hold point 分裂，verdict 语义碎片化）；
放 runtime 提交前预检（裁决离开 engine，违反"模型提议、代码裁决"的裁决点纪律）。

**D2 码集变更 = 死码出、新码入，一次 delta 完成。**
`hash_mismatch` 无生产者：ledger 完整性由链验证拥有（tampering 已有响亮失败），
提交时 content_hash 由内容即时计算、不存在"不匹配"的合法路径。保留死码违背
"小闭集"立意；未来若需要"final 文件 vs ledger 巡检"，届时按 owning change
重新引入（Alternatives 记录）。
备选落败：保留作"语义槽位"（无生产者的码是词汇债务）；只加不删（码集膨胀）。

**D3 长度包络 200–200,000 字符 + Sources 标题正则。**
下限 200：低于此不可能是研究报告（防"ok"空壳）；上限 200,000： sanity 防
异常巨物。Sources 识别 = 标题行含 `sources`/`来源`/`引用`（大小写不敏感）——
覆盖本仓报告的中英惯例，不锁特定模板。常量在 validator 模块顶部声明，
测试钉住。

**D4 fixture 升级走共享构造器 `fixture_report(body)`。**
四处旅程/冒烟 + 两处单测的报告文本统一经 `runtime/scripted/__init__.py` 的
构造器生成（标题 + body（旅程断言原文完整保留）+ 依据摘要 + Sources 节），
消灭五份手写变体；journey 对报告内容的既有断言（"cost-side"、plan 常量相等、
"最终简报全文内容"）逐一保留。

## Alternatives

- **只加码不删 `hash_mismatch`**：落败——见 D2，词汇债务与"小闭集"立意冲突。
- **结构维度放 gate（阶段验收层）**：落败——gate 消费的是已 admit 事实的计数，
  结构是提交裁决的一部分；放 gate 会让坏报告先进 bundle 再谈，违反 hold point。
- **放宽旅程 fixture 而非升级（比如给脚本报告开豁免）**：落败——豁免即第二
  真相源，且"拟真化"本身提升旅程可信度（fake 模型模拟的就是研究报告）。
- **Sources 标题用封闭枚举（仅 "Sources"）**：落败——本仓报告为中文研究产物，
  来源/引用是合法等价物；正则三类覆盖且诚实声明在 docstring。

## Risks / Trade-offs

- [真实模型产出的报告缺 Sources 节被拒] → 这正是契约的目的（delivery 记录
  reject + 理由，模型侧可修复重提——replay 纪律承接）；replay fixture 与
  现存 runs 报告探针全部合规，无存量迁移。
- [fixture_report 构造器成为第二个报告模板真相源] → 构造器 docstring 明示
  "仅供 fixture 模拟，真实报告结构由 validator 拥有"；validator 常量是唯一
  规范参数源。
- [旅程断言的原文片段被破坏] → 升级规则 = 原文字符串作为 body 原样嵌入；
  make smoke 全绿为机械证明。

## Migration Plan

代码 + fixture 同 change 落地；现存 runs/ 下已 admit 的报告不回溯（准入只发生在
提交时刻）。回滚 = revert 代码与 spec delta（fixture 升级可保留，拟真无副作用）。

## Open Questions

none: 码集二选一已裁（D2），包络与正则已定（D3），fixture 路径已定（D4）。
