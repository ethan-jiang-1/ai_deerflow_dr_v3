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

- [ ] 5.1 Add `domain/outcomes.py` declaring the terminal outcomes once (event name, derived classification, human-readable line) and switch the four consumers — the pump writers, `domain/diagnosis.classify`, `interaction/render`, and the `interaction/cli` status mapping — to read it; verify the journal capture is unchanged, `make verify` exits 0, and `diagnosis.classify`'s branch chain is replaced by a table walk
- [ ] 5.2 Extend the `domain/bundle.py` declaration into the single composition table (composition -> config name, wired flag) and derive the three consumers (`assembly.config_name_for_composition`, `adapters/client.CONFIG_NAMES`, `cli` argparse choices); verify the three captured value sets are unchanged, that `assembly` still raises for the declared-but-unwired `mixed` with the same message, and that `make verify` exits 0
- [ ] 5.3 Run `make smoke` and verify exit 0 (real framework assembly plus the scripted full journey)
- [ ] 5.4 Register the new subpackage and its modules in `openspec/governance/required-paths.toml`; verify `python3 openspec/governance/check_project_architecture.py` exits 0 from the repository root

## 6. Closeout evidence

- [ ] 6.1 Prove the tests were not touched: `git diff --stat origin/master..HEAD -- deep_research_harness/tests/` is empty; record the command and its (empty) output
- [ ] 6.2 Run the full harness gate set from `deep_research_harness/`: `UV_OFFLINE=1 make verify` and `make smoke`; verify both exit 0 and record the case counts against the baseline
- [ ] 6.3 Re-verify every capture from step 1.3 and the journal sequence from step 1.2 against the post-change tree; verify all identical, and record the diffs (empty) as the zero-behaviour-change receipt
- [ ] 6.4 Verify the structural outcome: `pump.py` shrank substantially, `_drive` is at most 60 lines with at most 4 parameters, and each of the four moved responsibilities has its own module; record the measured numbers
- [ ] 6.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipt lines produced by the runner above

## Deviation Register

- none: 本 change 的边界是"位置与调用形状改变、判定语义零变化"，且"测试一行不改"是硬不变量；若 apply 期间发现某处拆分必然改变可观察行为（例如委托壳无法满足契约测试的 AST 断言、或某个 journal 事件的顺序无法保持），按 core 原则记入本表并写明裁决依据与落点，而不是改测试或静默放宽。

## Delivery Record

- **外部行为**: 待 apply 填写（预期：`make verify` 与 `make smoke` 在测试零改动下全绿；journal 事件名与顺序、终端转移、四张注册表取值集合逐字不变）
- **影响面**: 待 apply 填写（预期：`runtime/pump.py` 变薄 + 新增 `runtime/pump_parts/`（4 模块）+ `domain/outcomes.py` + `domain/bundle.py`/`assembly.py`/`adapters/client.py`/`interaction/{cli,render}.py`/`domain/diagnosis.py` 改读声明 + `bundle/journal.py` 接收 `tail_journal` + `required-paths.toml`；`tests/` 一行不改）
- **实际跑了什么**: 待 apply 填写（runner 写下命令、退出码、revision）
- **未执行的检查**: 待 apply 填写
