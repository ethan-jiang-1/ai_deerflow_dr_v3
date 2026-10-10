# Design: enforce-delta-sync

See proposal.md — Why. The archive is the record of what was approved; the main
specs are the living authority. A skipped `--yes`/confirmation at archive time
breaks that join silently — twice historically (868d4f0 repaired two; ca82507
repaired two more). This change makes the join a machine invariant.

## Decisions

1. **规则落点：`check_project_specs.py` 默认模式，不新开 checker**。它已是 closeout
   gate 六组件之一、CI canonical 序列在跑；新开 checker 要动 gate 清单、
   `test_project_gate` fixture、ci-governance 声明面——为一个规则不值得。规则的
   selected-change 模式（`--change`）不受影响（那是活跃 change 的准入面，归档对账是
   另一个对象）。
2. **单方向钉死（ADDED→在场），不做全量 replay**。两处真实漏 sync 均为 ADDED 方向；
   双向 replay 会把 out-of-band 改名误报成「主干多出一条无 delta 来源」+「ADDED 缺失」
   成对假红，allowlist 成本翻倍。MODIFIED 标题不钉：改名后的旧 MODIFIED 引用是历史
   事实，由 allowlist 承载（首条：Six verbs→The verb set，868d4f0）。
3. **豁免面封闭，沿用 MARKER_ALLOWLIST 形状**：后续归档 delta 的 REMOVED/RENAMED（含
   `#### FROM:` 行）= 正式退役；`DELTA_SYNC_ALLOWLIST[(cap, title)] = 理由` = out-of-band
   修复，无理由条目即红。扩表是 visible change。
4. **归档序按目录名字典序**（date-prefixed，跨日精确；同日多 change 为近似——declared
   limitation，写进 spec 与 docstring）。真实树上该近似无影响（唯一的 REMOVED 跨日）。
5. **红绿落点：治理 unittest**（`test_project_specs.py` 案例矩阵：缺失红/在场绿/退役
   豁免/allowlist 豁免/capability 缺失红），不是 checker 内 --self-test——specs checker
   无自测电池传统（那是 doc-hygiene 的形状），其测试归 unittest 套件。

## Alternatives Rejected

- **全量 replay（从空重构到现值再对账）**：否——见决策 2；且 out-of-band 修复史
  （868d4f0）无法被 replay 表达，只会逼出更多 allowlist。
- **独立 `check_delta_sync.py` + gate 扩员**：否——见决策 1 的声明面成本。
- **改 archive CLI / 包装脚本强制 --yes**：否——外部 CLI 不可改（gate docstring 明言），
  包装层是第二入口、可被绕过；守卫钉结果，不钉流程。
- **把规则塞进 check_doc_hygiene**：否——它是 docs/账本/预算的 owner，spec 结构归
  specs checker；放错 owner 会让两份 README 各自描述半截。

## Verification

治理 unittest 红（植入 ADDED 缺失 → 非零点名）→ 实现绿 → 真树
`check_project_specs.py` exit 0（86 条对账：84 直在场 + 1 REMOVED 豁免 + 1 allowlist
豁免）→ 治理套件全绿 → closeout gate 0 → strict validate → archive --yes（本 change 的
ADDED requirement 随归档进主干——规则为自己的规范归属当第一个服务对象）。
