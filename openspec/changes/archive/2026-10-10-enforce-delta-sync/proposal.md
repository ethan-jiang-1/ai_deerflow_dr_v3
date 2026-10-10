# Proposal: enforce-delta-sync

## Why

2026-10-10 fresh-agent 全库审计系统性核对 71 个归档 change 的 86 条 delta requirement，
发现**两条 ADDED requirement 从未落进主 spec**：deerflow-wiring 的「The framework home is
pinned outside the application subtree」（2026-10-07-pin-framework-home）与
doc-truthfulness 的「Root README inventory counts are machine-pinned」
（2026-10-04-enforce-doc-recurrence-guards）——归档 CLI 的 spec-update 确认被跳过所致
（同类前科：868d4f0 修 entry-surface/agent-playbook 两处）。两处已人工补齐（ca82507），
但没有任何机器守卫：漏 sync 只能等下次人工核对才发现。归档账本（_backlog CLS-023 卡）
要求把这一漂移类变成 checker 当场红。

## What Changes

- `check_project_specs.py` 默认模式新增 delta-sync 完整性规则：归档 delta
  （`openspec/changes/archive/*/specs/<cap>/spec.md`）中每个 `## ADDED Requirements` 下的
  requirement 标题，必须在 `openspec/specs/<cap>/spec.md` 主 spec 在场；缺者点名归档
  change、capability、标题（check `deltaSyncMissing`）
- 豁免面封闭：同 capability **更晚归档** delta 的 `## REMOVED` / `## RENAMED` 携带该标题
  （正式退役，含 RENAMED 的 `#### FROM:` 行）；或声明式 allowlist
  （`DELTA_SYNC_ALLOWLIST`，(capability, title) → 理由，无理由条目即红——沿用
  doc-hygiene MARKER_ALLOWLIST 的形状）记录 out-of-band 修复
- 首条 allowlist：entry-surface「Six verbs mirror the state machine and observation
  layers」——868d4f0 审计修复吸收 operator-failure-diagnosis 漏 sync 时 out-of-band 改名为
  「The verb set mirrors…」，无 delta 正式记录该改名
- capability 无主 spec 的归档 ADDED 也响亮失败（check `deltaSyncCapabilityMissing`）
- 治理 unittest 套件红先绿后（`test_project_specs.py` 新增案例矩阵：缺失红 / 在场绿 /
  后续 REMOVED 豁免 / allowlist 豁免 / capability 缺失红）
- 规范归属：doc-truthfulness **ADDED** requirement「Archived ADDED requirements are
  machine-pinned into main specs」（随归档 sync 进主干）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `doc-truthfulness`: ADDED requirement——归档 delta 的 ADDED requirement 机器钉进主 spec，
  豁免面（正式退役 + 带理由 allowlist）与 declared limitation（MODIFIED 不钉、同日归档
  序按目录名近似）成文

## Impact

- 影响：`openspec/governance/check_project_specs.py`（+1 规则 + allowlist 表）、
  `openspec/tests/governance/test_project_specs.py`（+案例矩阵）、
  `openspec/governance/README.md`（checker 行措辞）、`openspec/specs/doc-truthfulness/spec.md`
  （归档 sync）；真树现值：86 条中 84 条直接在场、1 条后续 REMOVED 豁免、1 条 allowlist
  豁免——规则上线即绿
- 风险：低——规则只在默认（全树）模式跑，selected-change 模式不动；豁免面封闭声明，
  扩 allowlist 是 visible change（无理由即红）
- 边界：不做全量历史 replay（双向重构会把 out-of-band 改名误报，见卡内取舍）；不新开
  独立 checker（避免 gate 清单/CI 声明面联动扩员）；不改 `openspec archive` CLI 行为

## Change Focus

- **Primary module / causal owner:** `check_project_specs.py` 的默认模式——delta-sync
  规则的行为承载；规范 owner 是 doc-truthfulness（声明层真相性）
- **Seam classification:** deterministic-guardrail — 纯文本结构事实的机器校验；无模型、无运行时行为
- **Question:** 归档 delta 的 ADDED requirement 能否被机器钉进主 spec，使「归档时
  spec 更新被跳过」这一漂移类当场红，而非等下次人工审计？
- **Necessary adjacent/external contracts:** doc-truthfulness 主 spec（本 change 给规则以
  规范归属）；`test_project_specs.py`（红绿凭据形状）；治理 closeout gate / CI canonical
  序列（check_project_specs 已是组件，无需扩员）
- **Evidence seam:** 治理 unittest 红（植入的归档 ADDED 缺失 → 非零且点名）→ 实现绿 →
  真树 `check_project_specs.py` exit 0（86 条对账现值在案）→ 治理套件全绿
- **Not in scope:** 全量 replay；独立新 checker；`openspec archive` CLI 行为；MODIFIED
  标题钉死（out-of-band 改名由 allowlist 承载——declared limitation）
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 归档 delta 的 ADDED requirement 钉进主 spec（封闭豁免面） | 无——纯归档↔主干文本对账事实 | `check_project_specs.py` 新规则 + `DELTA_SYNC_ALLOWLIST` + 治理 unittest 案例矩阵 | non-bypassable | 豁免面必须走声明表（扩 allowlist = visible change，无理由即红）；漂移点名 change/cap/标题 | 复用既有 gate 组件与 allowlist 形状（doc-hygiene MARKER_ALLOWLIST 先例），不新增 checker/CI 面 | 治理 unittest 红→绿 + 真树 exit 0 + closeout gate 0 |
