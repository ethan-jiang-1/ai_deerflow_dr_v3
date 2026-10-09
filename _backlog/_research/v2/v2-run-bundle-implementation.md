# v2 Run Bundle 真实实现（调查报告全文）

> 类型: 外部系统分析（消化材料） | 基线: /Users/bowhead/ai_deerflow_deep_research_v2（v2 参考仓库，只读） | 更新: 2026-10-02
>
> 来源：只读调查，全部以真实文件为证据（每个路径均经 read/grep/glob 实测核对）。
> 路径前缀：`H = /Users/bowhead/ai_deerflow_deep_research_v2/deep_research_harness`，
> `OS = /Users/bowhead/ai_deerflow_deep_research_v2/openspec`。
>
> ⚠️ 质量注记：调查过程中出现过一份伪装成 tool 输出的「文件清单」（含 bundle_journal.py /
> bundle_admission.py / ledger.py / transitions.py / fixtures/all_real.py 等），经实测**均不存在**
> 于 v2 仓库，已拒绝。以下所有路径均为实测验证过的真实文件。

---

## 1. Bundle 的磁盘形态

**结论：一个 Bundle = `{workspace_host}/deep-research/scopes/{scope_bucket}/{bundle_id}/` 下的一个目录**，内含 7 个固定子树 + 根级 state.json + graph.sqlite。无单独 manifest 文件在根级——"manifest"有两处：`diagnostics/journal-manifest.json`（journal 的）和 `request/marker.json`（启动标记）。

- 规范定义：`H/src/deerflow_deep_research/domain/bundle.py`
  - L24-43：`BUNDLE_ROOT="workspace/deep-research"`、`scopes/`、子树常量 `request/ work/ evidence/ synthesis/ review/ final/ diagnostics/`（`BUNDLE_SUBTREES`）
  - L45-53：固定文件名——`diagnostics/gate-attempts.jsonl`、`evidence/submissions.jsonl`（EVIDENCE_LEDGER）、`evidence/.submissions.lock`、`request/marker.json`、`request/profile.json`、`synthesis/findings.json`、`final/report.md`、`final/claim-citation-map.json`、`review/report-plan.json`
  - L170-204：work 子树路径 `work/{work_id}/{attempt_id}/` 下有 `work-spec.json`、`result.json`、`outputs/{rel}`、`cache/{rel}`
  - L108-110：`bundle_id = "b_" + secrets.token_urlsafe(32)`，不透明、与请求/会话无关
- scope bucket：`H/src/deerflow_deep_research/runtime/bundle_lifecycle.py:330-341` `scope_bucket()` = `"s_" + b64url(sha256(长度前缀编码的 (effective_user_id, outer_thread_id)))`——只是私有容纳桶，不是公开身份
- **真实例子**（实际读取）：`H/.deep-research-demo-runs/workspace/archive/deep-research-20260925214340-412000/scopes/s_At5E…/b_Jq_iNZ03…/` 目录内容：
  ```
  state.json                      ← 生命周期唯一真相（schema_version 5, revision 2, phase_status terminal）
  graph.sqlite                    ← langgraph checkpoint（bundle 内含）
  request/marker.json             ← {bundle_id, request_digest, schema_version:1, start_message_id, state_schema_version:5}
  evidence/submissions.jsonl + .submissions.lock
  diagnostics/{events.jsonl, journal-manifest.json, run-summary.json, .journal.lock}
  work/g0_wave0_w0000/g0_wave0_w0000_a00/{work-spec.json, result.json, outputs/fixture.json}
  synthesis/ review/ final/       ← 空（fixture run 未产出；final/report.md 在别的 run 里有）
  ```
- 发布原子性：`bundle_lifecycle.py:1205-1248` `_publish_sync`——先建 `.staging-{bundle_id}`（0700）+ 7 个子树 + state.json，再 `os.replace(staging, root)` + fsync 目录；失败则 rmtree staging（从未可发现）
- 路径分类/containment：`domain/bundle.py:292-355` `resolve_bundle_contained_path` / `classify_bundle_path`（CONTENT/EVIDENCE/AUDIT/UNKNOWN）

