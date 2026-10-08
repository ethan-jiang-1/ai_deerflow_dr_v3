# Proposal: Assert Report Structure Contract

## Why

plan C6 第一批 · B 面：validator 六码全形状级——现有裁决对 final_report 的
**内容结构**零断言（无标题、无 Sources 节、空壳短文、非 UTF-8 都能 admit）。
产出质量验收需要"报告结构契约"作为 admission 阻断维度：这是"模型提议、代码
裁决"既有模式的延伸，不改权力结构。同 change 依据 plan 骨架缺口③ 的"二选一"
裁决**删除死码 `hash_mismatch`**（无生产者；ledger 完整性由哈希链验证拥有，
内容落盘后篡改属 bundle 篡改面）——dead code 正是 validator"词汇爆炸教训"
注释警惕的对象。

## What Changes

- **validator 新增 final_report 内容结构维度**（有序规则尾部、仅对
  `kind="final_report"` 生效，四方面任一违反渲染新码
  `report_structure_violation` 并点名违反面）：
  1. content 可严格 UTF-8 解码；
  2. 至少 1 个 Markdown 标题（`^#{1,6}\s+\S`）；
  3. 存在 Sources 类节标题（标题行含 `sources`/`来源`/`引用`，大小写不敏感）；
  4. 长度包络 200–200,000 字符（模块常量声明）。
- **封闭码集变更**：`verdicts.py` 删除 `hash_mismatch`、新增
  `report_structure_violation`（六码 → 六码）；`test_admission_engine.py` 的
  闭集断言同步。
- **run-admission spec MODIFIED delta**：`Admission vocabularies are small
  closed sets` requirement 逐字更新码清单 + 新增结构维度 scenario。
- **fixture 升级为拟真报告（机械、保断言）**：四处旅程/冒烟脚本与两处单测的
  final_report 文本升级为"标题 + 正文（保留旅程断言原文片段）+ Sources 节 +
  ≥200 字符"的拟真形态（经 `runtime/scripted/__init__.py` 新增
  `fixture_report()` 共享构造器）；replay fixture 的真实报告天然合规（探针
  2026-10-08：6 标题、有 Sources、3083 字符）。

## Capabilities

### New Capabilities

none: 结构维度并入既有 validator hold point，无新 capability。

### Modified Capabilities

- `run-admission`: 封闭码集 requirement 更新——结果码清单
  （`hash_mismatch` 出、`report_structure_violation` 入）+ 新增结构维度
  scenario；validator hold point / ledger / gate / register 各 requirement
  原样存活。

## Impact

- 代码：`engine/verdicts.py`（码集）、`engine/validator.py`（结构规则）、
  `runtime/scripted/__init__.py`（fixture_report 构造器）。
- 测试：`test_admission_engine.py`（闭集断言 + 结构红绿 + scoping 负例）、
  `test_admission_runtime.py`/`test_run_engine.py`（final_report fixture
  内容升级）、四个 journey/smoke 文件（脚本报告升级）。
- spec：`openspec/changes/assert-report-structure-contract/specs/run-admission/
  spec.md` MODIFIED delta。
- 行为影响：**准入语义收紧**——从此结构不合规的 final_report 被拒绝（ledger
  记 `report_structure_violation` + 理由，内容不落盘）；现存真实报告（探针）
  全部合规，无运行时迁移。
- `deerflow/` gitlink 不触碰；`make verify`（离线）与 `make smoke`（journey
  升级后）都触发。

## Change Focus

- **Primary module / causal owner:** `src/deerflow_deep_research/engine/
  validator.py` + `engine/verdicts.py` —— final_report 准入结构契约的语义
  决策最小 owner（hold point 的裁决面）。
- **Seam classification:** deterministic-guardrail — 纯确定性结构裁决（编码/
  标题/Sources/长度），无认知角色；模型产出被代码裁决，反馈走 ledger reasons。
- **Question:** 结构空壳的 final_report 是否被 admission 挡下，且既有真实
  报告与全部旅程在契约下依然绿？
- **Necessary adjacent/external contracts:** run-admission spec 封闭码集
  requirement（answers: 码集变更的规范权威，MODIFIED delta 承载）；C 面
  searches 物化与 replay fixture（answers: 真实报告探针为契约可行性证据）；
  journey/脚本 fixture（answers: 拟真升级保住旅程的管道断言）；
  `test_admission_engine.py` 闭集断言（answers: 码集变更的守卫同步点）。
- **Evidence seam:** `make verify`（引擎红绿：四方面各自红 + scoping 负例）+
  `make smoke`（journey 升级后全绿）+ closeout gate；spec delta 过 strict
  validate 与 plan gate。
- **Not in scope:** Sources 节内容的语义核验（URL 支撑属 A 面机器）；报告
  长度质量下限的"内容质量"化（200 字符是结构地板，不是质量评分）；A 面
  admission 化；D/E 面。
- **Triggered review policies:** change-admission, local-context
