# Proposal: Register Source Traceability Machine

## Why

plan C6 第一批 · A 面：产出质量的第一个内容级可断言面——**来源可追溯性**：
报告中出现的 http(s) URL 是否能在同 run 的搜索语料（`diagnostics/searches/` 的
工具输出记录）中找到支撑。现状：`research-process.md` 的人肉复核承诺
（"每次搜索已物化、可直读复核"）无机器断言；C 面（已落地）钉住了物化的可靠性，
本面在其上提供纯函数判定器并注册为质量机器。

**与 plan 原意的偏离（探针证据驱动，Alternatives 详录）**：plan 原设想 A 面为
"run-admission 新维度"（validator 拒绝码）。取证否决了该形态——真实 bundle 上
"每个 http(s) URL 可溯"**不成立**（厂商 API 端点出现在报告的 shell 片段中、
模型知识类 citation URL，均为合法 miss；实测 4 bundle 中 2 个非全命中）。本面
改为：**注册机器 + 纯函数 + 测试钉样**，不做 admission 阻断；admission 化
（如仅 Sources 节内 URL）留待未来单独裁决。

## What Changes

- **新增纯模块 `engine/traceability.py`**：`trace_source_urls(report_text,
  search_corpus_texts) -> SourceTraceReport`（frozen dataclass：`urls`、
  `traceable`、`untraceable`）。URL 抽取正则 `https?://\S+` + 尾部标点剥离；
  判定 = 归一化后的 URL 是否以子串形式出现在语料拼接文本中。纯 stdlib、零 I/O；
  明确语义：证明"**有记录支撑**"，不证明"记录为真"（诚实命名"可追溯性"，非
  "真实性"）。
- **注册机器**：`engine/machines.py` 的 `DECLARED_MACHINES` 增加
  `source-traceability` 条目；`docs/quality-register.md` 增加对应行（漂移测试
  强制两侧同步——本面红绿的主闸）。
- **新增测试 `tests/unit/engine/test_traceability.py`**：①fixture 钉样——回放
  fixture 的真实报告 6 URL 全可溯（探针 2026-10-08 实证）；②合成负例——引用
  未知 URL 的报告被点名；③known-violation smoke（collector 惯例）——空语料时
  全部 URL 判 untraceable（判定器在空输入上不可能假绿）；④篡改语料——删除一
  条记录后其 URL 变 untraceable。

## Capabilities

### New Capabilities

none: 新机器走既有"register 与 DECLARED_MACHINES 同步"requirement 的约束
（spec 不枚举机器清单，新增机器不需要 delta）；validator 结果码闭集不动。

### Modified Capabilities

none: `skip_specs: true` 已声明。run-admission spec 的全部 requirement 原样
成立。

## Impact

- 文件：`engine/traceability.py`（新增）、`engine/machines.py`（+1 机器）、
  `docs/quality-register.md`（+1 行）、`tests/unit/engine/test_traceability.py`
  （新增）。
- 车道：`make verify`；runtime/pump/admission 零触碰；validator 闭集不动
  （六码原样——死码 `hash_mismatch` 的处置归 B 面的封闭码集 delta）。
- `deerflow/` gitlink 不触碰。

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/engine/
  traceability.py` —— 来源可溯性判定的语义决策最小 owner（engine 层拥有
  确定性裁决面；判定器本身纯函数，登记走 machines）。
- **Seam classification:** deterministic-guardrail — 纯函数判定器 + 注册纪律，
  无认知角色、无 I/O、不渲染 verdict。
- **Question:** 报告 URL 的"有记录支撑"是否成为可计算、被注册、可红的质量面？
- **Necessary adjacent/external contracts:** `SearchLog` 物化契约（answers: 语料
  的物理来源与 payload 形状，C 面已钉）；`DECLARED_MACHINES`↔register 漂移测试
  （answers: 机器注册的同步闸）；run-admission 的"quality register stays in
  sync" requirement（answers: 本面登记方式不触 delta 的规范依据）。
- **Evidence seam:** `make verify`（新测试套件：fixture 钉样 + 三类负例，退出码
  直测）；漂移测试对新机器名生效（删 register 行即红——apply 期红证）。
- **Not in scope:** admission 拒绝码化（探针否决，见 Why）；Sources 节解析；
  URL 语义真伪；D 面（usage 接线）；E 面（real-model-io）。
- **Triggered review policies:** change-admission, local-context
