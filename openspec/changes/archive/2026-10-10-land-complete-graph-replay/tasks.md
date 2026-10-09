# Tasks

## 1. Replay providers and fixture (red-green by development failure)

- [x] 1.1 Land `runtime/replay_fixture.py`: `JourneyReplayModel` (journey-order serving, process-shared cursor, loud exhaustion) + `replay_web_search`/`replay_web_fetch` (corpus by (tool, arguments), loud misses). Verify: the integration test drives the real graph to completion (each intermediate failure was loud — ReplayMiss, the plan-marked rejection, the exhaustion error — receipts in Delivery Record).
- [x] 1.2 Land the fixture `tests/fixtures/replay/e2-complete-journey/` (model-io.jsonl + corpus.jsonl + recording.meta.json, extracted verbatim from bundle 55c35d44). Verify: 10 model lines, 28 corpus records, 0 duplicate (tool, args) pairs (measured).
- [x] 1.3 Fix `_Base.bind_tools` in `runtime/scripted/replay_model.py` (return self). Verify: the real agent chain binds without NotImplementedError; mechanism tests still green.

## 2. The proof test and docs

- [x] 2.1 Land `tests/integration/test_complete_graph_replay.py`: completed + gate lifecycle journaled + report verbatim + no plan markers + Sources-class section + ledger admit + no `$VAR` secret reference in the derived config. Verify: test passes (1 test, exit 0).
- [x] 2.2 Ladder note flip (`docs/testing-and-evaluation.md` level 3: the journey proof now exists, linked) + registry rows (`tests/README.md`, `tests/fixtures/README.md`). Verify: doc-hygiene green.

## 3. Receipts and closeout

- [x] 3.1 Full receipts: `make verify` 0, `make smoke` 0, replay test 0, `check_doc_hygiene.py` + `--self-test` 0, `check_project_gate.py --phase plan --change` and `--phase closeout` 0, `openspec validate` valid. Verify: all exit 0 (recorded in Delivery Record).
- [x] 3.2 Archive `land-complete-graph-replay`; E card `2026-10-10-real-model-io-complete-replay.md` closes as CLS-021 (three-README linkage, counters 20→21, Next CLS-022, root README count pinned). Verify: strict-validate 0; hygiene green; commits with quoted-heredoc messages.

## Deviation Register

- 1.（设计转向，测量驱动）key 匹配的旅程回放被三个环境三个首 key 的实测否决
  （e96eb2e776fa/4ce402058705/75b4270c727d——框架首轮流组装随模型配置与环境变化）；
  转向顺序供行 + 耗尽响亮 + key 留档溯源。单轮回放（ReplayChatModel）保持 key 匹配。
- 2.（中间件行过滤）summarization 中间件自有模型实例，其触发点依赖上下文尺寸——
  回放侧关闭摘要 + 供行队列过滤中段 content-only 行（续行反证=中间件调用）。诚实限制
  在案：回放的会话上下文因此不含摘要块，图结构与可观察端点（逐字报告）仍钉死。
- 3.（测试开发期两个自身 bug）首版断言 "Sources" 字面（报告用中文"来源清单"——validator
  两收，测试改宽）；deerflow_pin 传了非 40-hex 占位串（state machine 响亮拒绝，改全零）。

## Delivery Record

- **外部行为**: 替身阶梯级 3 的最后一块拼图——真实记录接入完整图的旅程证明落地：录制
  旅程（模型 journal + 搜索语料）零凭证驱动真框架图（计划→自动确认→检索→报告→准入），
  报告逐字复现，admit 在案。无运行时行为变化（测试道接线；checked-in 配置集不变）。
- **影响面**: 新增 `runtime/replay_fixture.py`、fixture 三件（e2-complete-journey/）、
  `tests/integration/test_complete_graph_replay.py`；修改 `runtime/scripted/replay_model.py`
  （`_Base.bind_tools`）、`docs/testing-and-evaluation.md`（级 3 注记翻面）、
  `tests/README.md` + `tests/fixtures/README.md`（登记行）；E 卡关闭。
- **实际跑了什么**: （退出码直读）`tests.integration.test_complete_graph_replay` → 0
  （completed + plan_proposed/plan_confirmed + 报告与录制末行逐字相等 + 无计划标记 + 来源节
  在 + ledger admit + 派生配置零 `$VAR` 引用）；`make verify` → 0；`make smoke` → 0（28）；
  开发期每次失败均响亮且留痕（ReplayMiss 点名三 key 证据、计划标记拒绝、耗尽错误）。
  脱敏：机器扫描 0 命中（key 模式/27 条公开查询/公开来源报告），驾驭者 2026-10-10 预清
  在案（E 卡与承诺记录）。
- **未执行的检查**: 真实 API（本 change 零 API——回放即零凭证的全部意义）；operator 面
  回放配置（刻意不做，测试道接线）；CI 远端序列 UNVERIFIED-until-push。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并实现；
  驾驭者常设授权下连续执行（含费用与脱敏预清），维护者对交付负最终责任。