## 2. 事件日志（Run Event Journal）

**结论：journal 在 `diagnostics/` 子树内，JSONL + 每记录带 schema_version=3 + manifest 高水位。它是"有界保留 + 诚实丢弃计数"，不是无限 append-only；它是观察证据，明确不是第二生命周期权威。**

- 实现：`H/src/deerflow_deep_research/runtime/run_observation.py`
  - L60-66：`run-summary.json`、`diagnostics/`、`events.jsonl`、`records.jsonl`（retained diagnostics）、`journal-manifest.json`、`.journal.lock`
  - L1-13 模块 docstring：「journal 是关于一个已授权 Run 的证据，绝不是第二个 Run locator」
- **事件类型清单**：`H/src/deerflow_deep_research/domain/run_observation.py:123-133` `RunEventCategory`：`admission, lifecycle, node, attempt, model_tool, validation, submit, retry, exhaustion, terminal`（共 10 种）
- append 顺序保证：`run_observation.py:655-663` `_next_sequence`——manifest `event_high_watermark+1`；L665-681 `_append_bundle_event` 校验单调且无重复、`journal_sequence_not_monotonic` 报错
- 并发保证：L593-626 `_locked_bundle_operation_sync`——64 个线程锁 stripe 按 journal 路径分桶 + `fcntl.flock(.journal.lock)`（O_NOFOLLOW、0600、拒绝 group/other 位）跨进程串行化；L1000-1027 `_atomic_write` mkstemp+fsync+os.replace
- 容量/保留：超过 `max_event_records` 按优先级驱逐（L729-763：terminal 90 > validation 80 > failure 70 > exhaustion 60 > retry 50 > finalized node 45 > lifecycle 40 > 其他 10；**admission anchor 永不驱逐**，L734-737），manifest 记 `dropped_event_count/first/last_dropped_sequence`；健康度 `JournalAvailability = complete/incomplete/unavailable` + 不完整原因 `legacy/capacity/persistence/sequence_gap`（L766-800）
- 回放/检查：`inspect()`（L453-482）返回 events+summary+diagnostics+健康度；`trace_projector.py:74,217-332` 把「checkpoint（commit 权威）+ journal（有界因果细节）」投影成 trace 页（L3 docstring 明确分工）；`run-summary.json` 只是投影（L832-872）
- 建立：`_establish`（L309-381）在任何 producer 发事实前写 admission 事件（sequence=1）
- 真实数据样例（读取的 events.jsonl）：`{"category":"admission",...,"schema_version":3,"sequence":1,...}` → node started/completed → `{"category":"terminal","outcome":"completed","sequence":35}`

## 3. 生命周期状态机

**结论：5 个公开动作 start/resume/status/cancel/refine 在 v2 全部真实存在；状态集合 6 个；状态机真相 = bundle 根的 `state.json`（revision CAS），跨进程用目录 lease 串行化。**

