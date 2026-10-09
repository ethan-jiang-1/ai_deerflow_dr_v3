# Tasks

## 1. Journal protocol extension (red-first)

- [x] 1.1 Extend `runtime/scripted/replay_model.py`: journal lines carry an optional `tool_calls` list (`[{name, args, id}]`); `_load` reads it with a default; `ReplayChatModel` reconstructs `AIMessage(content, tool_calls)` when present; script-mode `RecordingChatModel` captures `item["tool_calls"]` into the journal line. Verify: unit tests — a tool-call script turn records and replays whole (message carries both content and tool_calls); a legacy line (no field, the retained sample shape) replays content-only.
- [x] 1.2 Red-first negative: replaying a legacy line must not synthesize empty tool_calls, and replaying a tool-call line must carry each call's name/args/id. Verify: seeded mismatches fail naming the field.

## 2. Journaling provider (red-first, framework-free unit lane)

- [x] 2.1 Create `runtime/recording.py` (framework-free mixin) + `runtime/recording_deepseek.py` (composed provider, framework import at module scope reached only via record.yaml): `JournalingMixin` (construction resolves `DEERFLOW_RECORD_SINK`, fails loudly when unset; writes `<sink>.meta.json` once with model class, deerflow pin, argv, timestamp; `_generate` delegates to super and appends `{key, output, tool_calls?}`). Verify: `tests/integration/test_recording.py` (lane corrected from unit — langchain dependency) — unset env → loud failure; content turn → key/output line; tool-call turn → tool_calls whole; ReplayChatModel round-trips; legacy sample unaffected.
- [x] 2.2 Register `config/record.yaml` (full copy of base.yaml, model `use:` → the composed provider, header comment stating composition stays `all_real` and the env requirement). Verify: file exists, differs from base.yaml only at the seam and comments; `required-paths.toml` gains the entry (deerflow-wiring section).

## 3. Docs and registry sync

- [x] 3.1 `COMMANDS.md`: one row for the recording recipe (`DEERFLOW_RECORD_SINK=<path> make create PROBLEM="…" CONFIG=record`). Verify: command-surface guard green (no new make target, no CLI verb).
- [x] 3.2 `docs/testing-and-evaluation.md` level-3 note + `tests/README.md` limitation rows: tool_calls now journaled; usage/token still not. Verify: doc-hygiene link rule green; tables intact.

## 4. Receipts, archive, and ledger bookkeeping

- [x] 4.1 Full receipts (exit codes read directly): `make verify` (unit lane) 0; `tests.integration.test_recording` + `test_replay_model` (integration lane, venv) 0 (7 + 6 tests — the latter proving live backward compatibility against the retained legacy sample); `check_doc_hygiene.py` + `--self-test` 0; `check_project_gate.py --phase plan/closeout` 0; `openspec validate` valid; prove-it-red: journaling tamper (`if calls:` → `if False and calls:`) → exit 1 → restore → 0 (pycache cleared between same-length edits — stale-pyc discipline). The import-boundary guard caught a real level-2 relative-import bug (`..assembly` → nonexistent `deerflow_deep_research.assembly`) before any run tripped on it — fixed to `.assembly`.
- [ ] 4.2 Archive `journal-real-model-io` (deerflow-wiring delta syncs into the main spec), E card stays active with E-1 marked done in 落地关联 (E-2 real run is the next slice, triggered separately after archive). Verify: strict-validate 0; ledger hygiene green; commits with quoted-heredoc messages.

## Deviation Register

- 1.（测试车道修正）mixin 测试最初放 `tests/unit/runtime/`——单元门禁是纯 stdlib（langchain_core
  不进 unit lane，doctrine 在案），移至 `tests/integration/test_recording.py`（与 test_replay_model
  同道）；单元门禁测试数回到 249，集成道 7+6 绿。
- 2.（真实导入级 bug 被守卫逮住）`recording_deepseek.py` 初版写 `from ..assembly import`（二级
  相对导入 → 不存在的 `deerflow_deep_research.assembly`，运行时必 ImportError）——
  check_project_architecture 的 import.boundary 守卫在 apply 期抓红，改为同级 `.assembly`。

## Delivery Record

- **外部行为**: 替身阶梯级 3 获得真跑录制能力——`record` 配置（真模型 + journaling
  provider，journal 含 tool_calls、元信息 sidecar）；journal 格式向后兼容扩展（旧行
  content-only 回放不破，留存样本实证）；无运行时行为变化（base 语义位元不变；composition 仍 all_real）。
- **影响面**: 新增 `runtime/recording.py`（mixin，无框架依赖）+ `runtime/recording_deepseek.py`
  （组合 provider）+ `config/record.yaml` + `tests/integration/test_recording.py`；修改
  `runtime/scripted/replay_model.py`（journal 读写 + 可选 tool_calls + 重建）、
  `required-paths.toml`、`COMMANDS.md`、`docs/testing-and-evaluation.md`（级 3 注记）、
  `tests/README.md`（限制行 + provider 行）；E 卡（_backlog/issues/）落地关联更新。
- **实际跑了什么**（退出码直读，apply 工作树）: `make verify` → 0（249 tests）；
  `tests.integration.test_recording` → 0（7 tests）+ `test_replay_model` → 0（6 tests，含留存
  旧样本向后兼容）；负例控制——journaling 篡改 → exit 1 → 还原 → 0（pycache 清理纪律）；
  `check_doc_hygiene` live/self-test 0；closeout 六组件 0（含 import.boundary 守卫修复后）；
  `openspec validate` valid。
- **未执行的检查**: E-2 真跑（本 change 零 API 花费，录制跑在 archive 后单独触发）；
  E-3 完整图回放测试（其_own change）；usage/token 录制（边界在案）；CI 远端序列
  UNVERIFIED-until-push（仓库惯例）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并实现；
  驾驭者 2026-10-10 给出 E 立项承诺（费用+脱敏放行，终审章留人），常设授权下连续执行。
