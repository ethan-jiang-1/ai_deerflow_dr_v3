# Tasks: harden-backlog-next-id-guard

## 1. 红先（self-test 负例，此刻实现缺席必红）

- [x] 1.1 `check_doc_hygiene.py` self-test 增负例 A：同文件同前缀两条 "Next available"
      声明（其一为旧值）→ 断言 duplicate-declaration violation 被检出
- [x] 1.2 增负例 B：单声明但值 ≠ ∪ 推导 → 断言 disagreement violation 被检出
- [x] 1.3 运行 `python3 openspec/governance/check_doc_hygiene.py --self-test`，确认以
      "未检测"失败变红（退出码直测，记录红回执）

## 2. 转绿（实现）

- [x] 2.1 ∪ 推导抽为单一来源函数，counters 检查改用之（行为等价，现有负例仍绿）
- [x] 2.2 实现声明扫描：四个编号面 README 每文件每前缀 ≤1 条、值 == 推导；violation
      消息点名文件与冲突/不一致声明
- [x] 2.3 `python3 openspec/governance/check_doc_hygiene.py --self-test` 转绿（exit 0）；
      全树 `python3 openspec/governance/check_doc_hygiene.py` exit 0（当前树已合规）

## 3. 门禁与收口

- [ ] 3.1 `openspec validate harden-backlog-next-id-guard --strict` 退出码直测
- [ ] 3.2 `cd deep_research_harness && UV_OFFLINE=1 make verify`（本 change 不触应用，仍须绿）
- [x] 3.3 `python3 openspec/governance/check_project_gate.py --phase plan --change
      harden-backlog-next-id-guard` 退出码直测
- [x] 3.4 plan-review（control-placement 义务）：复核 Control Placement Review 表与实现
      一致（owner/evaluator/seam 三列对照 diff）
- [x] 3.5 `python3 openspec/governance/check_project_gate.py --phase closeout` 退出码直测
- [ ] 3.6 `openspec archive harden-backlog-next-id-guard`（strict validate 先行）；archive
      后核对 `openspec/specs/doc-truthfulness/spec.md` 已吸收 MODIFIED（七 scenario 在场）
- [x] 3.7 `openspec --version` 与 `.agents/skills/*/SKILL.md` 的 `generatedBy` 对齐确认
- [x] 3.8 BUG-002 关闭 ritual：`git mv _backlog/bugs/BUG-002-doc-hygiene-next-id-blindspot.md
      _backlog/_archived/_fixed_bugs/`（文件名不变）；`_fixed_bugs/README.md` 加行 +
      Next ID 不变（BUG-003）；`bugs/README.md` 删活跃行 + Next ID 不变（BUG-003）；
      `_archived/README.md` 计数 1→2、Next ID 不变（BUG-003）；卡头状态改
      `已修（harden-backlog-next-id-guard）`

## Delivery Record

- **外部行为**: declaration-layer 行为——ledger README 的 Next-ID 声明行获得两道机器
  门禁（每文件每前缀至多一条；声明值 == 归档 ∪ 活跃推导），BUG-002 漂移类永久变红；
  推导单一来源化（counters 检查与声明检查共用 `_allocated_numbers`）。
- **影响面**: `openspec/governance/check_doc_hygiene.py`（常量三件 + 推导抽函数 +
  声明扫描 + self-test 负例×2）；`openspec/specs/doc-truthfulness/spec.md`（MODIFIED
  delta，archive 吸收）；账本 README 无内容改动（当前树已合规）。
- **实际跑了什么**: （退出码直读，apply 工作树）`check_doc_hygiene.py --self-test` →
  红先 exit 1（duplicate/disagreeing not detected 两条）→ 实现后 exit 0；全树
  `check_doc_hygiene.py` → 0；`UV_OFFLINE=1 make verify` → 0（250 tests）；
  `openspec validate harden-backlog-next-id-guard --strict` → 0。
- **未执行的检查**: archive 后主 spec 吸收核对（任务 3.6 随后执行）；CI 远端序列
  UNVERIFIED-until-push。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）；
  self-test 守卫 needle 曾有一处子串假阳性（"bugs" 误配 "_fixed_bugs"），被第三道守卫
  当场抓住并已改为精确路径 needle。

## Deviation Register

- none: 实现与 design/tasks 一致——推导抽函数、声明扫描、self-test 负例均按计划落地；
  2026-10-10 同日的 ∪ 预修发生在本 change 立项前，已记录于 BUG-002 卡与 design Context，
  非本 change 任务偏差。
