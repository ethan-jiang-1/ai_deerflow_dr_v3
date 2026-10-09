# Tasks

## 1. 红测试先行（deterministic guardrail 的红绿起点）

- [x] 1.1 在 `tests/unit/domain/test_bundle_domain.py` 加吸收谓词红测试（与
  `test_predicate_detects_unanswered_ask_clarification` 对称）：ask_clarification 的
  call_id 在 answered 集内 → 谓词返回该调用；不在 → 不返回；无 ask_clarification →
  空结果；并加一条负对照（谓词与 unanswered 谓词对同一 observation 的划分互斥）。
  验证：`cd deep_research_harness && UV_OFFLINE=1 python3 -m unittest
  tests.unit.domain.test_bundle_domain -v` 先红。
- [x] 1.2 在 `tests/unit/runtime/test_run_engine.py` 加吸收轮红测试（脚本梯流）：
  终态轮携带已自答的 ask_clarification（call_id 在 answered 集）→ headless 无 hook
  跑完，journal 含 `clarification_absorbed`（带问题原文），`auto_proceed_count` 不变，
  终态 completed 不变。验证：`UV_OFFLINE=1 python3 -m unittest
  tests.unit.runtime.test_run_engine -v` 先红。
- [x] 1.3 同文件加 hook 路径红测试：有 clarification hook 的 run 中出现吸收轮 →
  hook 不被该轮调用、事件照记、预算不消耗。验证：同上命令先红。
- [x] 1.4 同文件加计划相位组合红测试：计划相位轮先吸收反问、随后无标记纯文本 →
  `clarification_absorbed` 与 `plan_gate_degraded` 同轮俱在、顺序正确。验证：同上命令先红。

## 2. 实现（绿）

- [x] 2.1 在 `domain/clarification.py` 实现吸收谓词（纯函数，stdlib，与
  `unanswered_ask_clarification` 对称）。验证：1.1 的测试转绿。
- [x] 2.2 在 `runtime/pump.py` `_drive` 的 `detected` 计算之后、终态/计划分支之前，
  对每个吸收调用记 `lifecycle`/`clarification_absorbed`（`{"question": …}`）。
  验证：1.2/1.3/1.4 的测试转绿；journal category 断言（closed set）不变红。
- [x] 2.3 扩展 `PLAN_REQUEST_SUFFIX` 通道纪律措辞（提问轮只携带
  ask_clarification、计划确认只走 `<research-plan>` 标记）；`AUTO_REPLY_PREFIX` 与
  `PLAN_SKIP_MESSAGE` 字节不变。验证：钉措辞常量的既有脚本梯测试（若断言旧措辞则
  按 spec delta 更新断言并说明）+ 1.2–1.4 全绿。

## 3. 集成验证

- [x] 3.1 `cd deep_research_harness && UV_OFFLINE=1 make verify` —— 单元门禁
  exit 0 直测。
- [x] 3.2 `uv sync && make smoke` —— 集成旅程 exit 0 直测；确认现有
  `tests/integration/test_plan_journey.py` 旅程在新措辞与事件下不破。
- [x] 3.3 仓库根跑治理 checker 序列与
  `openspec validate bind-clarification-channel-discipline --strict`，退出码逐一
  直测（不许管道吞码）。
- [x] 3.4 核对 `watch`/`inspect` 渲染路径对未知事件名 `clarification_absorbed`
  通用展示（不静默吞）；若渲染器白名单化事件名，补最小改动 + 测试。
  验证：fixture bundle 上 `python3 cli.py watch <id>` exit 0 且事件可见。

## 4. 文档随 slice 落

- [x] 4.1 `docs/playbook/run-research.md` 坑节补两条：通道纪律措辞与
  `clarification_absorbed` 事件（吸收轮可观测、不耗预算、不改终态）。
  验证：文档所述行为与代码一致，同轮自查。
- [x] 4.2 若新增测试文件/资产，按 `tests/README.md` 登记规则注册。验证：登记在案。

## 5. 真梯验收（依赖驾驭者的人工步骤）

- [ ] 5.1 【人工·先于措辞评判】驾驭者跑真人 TTY 基线 run（`CONFIG=base
  make create`，仓库根 `.env` 凭证由驾驭者自备），记录：<research-plan> 标记遵从、
  是否走私计划确认进反问通道、journal 交互重建完整度。回执：bundle id + 终态行。
  （backlog plan 风险表约定：基线先行，避免无基线调参。）
- [ ] 5.2 改动落库后真梯重跑一次：验收判据 = journal 能完整重建全部交互轮（含被
  吸收反问），且不再出现走私导致的重复摆计划与预算空烧；与 5.1 基线对照给遵从率
  侧写。UNVERIFIED 项在 5.1/5.2 完成前不得宣称已验证。

## 6. Closeout 义务

- [x] 6.1 交回回执：runner 写下命令/退出码/revision，回执新于最后一次改动；
  `git status --porcelain` 干净度随回执记录。验证：回执在案。
- [x] 6.2 archive 前跑仓库根
  `python3 openspec/governance/check_project_gate.py --phase closeout` 与
  `UV_OFFLINE=1 make verify`（deep_research_harness 下）、
  `openspec validate bind-clarification-channel-discipline --strict`、
  `git diff HEAD --check`，退出码逐一记录。验证：全绿回执。
- [ ] 6.3 验收判据达成后按 `_backlog` ritual 关闭 backlog plan（CLS-018：git mv 入
  `_done/_closed_plans/`，三处 README 联动）。验证：三处 README 一致。

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记。

## Delivery Record

- **外部行为**: 反问与计划确认的通道绑定——计划相位框架消息明确"提问轮只携带
  ask_clarification、计划确认只走 <research-plan> 标记"；被框架同轮自答的反问
  （5128f695 静默吸收形状）记 journal lifecycle/clarification_absorbed（带问题
  原文），交互史可完整重建；吸收轮不耗预算、不改终态、不触发续跑、不触 hook。
- **影响面**: `domain/clarification.py`（+吸收谓词，与未答谓词对称）、
  `runtime/pump.py`（分类点记账 + 措辞扩展；AUTO_REPLY_PREFIX 字节不变）、两个
  既有测试文件（+6 测试：谓词 2 + 引擎 3 + 措辞钉 1）、playbook 坑节 2 条；
  无新测试文件，无 CLI/状态机/journal category 变更。
- **实际跑了什么**: 红证（谓词 AttributeError×2；引擎 0!=1×3；措辞钉 FAILED×1）
  → 实现 → `UV_OFFLINE=1 make verify` exit 0（242 tests）→ `make smoke` exit 0
  （15 tests）→ 治理 checker 五件 + `check_project_gate --phase plan` +
  `openspec validate --strict` 全 exit 0 → fixture bundle 上 `cli.py watch`/
  `inspect` exit 0 且 `clarification_absorbed` 可见 → apply 提交 `933842b`。
- **未执行的检查**: tasks 5.1/5.2（真人 TTY 基线 + 真梯重跑验收）未执行——UNVERIFIED，
  归驾驭者；archive 等待其完成；本机无法验证模型对新措辞的遵从率（措辞是约束
  不是强制）。