- 动作枚举：`H/src/deerflow_deep_research/domain/lifecycle.py:29-34` `LifecycleAction: start/resume/status/cancel/refine`；分发在 `runtime/bundle_control.py:97-158` `BundleControl.dispatch`
- 状态：`lifecycle.py:37-43` `LifecycleStatus: active/suspended/completed/stopped/cancelled/blocked`；TerminalReason（L70-76）：`completed/user_stopped/user_cancelled/rerun_exhausted/gate_blocked/internal_blocked`；LegalNextAction（L53-61）
- 状态文件：`bundle_lifecycle.py:71` `_STATE_FILENAME="state.json"`；`BundleStateStore`（L145-246）——read/validate/reduce/write，`revision` 乐观 CAS（L235-246 `state_revision_conflict`），原子写（O_EXCL 临时文件 + os.replace + fsync，L273-327）
- 活跃判定：非 terminal state = active；`pending_request_id != None` = suspended/waiting（`result_for_state` L915-979）
- 转换串行化：`runtime/bundle_transition.py` `BundleTransitionCoordinator/Lease`——对 bundle 根目录 fd 加 flock，持有 `(st_dev, st_ino)` 身份，`ensure_live()` 在每次读/写前 re-open 验证根未被删除/替换（防"删除后通过 detached fd 复活"）
- 关键操作落点：`start`（bundle_lifecycle.py:371-407，scope exclusion 下发现无 active 才发布）；`cancel`（564-604，唯一 terminal cancel 转换）；`resume`（654-672，只消费 correlated response `consume_bundle_response`）；`admit_refinement`（674-709 + `_admit_state_refinement` 1108-1151，disposition pending/applied/conflict/exhausted）；`end`（711-752，runtime 内部 terminal）；`sync_graph_progress`（754-880，graph→state 单向镜像 + stale fence `_graph_progress_is_authorized` L857-880）；`status`（882-899）
- refine 语义细节（spec `OS/specs/deep-research-harness-run-bundles/spec.md:129-307`）：方向文本 vs 无文本 continuation 两形态；一个 bundle 同时至多一个 pending refinement；重放幂等（replay receipts）；generation 上限（`FullRerunPolicy.max_rerun_generations > 2` 直接 raise，bundle_lifecycle.py:362-363）
- checkpoint：`graph.sqlite` 由 `open_graph_checkpoint`（bundle_lifecycle.py:485-539）打开，`AsyncSqliteSaver` + `RootBoundedCheckpointSaver`（64KiB 上限，`runtime/checkpoint.py`）；打开前 `_validate_current_graph_checkpoint`（L1027-1070）拒绝 legacy checkpoint

## 4. 确定性验收（validator / evidence ledger / gate）

**结论：三件套分层清晰——(a) 纯函数 validator 在 ledger 写入前跑；(b) hash 链 JSONL ledger 是唯一「候选进 Bundle」收口（单一 owner：`WorkUnitStore.commit_candidate`）；(c) gate kernel 在图路由层做 pass/repair/blocked 裁决。**

- **Validator**：`H/src/deerflow_deep_research/engine/work_units/validation.py`
  - `validate_submission_candidate`（L179-304）：纯有序检查——identity（bundle/generation/phase/work/attempt/worker_role 六元组）、spec_hash、schema_version、result-contract 注册表（L57-72 注册 wave0/wave1/targeted source-intake 合同）、**路径必须 canonical**（L220-227：result/outputs 必须精确等于 `bundle_result_path`/`bundle_output_path` 算出的路径）、artifact 逐个读取并校验 content_hash+byte_count（L142-161）、candidate_hash、同 work_id 冲突；错误码封闭集合 `SubmissionValidationCode`，按 `SUBMISSION_VALIDATION_PRECEDENCE` 排序返回
  - 调用点：`graph/components/work_units.py:210-249` `submit_candidate_if_active`——先 `require_attempt_submittable`（生命周期）→ 读 ledger → `build_validation_plan`+`read_validation_plan`（再读 artifacts）→ `validate_submission_candidate` → **有 codes 就 raise `SubmissionValidationFailure`，零码才 `commit_candidate`**
- **Evidence ledger**：`evidence/submissions.jsonl`
  - 记录模型：`domain/work_units.py:602-636` `SubmissionRecord(CandidateResult)` + scope + validator_version + passed_checks + `previous_record_hash` + `record_hash`（hash 链，L289-291 域分隔 hash）；`VALIDATOR_V1_PASSED_CHECKS`（L79）是封闭检查清单（实测样例：`artifact_hashes, candidate_hash, identity, logical_work_unique, paths, result_contract, source_refs, work_spec`）
  - 编解码：L648-690 `encode_submission_ledger`（canonical JSON、LF-only、拒绝重复 JSON key L639-645、链验证 `submission_ledger_chain_invalid`、同 attempt/work 去重）
