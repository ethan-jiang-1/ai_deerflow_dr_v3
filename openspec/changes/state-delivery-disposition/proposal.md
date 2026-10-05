# Proposal: State Delivery Disposition

## Why

Phase 5 第 3 轮裁决（正交模型）："`state.json` 是运行状态唯一权威"，但它回答不了
"交付了吗"——准入结果（admitted/rejected/空回答未提交）只存在于 journal 和
final/ 文件的有无里；一次 completed 但被拒/空回答的 run，要弄清为什么没有报告
必须翻 journal。交付是 run 的一等事实，应该由 state 直接回答。进程 status 与
交付 disposition 是**两个正交事实**，分开记录（合并进终态枚举会破坏
refine-after-rejected 循环，已被裁决否决）。

## What Changes

- **`BundleState` 增两个可选字段**：`delivery`（None / `"admitted"` /
  `"rejected"` / `"no-answer"`；None = 未记录——变更前的旧状态、未完成的
  terminal、或 enrichment 写入前崩溃）与 `delivery_artifact`（admitted 时的
  相对路径，如 `final/report-gen2.md`；非 admitted 时为 None）。
- **validate 增规则**：delivery 封闭集合；admitted ⇒ artifact 非空；
  非 admitted ⇒ artifact 为 None。
- **序列化向后容错**：`from_dict` 对两个新键用 `.get()`——变更前的旧
  state.json 读取正常，delivery 读作 None（"未记录"而非错误）。
- **写入点（run_engine 完成路径）**：终态写入之后、`_submit_final_report`
  返回 disposition 信息，再经既有 CAS 路径做一次 enrichment 写（status 不变，
  仅 delivery 字段；revision 照常 +1）。空回答 → no-answer；提交 →
  ledger disposition admit/replay 映射 admitted、reject 映射 rejected（细粒度
  disposition 仍归 journal/ledger，state 只回答"交付了吗"）。
- **status 呈现合成**：`cmd_status` 增一行
  `delivery: admitted (final/report-gen2.md)` / `rejected` / `no-answer` /
  `(not recorded)`。
- **spec delta**：run-bundle "state.json is the single run-state authority"
  requirement MODIFIED——权威字段清单加入 per-generation delivery disposition，
  增一个场景（交付事实在终态后经 CAS 写入；旧状态读取为未记录）。终态规则、
  CAS/lease 语义、六动词集合**不变**。
- **文档同轮**：run-bundle.md（state 行 + "状态≠交付≠质量"改为两查 + 文件
  belt）、research-process（判断完成段）、tests/README（旅程描述）。
- **不变**：状态机转移规则、准入语义、cancel/refine、journal/ledger 合同、
  refine-after-rejected 循环（rejected 的 run 仍可 refine——正交模型的要点）。

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `run-bundle`: the state-authority requirement's enumerated field list gains the
  per-generation delivery disposition (admitted/rejected/no-answer + artifact path
  when admitted), written after the terminal write through the existing CAS path;
  one new scenario; the two original scenarios preserved verbatim.

## Impact

- 代码：`domain/state_machine.py`（字段/validate/序列化）、
  `runtime/run_engine.py`（完成路径 enrichment 写）、
  `runtime/interaction/cli.py`（status 一行）。
- 测试：test_bundle_domain（validate/roundtrip/容错）、test_run_engine
  （admitted / no-answer / rejected-duplicate 三态）、新
  `tests/unit/interaction/test_status_delivery.py`（status 行接线）、旅程
  smoke（create 与 refine 后的 status 断言 delivery 行）。
- 触发双 lane：verify（src/tests）+ smoke（cli.py/interaction/旅程）。
- 不触碰：engine/、admission 本体、config、`deerflow/`、终态规则。

## Change Focus

- **Primary module / causal owner:** `domain/state_machine.py` 的 state 合同——交付字段的语义与校验归 domain；run_engine 的 enrichment 写与 status 呈现是其 conformance 面。
- **Seam classification:** wiring — 正交事实的字段化与呈现；无认知面、无终态规则变化、无准入语义变化。
- **Question:** completed 的 run 能否让 status 一眼回答"交付了吗"——delivery 字段经既有 CAS 写入、旧状态容错读取、refine-after-rejected 不受影响？
- **Necessary adjacent/external contracts:** run-bundle（answers: state authority requirement MODIFIED 的字段清单扩展；CAS/lease 语义原样）；run-admission（answers: 提交/裁决语义不变，ledger 保留细粒度 disposition，state 只做三值投影）；entry-surface（answers: status 的呈现面加一行，六动词集合不变）。
- **Evidence seam:** 红×4（domain 字段校验、run_engine 三态、status 行、旅程 delivery 断言）先行；verify + smoke 全绿；旧 state.json 容错回归锁。
- **Not in scope:** 终态枚举变化（已裁决否决）；completed 与 admission 合并；evidence 物化（下一 change）；delivery 的历史表（per-generation 历史仍在 journal）。
- **Triggered review policies:** control-placement, workflow-outcome-review, change-admission

认知不因果：交付事实是确定性投影（ledger disposition → 三值），模型不参与。

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| 交付事实进 state（journal-only → 一等字段） | Human judgment（第 3 轮裁决正交模型；拒绝终态合并） | BundleState 字段 + validate 封闭集合；run_engine 完成路径经 CAS enrichment 写 | non-bypassable | 终态规则不受 delivery 影响（spec 明示）；旧状态读作未记录；崩溃两写之间 → None 诚实 | status 不再需要翻 journal 回答交付；三查减为两查 + belt | domain/run×3/status/旅程 红→绿 |
| 三值投影映射（admit/replay→admitted 等） | 无认知候选（确定性映射） | _submit_final_report 返回 disposition 映射 | bounded-repair | 细粒度 disposition 仍在 journal/ledger；映射规则在 docstring 与 spec 写明 | state 只回答"交付了吗"，不复制裁决细节 | run_engine 三态测试 |
| status 呈现合成 | 无认知候选 | cmd_status 一行渲染 delivery + artifact | bounded-repair | 呈现层无权威：漂移即改一行；文件存在性仍是 belt；呈现不产生新事实 | 操作者一眼读交付 | status 行接线测试红→绿 |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
|---|---|---|---|---|---|
| 终态写后 enrichment 写前崩溃 | delivery 留 None（未记录） | 三查法兜底（journal disposition + final/ 文件）；无需恢复写 | completed + delivery 未记录（诚实） | inspect 查 journal；或重新 refine | 旧状态容错回归锁 |
| enrichment 写与外部 status CAS 竞争 | CAS 语义（既有） | 外部读输即重读；enrichment 写重试一次或留 None | completed（不变） | status 再查 | 既有 CAS 冲突负例 |
| 报告被拒（重复 hash 等） | admission validator（既有） | 不恢复——拒绝是正确裁决 | completed + rejected | refine 重试（循环不受影响） | 重复负例 + refine-after-rejected 测试 |
| 空回答 | run_engine（不提交） | 不恢复 | completed + no-answer | refine 换方向 | 空回答既有测试 |
