# Design

## Context

C 面已钉住物化（11=6+5，键完整非空）。判定器输入两端都有稳定形状：报告文本
（`final/report-gen{N}.md`）与语料（每条记录的 `content` 为工具原始输出字符串、
`arguments` 为调用参数 dict）。探针实证（2026-10-08）：回放 fixture 报告 6 URL
全可溯；真实历史 bundle 4 样本中 2 个非全命中（厂商端点、模型知识 URL）——
admission 阻断形态被证据否决。

## Goals / Non-Goals

**Goals:**

- "有记录支撑"成为纯函数可计算面，注册进机器清单与 register；
- 三类负例（合成未知 URL / 空语料 / 篡改语料）保证判定器不会假绿。

**Non-Goals:**

- 不进 validator、不加结果码、不阻断 admission；
- 不解析报告结构（Sources 节识别属未来裁决面）；
- 不做 URL 归一化的穷尽（重定向、短链、转义变体——明示为已知边界）。

## Decisions

**D1 判定 = 归一化 URL 的子串包含。**
抽取 `https?://\S+`，剥尾部标点 `),\]\}>"'.;`；语料 = 全部记录的
`content + json.dumps(arguments)` 拼接；URL（原样）在语料中出现即可溯。
**为什么足够**：工具输出是搜索引擎/fetch 的原始返回，citation URL 若真来自
检索必然逐字出现在其中；子串包含不引入假阳性。**已知边界（如实声明）**：
URL-decode/变体归一不做——fetch 内容若被工具截断可能漏配对（真实样本
c7f0d36f 的 jina.ai 即疑似此类），该边界被探针记录且是"不阻断"决策的依据之一。
备选落败：多级归一化（decode+scheme 剥离+尾斜杠）——提升召回但引入误配风险
且无法在纯函数内诚实命名；留未来按证据增强。

**D2 注册为机器而非 validator 维度。**
探针证据：真实 run 的合法 miss 使阻断形态会拒绝诚实完成的 run（validator 是
hold point，误拒 = 交付被卡）。机器形态保留全部价值（可计算、被钉、进 register）
且零交付风险。未来 admission 化（如仅 Sources 节）是独立规范语义裁决。
备选落败：validator 新码 `source_untraceable`（见 proposal Why 的探针证据）。

**D3 测试四件套对应 collector 惯例。**
fixture 钉样（金样本行为）、合成负例（点名列出 untraceable）、空语料
（collector 类 known-violation smoke：空输入全红，杜绝假绿）、篡改语料（删除
一条记录 → 其 URL 变 untraceable，钉语料完整性依赖）。回放 fixture 在测试内
现场驱动（0.06s 实测，unit 车道可承受）。

## Alternatives

- **admission 阻断（plan 原意）**：落败——真实 bundle 探针证明会拒绝诚实 run；
  完整证据与未来选项记录于本 change。
- **判定器放 `runtime/`（读文件自己取语料）**：落败——I/O 归 runtime、判定归
  engine 的分层纪律；纯函数只收数据，语料装配由测试/未来调用方负责。
- **同时落 B 面结构契约**：拆两把——B 面动封闭码集与 spec delta（规范语义、
  独立拍板面），本面零契约；混装会让 review 面不可分。

## Risks / Trade-offs

- [子串包含误报"可溯"（URL 恰好作为普通文本出现）] → 接受：方向是"证有"
  宽松而非"证无"；该边界与"不证真"的命名纪律一致，register 行明示。
- [机器名进 register 后测试对文件位置敏感] → register 行写相对路径（既有
  惯例），漂移测试只查名字在场，不锁行号。
- [fixture 报告演进导致钉样失效] → 同 C 面的金样本纪律：泵演进随 owning
  change 更新预期（探针命令已记录在案）。

## Migration Plan

纯增量（新模块 + 新测试 + 两处登记一行），无迁移。回滚 = 删文件 + 还原两行。

## Open Questions

none: 形态（机器 vs 码）已由探针证据与授权裁决。