- **收口（单一 owner）**：`runtime/work_unit_store.py:730-757` `commit_candidate` → `_commit_candidate_sync`（L1046-1116）：flock `.submissions.lock`（带 LOCK_TIMEOUT）→ 清残留 staging → 幂等检查（同 attempt 完全一致 = REPLAYED；同 work 已接受 = WORK_ALREADY_ACCEPTED）→ 新记录 hash 链接前条 → 写 staging `.submissions.{token}.tmp` → **fsync 后 `_require_live_bundle`（L776-800：重新 no-follow 遍历 bundle 根比对 (dev,ino)，防删除期间写入）→ `os.replace` 整个 ledger → fsync 目录 → 再验活**
  - admit = 追加一条链式记录；reject = validator raise（不触 ledger）；replay = 类型化幂等结果
  - 反向核对：`reconcile_parent_ledger_authority`（graph/components/work_units.py:184-207）在派发 worker 前把 checkpoint 内的 accepted refs 与 ledger 逐条重验证（含对已接受记录的 artifacts 复验 `_validate_accepted_record_artifacts` L137-181，diverged = LEDGER_CORRUPT/ACCEPTED_ARTIFACT_DIVERGED）
- **Gate**：`domain/gate.py`（GateDefinition/GateRule/GateResult，`PhaseVerdict: pass/repair/blocked/needs_human`，L16-25；规则名封闭 route labels L153-173）+ `engine/gate_kernel.py`（L32-56 verdict 推导：hard→blocked、only-degradable→degraded pass、repairable/semantic→budget 内 repair；budget [0,10] L92-115；疲劳检测 fingerprint consecutive L64-78）+ `engine/real_gates.py`（生产规则，如 wave2 searchable gap、work-unit completion）；gate 尝试审计写 `diagnostics/gate-attempts.jsonl`（domain/bundle.py:45）
- 事件对接：SUBMIT/VALIDATION 事件进 journal（RunEventCategory）

## 5. 删除语义

**结论：保证来自三层——(1) 无任何全局注册表/索引/pointer（发现=扫描目录）；(2) 所有写路径在 durable 步骤前后重验 bundle 身份；(3) spec 明文「Bundle loss … never recovered」。**

- Spec：`OS/specs/deep-research-harness-run-bundles/spec.md:309-323`「Requirement: Bundle loss makes only that Run unavailable and is never recovered」——删除/不可读 = 该 Run 永久 unavailable，不得从 checkpoint/session/binding/registry/index/cache/log/工件副本重建；新独立 Run 合法、不复用旧 id
- 无注册表证据：`bundle_lifecycle.py:1284-1311` `_discover_active_sync` 只 iterdir scope 桶（跳过 `.` 开头），逐个读 state.json，>1 active = ambiguous fail-closed；spec L84-87 明确 scope 桶「SHALL not contain a manifest, active pointer, index, session binding」
- 删除期间写保护：`work_unit_store.py:776-800` `_require_live_bundle`；`bundle_transition.py` lease `ensure_live`；`bundle_lifecycle.py:296-297`（state 写入 staging 后 re-check 根，防删除产生替代根）
- journal 不外置：`run_observation.py:274-277` `cleanup()` 恒返回空——「no observation can delete a Bundle」；唯一进程内残留是 `_PERSISTENCE_FAILURES_BY_JOURNAL` dict（L73，非持久、非 Run locator）
- 运维层教训见第 7 节（BUG-052）

## 6. 显式组成（all_real / fixture / mixed）

**结论：实现在 `src_fixtures/` 独立包 + 生产侧 `NodeAdapter(kind=REAL|FIXTURE)` 显式选择接口；fixture 替换的是「节点适配器」层（每个逻辑节点一个 factory），不是 runtime/lifecycle/store 层——bundle、ledger、validator、journal 对 fixture 与 real 完全同构（见第 1 节真实 fixture run 的 bundle）。**

