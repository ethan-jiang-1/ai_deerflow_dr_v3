# Tasks

## 1. Baseline and the turn-consumption module

- [x] 1.1 Record the baseline: from `deep_research_harness/`, run `UV_OFFLINE=1 make verify` and `make smoke`; verify both exit 0 and record the case counts; from the repository root verify `git status --porcelain=v1 --untracked-files=all` is empty
- [x] 1.2 Capture the pre-change journal event sequence for one driven run (reuse the existing unit fixture that drives `pump.run_research` with scripted events) into `/tmp/pump-before/journal-events.txt`; verify the capture is non-empty and lists event names in order
- [x] 1.3 Capture the pre-change public surface: `python3 -c "from deerflow_deep_research.runtime import pump; print(sorted(n for n in dir(pump) if not n.startswith('__')))"` plus the two registry value sets (`bundle.COMPOSITIONS`, `client.CONFIG_NAMES`) and the CLI `--config` choices into `/tmp/pump-before/`; verify each capture is non-empty
- [x] 1.4 Add `runtime/pump_parts/__init__.py` and `runtime/pump_parts/turn.py` with a frozen `TurnOutcome` dataclass (tool_calls, answered, stop_reason, fallback_error_type, final_text) and move `_consume_turn` into it, returning `TurnOutcome`; verify `make verify` still exits 0 (the call site adapts in the same step)
- [x] 1.5 Verify the turn module preserves behaviour: re-capture the journal event sequence through the same fixture and diff it against `/tmp/pump-before/journal-events.txt`; verify identical, and verify `make smoke` exits 0

## 2. Gate steps out of the drive loop

- [x] 2.1 Move the plan-gate branch out of `_drive` into `pump_parts/gates.py` as `plan_gate_step(...)`, preserving every journal entry name, order, and the plan/amend/skip/degrade branches verbatim; verify `make verify` exits 0
- [x] 2.2 Move the clarification branch into the same module as `clarification_step(...)`, preserving the absorbed/asked/answered/declined/auto-continuation/exhaustion branches and their journal entries verbatim; verify `make verify` exits 0 and the journal capture is unchanged
- [ ] 2.3 Reduce `_drive` to a loop that calls the two steps plus a `_finish` helper; verify `_drive` is at most 60 lines and takes at most 4 parameters, and that `make smoke` exits 0  ⚠ 部分完成：_drive 51 行（≤60 达标），但仍 8 个参数（目标 ≤4）——参数收窄留下一步。

## 3. Delivery module behind contract-locked shells

- [x] 3.1 Move the delivery implementation into `pump_parts/deliver.py` (`submit_final_report`, `record_delivery`) and leave `_record_delivery` / `_submit_final_report` in `pump.py` as one-line delegating shells that keep calling each other by those names; verify `make verify` exits 0 (the contract test parses `runtime/pump.py` for exactly those names and the call between them)
- [x] 3.2 Add a comment on each shell naming the contract test and line range that pins it, so a later maintainer does not "de-duplicate" them away; verify the shells are one call each and that `python3 -m unittest tests.contract.test_entry_chain` (via the suite) still exits 0
- [x] 3.3 Verify the journal capture and the public-surface capture are both unchanged after the move

## 4. Watch tool leaves the pump

- [x] 4.1 Move `tail_journal` into `runtime/bundle/journal.py` and re-export it from `pump.py`; verify `grep -n "def tail_journal"` finds it once (in `bundle/journal.py`) and that `pump.tail_journal` resolves, with `make verify` exiting 0
- [x] 4.2 Verify `interaction/cli.py`'s watch command still works through the re-export by running `make smoke` and confirming exit 0

## 5. One declaration each for terminal outcomes and compositions

- [x] 5.1 Add `domain/outcomes.py` declaring the terminal outcomes once (event name, derived classification, human-readable line) and switch the four consumers — the pump writers, `domain/diagnosis.classify`, `interaction/render`, and the `interaction/cli` status mapping — to read it; verify the journal capture is unchanged, `make verify` exits 0, and `diagnosis.classify`'s branch chain is replaced by a table walk
- [x] 5.2 Extend the `domain/bundle.py` declaration into the single composition table (composition -> config name, wired flag) and derive the three consumers (`assembly.config_name_for_composition`, `adapters/client.CONFIG_NAMES`, `cli` argparse choices); verify the three captured value sets are unchanged, that `assembly` still raises for the declared-but-unwired `mixed` with the same message, and that `make verify` exits 0
- [x] 5.3 Run `make smoke` and verify exit 0 (real framework assembly plus the scripted full journey)
- [x] 5.4 Register the new subpackage and its modules in `openspec/governance/required-paths.toml`; verify `python3 openspec/governance/check_project_architecture.py` exits 0 from the repository root

## 6. Closeout evidence

- [x] 6.1 Prove the tests were not touched: `git diff --stat origin/master..HEAD -- deep_research_harness/tests/` is empty; record the command and its (empty) output
- [x] 6.2 Run the full harness gate set from `deep_research_harness/`: `UV_OFFLINE=1 make verify` and `make smoke`; verify both exit 0 and record the case counts against the baseline
- [x] 6.3 Re-verify every capture from step 1.3 and the journal sequence from step 1.2 against the post-change tree; verify all identical, and record the diffs (empty) as the zero-behaviour-change receipt
- [x] 6.4 Verify the structural outcome: `pump.py` shrank substantially, `_drive` is at most 60 lines with at most 4 parameters, and each of the four moved responsibilities has its own module; record the measured numbers
- [x] 6.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines produced by the runner above

