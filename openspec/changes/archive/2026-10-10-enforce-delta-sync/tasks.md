# Tasks: enforce-delta-sync

## 1. 红：案例矩阵先行（治理 unittest）

- [x] 1.1 `openspec/tests/governance/test_project_specs.py` 新增 `DeltaSyncCompletenessTest`：
      临时树案例矩阵——(a) 归档 ADDED 缺失 → `_validate_main_specs` 非零且 stderr 点名
      change/capability/标题；(b) ADDED 在场 → 0；(c) 后续 delta REMOVED 豁免 → 0；
      (d) allowlist 对（entry-surface + Six verbs 旧标题）豁免 → 0；(e) capability 无主
      spec → 非零。Verify: 治理套件该类红（(a)(e) 两例失败），先于实现。
- [x] 1.2 负例的负例：案例 (b) 与 (c) 同树对照——证明豁免来自「退役在场」而非
      「规则沉默」。Verify: (b)/(c) 在实现前即绿（规则沉默时也 0）——矩阵对照读数
      记入回执，实现后 (a)(e) 转绿而 (b)(c) 保持绿。

## 2. 绿：规则实现

- [x] 2.1 `check_project_specs.py`：`DELTA_SYNC_ALLOWLIST`（首条 Six verbs，理由含
      868d4f0 出处）+ 分节解析（ADDED/REMOVED/RENAMED 各自标题，RENAMED 另收
      `#### FROM:` 行）+ `_delta_sync_violations(root)`（check `deltaSyncMissing` /
      `deltaSyncCapabilityMissing`，detail 点名 change、capability、标题），接入
      `_validate_main_specs` 的 violations 与 labels。docstring 声明 declared
      limitations（MODIFIED 不钉、同日归档序近似）。
      Verify: 1.1 全绿。
- [x] 2.2 真树对账：`python3 openspec/governance/check_project_specs.py` exit 0
      （86 条：84 直在场 + 1 REMOVED 豁免 + 1 allowlist 豁免——读数写回执）。
- [x] 2.3 治理 unittest 套件全绿（`python3 -m unittest discover -s openspec/tests/governance -q`）。

## 3. 注册与收口

- [x] 3.1 `openspec/governance/README.md` 的 `check_project_specs.py` 行更新（默认模式
      + delta-sync 完整性描述）。
- [x] 3.2 全套门禁：closeout gate 0、doc-hygiene 0、`openspec validate enforce-delta-sync
      --strict` 0、`make verify` 0、`make lint` 0。
- [x] 3.3 Delivery Record 回填（红绿读数 + 86 条对账现值）。

## 4. 归档与关卡

- [x] 4.1 `openspec archive enforce-delta-sync --yes`（ADDED requirement 随归档 sync 进
      doc-truthfulness 主干——规则为自身规范归属当第一个服务对象）；root README 计数
      74→75（count-pin 咬合）；归档后 `check_project_specs.py` + `check_doc_hygiene.py`
      复跑全 0。
- [x] 4.2 账本关卡（_backlog CLS-023）：`git mv issues/2026-10-10-delta-sync-guard.md
      _archived/_settled_issues/`，三处 README 联动（settled 索引行 + Next-ID、
      _archived 计数、issues 活跃行）。

## Deviation Register

- 2026-10-10：任务 1.1 矩阵首写被拼接脚本自身吃掉（append 后的去重逻辑误删 case，套件
  仍 94 条），发现后改用 edit 工具重写——损失一轮，矩阵本体无偏差。
- 2026-10-10：实现首跑 ValueError（`DELTA_SYNC_ALLOWLIST.items()` 按三元组解包，实为
  ((cap,title), 理由) 二元组）——当场修复，真树对账未受影响。
- 2026-10-10：spec 场景承诺「点名 change/capability/标题」，首实现沿既有输出形状只打印
  file+行号（detail 未输出）——补 detail 打印后达成场景；顺带让既有结构违规也输出
  detail（输出格式增强，无判定语义变化）。

## Delivery Record

- **外部行为**: 归档 delta 的 ADDED requirement 漏 sync 从此在 `check_project_specs.py` 默认模式当场红，violation 点名归档 change、capability、标题；真树现值 86 条 ADDED 对账 = 84 条直接在场 + 1 条后续 REMOVED 豁免（project-structure「Registered requirements are owned by specs」，2026-10-04 正式退役）+ 1 条 allowlist 豁免（entry-surface「Six verbs mirror…」，868d4f0 out-of-band 改名）。
- **影响面**: `openspec/governance/check_project_specs.py`（+`DELTA_SYNC_ALLOWLIST`、`_delta_section_titles`/`_main_requirement_titles`/`_delta_sync_violations`、violations 接入与 labels、detail 输出增强）、`openspec/tests/governance/test_project_specs.py`（+`DeltaSyncCompletenessTest` 五例矩阵）、`openspec/governance/README.md`（checker 行）、`openspec/specs/doc-truthfulness/spec.md`（归档 sync 的 ADDED requirement）、root README 计数 74→75、_backlog CLS-023 关卡三处 README。
- **实际跑了什么**: （退出码直读）红：治理套件 → FAILED (failures=2)（Ran 99 tests；恰 (a) 缺失红、(e) capability 缺失红两例，(b)(c)(d) 对照组绿——规则沉默期对照读数在案）；绿：治理套件 → OK (skipped=1)（Ran 99）；真树 `check_project_specs.py` → 0（13 main spec files, 0 violations）；closeout gate → 0；`make verify` → 0；`make lint` → 0；strict validate → 0。
- **未执行的检查**: none。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）。