- 模式枚举：`domain/lifecycle.py:64-67` `ImplementationMode: fixture/mixed/all_real`
- 选择接口：`graph/implementation_map.py:22-56` `AdapterKind` + `NodeAdapter(factory, kind, requires_gate)`；`all_real_adapters`（L59-77）是唯一生产选择；`resolve_implementations`（L88+）拒绝缺失/未知/重复 adapter；`REAL_GATED_NODES = {wave0, wave1, wave2_synthesis, final_delivery}`（L45）
- 组合根：`runtime/research.py:108-206` `ResearchGraphRecipe.from_adapters`——adapter kinds 全 real→ALL_REAL、全 fixture→FIXTURE、否则 MIXED（L127-134）；**real 依赖链强制**（L157-188：hitl1_real 需要 bootstrap_real，wave1_real 需要 wave0+targeted_evidence_real 等）；`all_real()`（L208+）是唯一公开可部署 recipe
- fixture 包：`H/src_fixtures/deerflow_deep_research_fixtures/`——每节点 `graph/nodes/{name}/adapter.py`（bootstrap/topic_planning/wave0/wave1/wave2_synthesis/targeted_evidence/hitl1/hitl2/readiness/rerun/final_delivery 共 12 个）+ `gates.py`（配对 fixture gate defs）+ `routing.py`/`scenario.py`/`work_units.py` + `scripted_real/`
- 隔离规范：`OS/specs/fixture-source-isolation/spec.md`（FSI-001..003）：生产 wheel 不含 fixture 包；生产源不得 import fixture 包；fixture 只能经 `ResearchGraphRecipe.from_adapters()` 组合；结构校验拒绝 `fake.py` 出现在生产节点包（`graph/registry.py:18,103-104`）；mixed recipe 必须 rebuild gate 选择（real ungated adapter 不能留 fixture gate）
- mode 持久化进 bundle：state.json 里 `"implementation_mode":"fixture"`（实测样例可见），由 `BundleLifecycle.start` 写入（bundle_lifecycle.py:390-396）

## 7. v2 自评：决策记录与教训（openspec 归档 change + specs）

194 个归档 change 中 bundle 相关关键记录（均实际读过）：

- **`2026-08-06-adopt-deep-research-harness-run-bundles/proposal.md`**（核心取舍）：旧设计把一个 run 摊在「会话派生 `research_id` + 应用自选 bundle 目录 + 外部 graph checkpoint + session/binding/index 记录」上，与"Bundle 是唯一可独立删除的持久真相"矛盾。该 change **retire 了 research_id**、废除 durable active pointer/binding/index/外部 checkpoint 恢复；Control Placement Review 表（L150-157）逐条写明每类决策的 owner 与「避免的复杂度」。明确否决：自动迁移/重建/外部 checkpoint 恢复被删 Bundle（Not in scope + spec「never recovered」）。
- **`2026-08-10-systemic-run-event-journal/proposal.md`**：动机——「truthful terminal outcome 丢失了解释它所需的 process facts」；journal 定位为 bounded/redacted/read-only/随 Bundle 删除、绝不成为 lifecycle 权威；「rejected request 不留 ghost journal」。schema 教训：v1 无迁移路线，v2→v3 仅限显式注册的 offline 路线，runtime reader 切换后只接受 v3（spec `run-event-journal/spec.md:63-77`）——**拒绝运行时静默迁移**。
- **`2026-08-14-converge-run-bundle-observation-authority/proposal.md`**（返工清理）：bundle 化后残留的 session/binding capability 与「state-only `BundleLifecycle.refine()` 包装」让 workbench 绕过 canonical `RefinementAdmission`——逐条迁走观察/诊断/反恢复规则后才 retire 旧 capability，并给反复活测试「种」显式违规（anti-resurrection tests with planted violations）。
- **`2026-08-19-preserve-failed-run-bundles/proposal.md`**（BUG-052 血泪）：排障脚本 `soft_bundle.py` 每次重跑前 `shutil.rmtree` 整个 deep-research 子树——「重跑本身在销毁要排障的证据」。修复：删改**归档**（archive/ 前缀不进 discovery，每名保留 3 份）。教训：删除语义留给用户/外部，操作员工具不得顺手清场。
- **Spec 内嵌教训**（`deep-research-harness-run-bundles/spec.md`）：L39-50 拒绝把 retired terminal reason（REPAIR_EXHAUSTED）映射成别的结果——旧 state 只能经注册 offline 迁移；L359-370「State 写 versioned/atomic/single-writer，corrupt State 拒绝而非 reset」。代码里大量 `@impl BUG-0xx` 注释（如 BUG-037 checkpoint serde、BUG-048 envelope、BUG-058「从 event journal 单独推 route 会错」wave1/review.py:101、BUG-064 孤儿 active state 可从 checkpoint 恢复、REG-023、REG-008 over-bound 内部 block）——每个 bug 修完都在原位留了理由与锁定测试。
- 未找到独立的 ADR 目录；`_backlog/bugs` 里未见 bundle 相关未修 bug（grep 无结果，多数已修并入归档 change）。

