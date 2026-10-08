# Design

## Context

现状：`openspec/README.md` 是 18 行 Reading Map（config/specs/product/guidance/
governance 五条路由）；闭环知识散落在 `_backlog/README.md` 总流程、
`change-guidance/` Policy Route、`governance/README.md` 门禁序列、
`deep_research_harness/docs/testing-and-evaluation.md` 车道表、
`tests/README.md` 资产地图与 `governance/selected-change-closeout.md` 收尾义务里。
没有一个页面把它们按"一次变更的生命周期"串起来。约束：入口链文件相对链接由
`check_doc_hygiene.py` 机器校验；根 `AGENTS.md` 预算余量 22 字符；入口层预算
ratchet 只降不升；`openspec/README.md` 本身无字符预算但在 ENTRY_DOCS 内。

## Goals / Non-Goals

**Goals:**

- 一页走通六步闭环，每步链接可点达真实 owner（路由，不复制正文）。
- 两个词汇块（证据分层"四件不同的事"、门禁等级四分）以本仓实例定义，成为后续
  change（C2 标注、C6 验收面）的引用锚点。

**Non-Goals:**

- 不给任何规则标注等级、不加任何必填段、不建 deviation register（C2 的范围）。
- 不改 checker、不加预算、不建新 spec capability。
- 不在 app `docs/` 层建镜像页（闭环是 SDLC 面，应用文档另有 Reader Roles）。

## Decisions

**D1 落点 = `openspec/README.md` 扩展，不新建页。**
为什么：它是 SDLC 层既有入口（ENTRY_DOCS 成员、链接被机器校验、无字符预算），
且闭环六步的 owner 大半在 `openspec/` 树内，路由距离最短。
备选落败：根 `AGENTS.md` 路由扩展（余量 22 字符，ratchet 纪律不涨预算）；
app `docs/` 新页（DOC_LAYER_DOCS 清单要动 checker 声明表，且读者角色错位——
`docs/` 是应用运行面文档）；新建 `openspec/development-loop.md`（多一个入口
文件多一份维护面，Reading Map 本来就该是它）。

**D2 词汇块命名取本仓车道，不引语料原词。**
"四件不同的事"映射为：**离线单元与契约 mirror（`make verify`）/ 装配 smoke
（`make smoke`）/ 真实梯观察（显式 opt-in）/ 冷启动发布（release-face）**——
前四者已在 `testing-and-evaluation.md` 车道表各有"不证明什么"列，词汇块只做
命名与链接，不重复列内容。冷启动作为第四件的发布面补充。门禁等级四分用本仓
实例举偶（治理 checker=机器门禁、回执=自我声明、远端 required-checks 配置=
仓库外不可核实），语料出处标注为"上游参考（DeerFlow 应用开发语料·卷二组织
立场，钉定 v2.1.0）"，不冒充本仓要求。

**D3 结构：Reading Map 保留，闭环六步成节，词汇块两个小节。**
页面骨架：`# Deep Research OpenSpec` → 既有 Reading Map（不动）→ `## 开发闭环
（一页走通）`六步编号列表（每步一句话 + 链接 owner）→ `## 证据分层：四件不同的
事` → `## 门禁等级（读规则先问在哪层）`。总体控制在 ~70 行内，遵守"路由不
复制"纪律（Information Map 规则）。

**D4 配套两行小改。**
`_backlog/README.md` 总流程节末补一行"全景一页走通见
[openspec/README.md](../openspec/README.md) 开发闭环"；`local/deep-research.md`
Reader Roles 表补 `openspec/README.md` 行（读者=维护者/coding agent，job=走通
开发闭环与两级词汇）。两文件均在入口链/指导层，无预算约束，链接守卫覆盖。

## Alternatives

- **根 AGENTS.md 扩展为闭环页**：落败——预算 2425、实测 2403、余量 22 字符，
  装不下任何一步；涨预算违反 ratchet 纪律，且根 AGENTS 的定位是路由不是教程
  （分层指南原则）。
- **app `docs/` 新建 development-loop.md**：落败——`docs/` 层是应用运行面文档
  （Reader Roles 表在案），闭环六步的 owner 在 `_backlog`/`openspec`/governance，
  读者角色错位；且需动 `DOC_LAYER_DOCS` 声明表（本 change 声明不动 checker）。
- **建新 capability spec（`development-loop`）承载闭环为规范**：落败——闭环页是
  导航与词汇，无规范级行为；把 guidance 写成 spec 会制造 competing authority
  （guidance never creates runtime behavior）。规范性部分留给 C2。
- **语料原词直搬（"能 import / 包测试绿 / 装上了 / 宿主侧行为被观察到"）**：
  落败——那是 extension 包形态的四层；我们是内嵌 harness 形态，对不上，照搬
  制造假词汇。取其结构（分层声明边界），换本仓车道命名。

## Risks / Trade-offs

- [闭环页膨胀成第二份手册，稀释入口层注意力] → D3 行数约束 + "路由不复制"
  纪律；每步一句话，内容留在 owner。
- [词汇块与车道表漂移（车道改名后词汇页过时）] → 词汇块只命名+链接，不复制
  车道表内容；车道表改名会断链接（doc-hygiene 红），漂移被既有守卫接住。
- [C2 未落地前，词汇块无人引用变成装饰] → 接受：地图先行的收益（可走通性）
  独立于 C2；C2 的 proposal 会引用本页词汇作为锚点。
- [`_backlog`/local 两处小改被后续重构遗忘] → 两处都是一行级登记，且入口链
  链接守卫覆盖 `_backlog/README.md`；local profile 无机器守卫，靠 change 记录
  在案。

## Migration Plan

纯文档落地，无运行时迁移。回滚 = revert 三个文件编辑。

## Open Questions

none: 落点、命名、结构均已裁决；C2 及后续引用方式属其各自 change。