## Deviation Register

- 偏差 1（apply 于步骤 2.3，未完成项如实登记）：`_drive` 拆为具名步骤后**行数达标（131 → 51）但参数仍 8 个**（目标 ≤4）。参数收窄要引入"回合上下文"包（handle/stream_fn/hooks/recorder 打包），会改变 `run_research` → `_drive` 的调用形状——而该形状目前没有被任何契约测试钉住，属可做的重构；本轮上下文不足以在不破坏已验证状态的前提下完成，故**留在原地并显式记为未完成**，而不是把目标降级成"行数达标即可"。
- 偏差 2（apply 期过程记录，如实留痕）：契约锁定（`tests/contract/test_entry_chain.py` 要求 `pump.py` 里 `_record_delivery` 调 `_submit_final_report`、且后者体内出现 `submit_artifact`）与"测试零改动"叠加，使交付实现**不能整体移出** `pump.py`。试过用关键字参数把调用点交给壳（契约测试只收集调用点的函数名，故不被接受），最终形态是：两个壳各自携带被 pin 的那次调用，壳再把 ledger 条目交给 `pump_parts/deliver.record_delivery` 做状态富化——hold point 既不绕过也不重复调用。
- 偏差 3（apply 期过程记录）：`_drive` 重写引入**死循环两次**（计划闸降级时该掉入收尾却写成继续；`continue` 前忘清 `awaiting_plan`）与**状态陈旧一次**（澄清步推进计数未回传，触发非法转移），全部由单元测试与超时当场抓红；修法是"每轮从 bundle 重读状态、`_finish` 只以 bundle 为事实源"。
- 偏差 4（apply 期过程记录）：一次误操作把 `_record_delivery`/`_submit_final_report` 复制进 `turn.py` 又删掉，导致 `pump.py` 一度缺名（契约测试与 24 个错误抓出）；另有一次按旧行号切片导致跨函数污染。教训：跨文件搬移必须用 AST 定位，且拼接后立刻跑全量门禁。
- 偏差 5（apply 于步骤 5.2，探针两次抓红）：组合注册表派生先混入未接线的 `mixed`（集合错），修正后顺序又变（`('fixture','base','record')` vs 基线 `('base','fixture','record')`）——同一逐字对照探针两次抓出，最终取字母序恢复逐字一致。
- none: 除上述五项外无其他设计偏离。



## Delivery Record

- **外部行为**: `make verify`（251 tests）与 `make smoke`（30 tests）**在不改任何测试文件的前提下全绿**——`git diff --stat origin/master..HEAD -- deep_research_harness/tests/` 为空，是本 change 最硬的一条证据 · journal 事件名与顺序逐字不变（一次受驱动运行的 6 条序列与基线完全一致）· 终端转移结果不变（诊断分类与事故用例全绿）· 四张组合注册表的取值集合与**顺序**逐字等于基线（`COMPOSITIONS` 与 `CONFIG_NAMES` 逐字对照）· pump 模块公共面零缺失、两个公共签名不变 · CLI `--config {base,fixture,record}` 与 `mixed` 的抛错文案不变。
- **影响面**: `runtime/pump.py` 450 → 228 行 · 新增 `runtime/pump_parts/`（`turn.py` 302 / `gates.py` 111 / `deliver.py` 38 / `__init__.py` 9）· 新增 `domain/outcomes.py`（7 个结局的唯一声明）· `domain/bundle.py`（组合声明）、`runtime/assembly.py`、`runtime/adapters/client.py`、`runtime/interaction/{cli,render}.py`、`domain/diagnosis.py` 改为读声明 · `runtime/bundle/journal.py` 接收 `tail_journal`（+25 行）· `required-paths.toml` 增 1 包目录 + 5 个文件 · **`tests/` 一行未改** · 无 spec 改动（`skip_specs: true`）。
- **实际跑了什么**: `UV_OFFLINE=1 make verify` exit 0（Ran 251 tests）· `make smoke` exit 0（Ran 30 tests）· journal 捕获逐字 diff 通过（基线与终态各一次）· 公共面/签名/注册表三份捕获逐字复验通过 · `git diff --stat origin/master..HEAD -- deep_research_harness/tests/` 为空 · 架构 checker exit 0 · 体积闸 exit 0 · 登记变红实测：移走 `pump_parts/deliver.py` → `ERROR [path.missing] required file is missing: …` exit 1 → 恢复 exit 0 · 治理套件 exit 0（157 用例）。
- **未执行的检查**: 6.4 要求的"`_drive` 参数 ≤4"**未达成**（现 8 个参数，行数 51 已达标）——见 Deviation Register 偏差 5，留下一步 · 远端 CI Governance Gate 未跑（本地领先远端 6 个提交，归档后一并推送复核）· 真实模型梯未跑（本 change 是 wiring 重组，窄证据政策下不整跑）· `make smoke` 只覆盖脚本模型车道，真模型研究质量不在本 change 承诺内。
