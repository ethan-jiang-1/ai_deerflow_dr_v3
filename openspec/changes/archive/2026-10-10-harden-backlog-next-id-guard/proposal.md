# Proposal: harden-backlog-next-id-guard

## Why

BUG-002（`_backlog/bugs/BUG-002-doc-hygiene-next-id-blindspot.md`，2026-10-10 审计）证实：
`_backlog/issues/README.md` 曾同文件滞留两个 "Next available issue ID" 声明（头注 CLS-021
已被占用、正文 CLS-022 正确），而 `check_doc_hygiene.py` 全绿通过——其 Next-ID 校验只读
`_archived/README.md` counters 表与归档 index，活跃/归档 README 里**人读的声明行不在任何
校验路径上**。同日已把推导模型修为"归档 ∪ 活跃"（账本成文法则），但声明行的**唯一性**与
**声明值一致性**仍无机器守卫：多声明点是复酿温床，第三份拷贝随时可再漂移。

## What Changes

- `check_doc_hygiene.py` 账本一致性规则增加两条 red-first 检查：
  - 每个 ledger README（`issues/`、`bugs/`、`_archived/_fixed_bugs/`、
    `_archived/_settled_issues/`）对同一 ID 前缀的 "Next available … ID" 声明行**至多一条**；
  - 任何声明值 SHALL 等于按账本法则推导的下一个 ID（归档 index ∪ 归档卡 ∪ 活跃卡的
    最大已分配号 + 1）。
- `--self-test` 增负例：同文件双声明（其一为旧值）必须红；声明值与推导不一致必须红；
  对应 ∪ 一致的正例保持绿。
- `openspec/specs/doc-truthfulness/spec.md` 的 "Ledger bookkeeping surfaces are
  machine-consistent" requirement 以 MODIFIED delta 同步扩展（archive 时吸收）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `doc-truthfulness`: MODIFIED——"Ledger bookkeeping surfaces are machine-consistent"
  增加 Next-ID 声明唯一性与声明值一致性两个 SHALL，及对应失败 scenario。

## Impact

- 影响：`openspec/governance/check_doc_hygiene.py`（检测 + self-test 负例 + ∪ 推导
  抽函数共用）、`openspec/specs/doc-truthfulness/spec.md`（delta 吸收）；账本 README
  无需改动（当前树经 2026-10-10 手工去重后已满足新规则，新规则上线即绿）。
- 风险：低——纯文本层检查，无运行时触及；负例先红后绿锁住回归路径。
- 边界：不修改、不深读 `deerflow/` gitlink；不触碰应用运行时与 CI 声明面。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` — 唯一
  行为承载是其账本一致性规则的两个新 red-first 检查与 self-test 负例；spec delta 是同一
  裁决的规范面。
- **Seam classification:** deterministic-guardrail — 红先规则跑在文本/账本事实上；无模型、
  prompt、状态机或生命周期结果被触及。
- **Question:** 账本 README 内的 Next-ID 人读声明能否被机器钉死为"每文件每前缀至多一条、
  且值等于 ∪ 推导"，使 BUG-002 的漂移类（多拷贝 + 无声明校验）永久变红？
- **Necessary adjacent/external contracts:** `_backlog/README.md` 知识地图表 +
  `bugs/README.md` + `_archived/_fixed_bugs/README.md`（answers: ∪ 编号法则的成文出处——
  机器化的对象是这条既有法则，不是新法则）；`doc-truthfulness` spec（answers: 门禁语义的
  规范归属与存续文本）。
- **Evidence seam:** `python3 openspec/governance/check_doc_hygiene.py --self-test`
  （负例红/正例绿，退出码直测）+ 全树 `check_doc_hygiene.py` exit 0。
- **Not in scope:** YAML frontmatter 卡头（2026-10-09 已裁定不借）、挂起池编号
  （无编号面）、账本 README 措辞重写、`check_ci_governance` 声明面、根 README 计数钉死。
- **Triggered review policies:** control-placement, change-admission, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Next-ID 声明唯一性/一致性从"人执行惯例"升格为机器门禁 | 无——纯文本事实，无认知候选 | `check_doc_hygiene.py` 账本一致性规则（`_rule_ledger_consistency`） | non-bypassable | 账本"编号、索引、计数三处一致"ritual 不被无声破坏；违规时点名文件与冲突声明 | 复用既有 ∪ 推导与 `BACKLOG_NEXT_ID_RE`，不新增第二解析器 | `--self-test` 退出码直测 + 全树 checker 退出码（红先：负例先行，实现转绿） |