## 8. v3 可直接继承的（判断）

1. **Bundle 目录契约本身**：scopes/{bucket}/{bundle_id}/ + 7 子树 + state.json + graph.sqlite 的形态，路径常量集中在一个纯 domain 模块（v2 的 `domain/bundle.py` 就是单一事实源，414 行零依赖）。
2. **state.json 单一真相 + revision CAS + 目录 lease**：跨进程 flock + (dev,ino) 身份 re-check 这套「删除不可绕过」机制是 v2 最硬的部分。
3. **hash 链 evidence ledger + 单一 commit 收口 + 写前纯函数 validator + (dev,ino) 活性重验**：admit/reject/replay 三分（APPENDED/REPLAYED/WORK_ALREADY_ACCEPTED）设计干净。
4. **journal 的「诚实有界」哲学**：admission anchor 不驱逐、优先级驱逐 + dropped interval 计数、complete/incomplete/unavailable 三态——比无限 append-only 更实际。
5. **fixture = 独立包 + NodeAdapter 显式选择 + real 依赖链校验 + mode 写进 bundle state**。
6. **spec 的反模式清单**（不复活、不静默迁移、不 second authority、删除即永久）。

## 9. v3 应改掉/扔掉的（判断）

1. **journal 的"整文件重写"**：v2 每次 append 都 `_read_lines` 全量 + 重写整个 events.jsonl（run_observation.py:665-713）——O(n²) 且靠容量上限兜底；v3 可用真 append + 周期性 compaction，保留高水位校验即可。
2. **重 POSIX 手工程过多**：O_NOFOLLOW/dir_fd/mkstemp 手写遍及每个 store（run_observation 1100 行、work_unit_store 1126 行、bundle_lifecycle 1339 行）——安全收益真实但复杂度高，v3 应抽一个共享的「安全文件原子层」小模块而不是每个 store 复制。
3. **schema_version 逃生门复杂度**：v1 无迁移/v2 注册 offline 迁移/REPAIR_EXHAUSTED fail-closed 是历史包袱的产物；v3 从零开始可以单一 schema + 显式版本拒绝，不需要迁移清单机制。
4. **refine 的两形态（方向文本 vs 无文本 continuation）+ replay receipts + post-CAS 恢复例外**：spec 里占了 ~180 行、bundle_control._refine 160 行分支——为极窄的 crash-window 恢复付了很大复杂度；v3 可先只做方向形态，把 continuation 留给显式新 run。
5. **ResultCode 轰炸**：ResultCode 40+ 个、事件字段 30+ 个（record_event 33 参数）——多数为具体 bug 长出；v3 先小封闭集合，需要时再加。
6. **graph.sqlite 内嵌 bundle**：导致 64KiB bound、serde 注册、legacy checkpoint 校验等连锁复杂度（checkpoint.py、RootBoundedCheckpointSaver）；v3 若不需要 langgraph 恢复可考虑 state.json 即 checkpoint，或至少把 bound 治理独立化。

## 10. 未找到/不确定（如实记录）

- v2 无独立 ADR 目录（决策记录全在 openspec change proposal/design 里）。
- 未找到「删除 bundle」的公开 API（删除只由外部文件系统操作完成，v2 代码内无 delete-bundle 入口——这是刻意设计，spec 把删除定义为外部行为）。
- `.deep-research-demo-runs` 下的真实 bundle 是 demo/fixture run（state 里 implementation_mode=fixture），未在只读调查中找到 all_real 的 credentialed run 现场（proposal 说该验收 deferred）。
