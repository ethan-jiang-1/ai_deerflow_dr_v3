# Tasks

## 1. Red-first tests (every rule sees red before it counts)

- [x] 1.1 Write `tests/unit/engine/test_behavior_profile.py` with the three assertion families as failing-first stubs: fixture pinning (per-tool counts / event composition / span vs declared values), degenerate-research negative (zero search/fetch calls → named violation), and machine↔register drift (the existing DECLARED_MACHINES↔quality-register sync test must cover the new entry; remove the register row → red). Verify: each seeded violation produces a named red before the implementation lands.
- [x] 1.2 Write the retained-sample consumer beside `tests/integration/test_replay_model.py`: replay `real-model-io.jsonl`'s recorded key → assert the recorded output; docstring states provenance limits (no input/model/pin/command — claims replay fidelity only). Verify: mismatching the expected output → red.

## 2. Machine and registration

- [x] 2.1 Implement `src/deerflow_deep_research/engine/behavior_profile.py`: `profile_journal(events) -> BehaviorProfile` (frozen dataclass: per-tool call counts from `model_tool_call.calls`, event-kind counts, wall-clock span from first/last `ts`, unknown-tool surfacing) plus `check_expectations(profile, expectations) -> list[str]` (pure comparisons naming violated faces; the degenerate guard "at least one search-or-fetch call" is an expectation family, not a special path). Closed known-tool vocabulary declared in the module. Zero I/O. Verify: unit tests from 1.1 turn green.
- [x] 2.2 Register the machine: one `DECLARED_MACHINES` entry (invariant states observation, never admission) + one `docs/quality-register.md` row with the evidence seam. Verify: register-drift test green with both sides present; red on either side removed.

## 3. Fixture and docs sync

- [x] 3.1 Extract the journal fixture verbatim from the richest recorded run (2026-10-05 `5bb2c343`, 34 events) into `tests/fixtures/replay/` with a provenance header (source bundle id, extraction date, verbatim note). Verify: fixture loads as jsonl; pinned profile values in the test match the recorded run exactly.
- [x] 3.2 Update `docs/testing-and-evaluation.md` ladder: row 4 ⬜未规划 → ✅ with mechanism/usage links and an honest limits note (token totals not asserted — no structured journal field; observation, not admission); row 3's "留存模型样本未被现有测试消费" note updated to name the consumer. Verify: doc-hygiene link rule green.
- [x] 3.3 Update `tests/README.md` and `tests/fixtures/README.md` registry rows: the real-model-io sample's "当前没有测试消费者" flips to name the consumer; the new journal fixture gets a row. Verify: doc-hygiene green; tables not shattered.

## 4. Receipts, archive, and ledger closeout

- [x] 4.1 Full receipts (exit codes read directly): `make verify` (deep_research_harness), `check_doc_hygiene.py` + `--self-test`, `check_project_gate.py --phase plan --change` and `--phase closeout`, `openspec validate`. Verify: all exit 0; record in Delivery Record.
- [ ] 4.2 Archive `establish-behavior-assertion-lane` (spec sync: `test-evidence` becomes a main spec), ledger ritual: the issue card `2026-10-09-behavior-assertion-eval-stack.md` closes as CLS-020 (three-README linkage, counters 19→20, Next CLS-021), root README archived-change count pinned. Verify: archive strict-validate 0; doc-hygiene green at the final revision; commits with quoted-heredoc messages.

## Deviation Register

- 1.（负例控制还原事故）register 负例控制的"还原"误用 `git restore`——把本 change
  未提交的账行一并抹掉（还原必须针对**受控编辑**，不能对未提交工作树用 git 还原）。
  重新加行后 sync 全绿；真实 exit 序列如实保留：删行 → 1（点名 behavior-profile）。
- 2.（stale pyc 假象复发）pin 负例控制红→sed 还原→仍红：等长同秒替换未失效字节码
  缓存（与 assert-replay-materialization 交付记录同款现象）；清 `__pycache__` 后绿。
  现象已在案，本次如实再记。

## Delivery Record

- **外部行为**: 替身阶梯级 4 从未规划变为在案——`test-evidence` owning main spec 落地
  （阶梯诚实边界 / 纯派生 / 观察非准入 / 样本来源诚实四组 requirement）；`behavior-profile`
  注册机器对真实 journal 的工具选择、事件构成、时长派生可断言、可红绿；留存真实模型样本
  首次有测试消费者。无运行时行为变化（准入路径、模型面、CLI 全不动）。
- **影响面**: 新增 `engine/behavior_profile.py`、`tests/unit/engine/test_behavior_profile.py`、
  `tests/fixtures/replay/real-research-journal.jsonl`（逐字提取自真实 run `5bb2c343`）、
  样本消费者测试（test_replay_model.py 增 RetainedSampleTest）、`test-evidence` spec delta；
  修改 `engine/machines.py`（一条）、`docs/quality-register.md`（一行）、
  `docs/testing-and-evaluation.md`（阶梯两行）、`tests/README.md` 与 `tests/fixtures/README.md`
  （登记行）。
- **实际跑了什么**（退出码直读，apply 工作树）: `make verify` → 0（249 tests，含新增 9：
  画像 7 + 样本消费者 2）；负例控制——register 删行 → `QualityRegisterSyncTest` exit 1
  （点名 behavior-profile 缺席）→ 还原绿；pin 篡改 9→8 → exit 1（字典断言命名字段）→
  sed 还原 + 清 pycache → 0（stale-pyc 假象见 Deviation 2）；退化/未知工具/无时间戳负例
  为在档测试（随 249 绿）；`check_doc_hygiene.py` live 0 / self-test 0；closeout 六组件 0；
  `openspec validate` valid。
- **未执行的检查**: live bundle 上的 CLI 画像（entry-surface 未动，属后续触发行）；token
  维度断言（journal 无结构化字段，spec 登记为级 4 限制）；E/F/G（CLS-017 裁决维持）；
  CI 远端序列 UNVERIFIED-until-push（仓库惯例）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并实现；驾驭者
  2026-10-09 常设授权 propose 后直接 apply→archive→提交，维护者对交付负最终责任。
