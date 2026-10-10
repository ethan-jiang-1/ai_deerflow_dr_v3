# Issue: 归档 delta 的 ADDED requirement 未进主 spec 无机器守卫（漏 sync 类反复发生）

> 立卡: 2026-10-10 ｜ 状态: 已结 ｜ 类型: Task ｜ 毕业门: 已过 → enforce-delta-sync ｜ 可关闭: 是

**问题与期望结果：** 2026-10-10 fresh-agent 全库审计系统性核对 71 个归档 change 的 86 条
delta requirement，发现两条 ADDED requirement 从未落进主 spec（deerflow-wiring 的
framework-home pin、doc-truthfulness 的 root README 计数钉死）——归档 CLI 的 spec-update
确认被跳过所致。同类前科：868d4f0 曾修 entry-surface/agent-playbook 两处漏 sync。期望：
漏 sync 从「下次审计人工核对才发现」变成「归档后 checker 当场红」。

**当前情况：** 两处漏 sync 已在 ca82507 人工补齐（逐字 delta→主干）；根因路径实锤：
`openspec archive` 不带 `--yes` 时 spec 更新需交互确认，非交互上下文会直接报错跳过
（widen-doc-link-guard-scope 归档时 CLI 演示了 `--yes` 自动应用）。

**结论（做）：** 在 `check_project_specs.py`（既有 gate 组件、CI 已跑）默认模式加
delta-sync 完整性规则：归档 delta 的每个 ADDED requirement 标题必须在对应主 spec 在场；
豁免面封闭——后续归档 delta 的 REMOVED/RENAMED（正式退役）、带理由的 allowlist
（out-of-band 修复，如 868d4f0 的 Six verbs→The verb set 改名）。红先绿后进治理
unittest 套件。规范归属：doc-truthfulness ADDED requirement（checker 实现先行落地，
spec 随 change 归档 sync——本 change 自己就是这条规则的第一个服务对象）。

**方案与取舍：** 选单方向钉死（ADDED→主干在场）而非全量 replay（双向重构历史）：
两处真实漏 sync 均为 ADDED 方向，replay 会把 out-of-band 改名误报成新增/缺失对，
allowlist 成本更高；单方向 + 封闭豁免面是同一诚实度的最小切片。MODIFIED 标题不钉
（out-of-band 改名以 allowlist 承载）——declared limitation，写进 spec 与 docstring。
不新开独立 checker（避免 gate 清单/CI 声明面联动扩员）。

**落地关联：** change `enforce-delta-sync`（propose→apply 红绿→archive --yes，
2026-10-10 常设授权闭环）。

**关闭条件：** 做——验收见 change tasks（红绿回执 + 真树绿 + 全套门禁）。
