# Proposal: consolidate-journal-writes

## Why

CLS-025 卡上"事实 13"记着三处债，逐条复核后**全部仍然成立**：

1. **死码 + 内联重复（同一件事两份实现）**：`bundle_actions.write_unanswered_questions`
   （`bundle_actions.py:170`）**零调用者**，而 `pump_parts/gates.py:96-105` 在 exhaustion
   分支内联手写了同一件事——JSON 形状逐字相同（`{"questions": [...]}`、`ensure_ascii=False`、
   `indent=2`、结尾换行），但内联那份走**裸 `write_text`**，**绕过了 atomic**。也就是说：
   库里有原子写入器没人用，路径上却裸写一个"要么完整要么撕裂"的 facts 文件。
2. **`_now_iso` 三份**（`bundle_actions.py:38`、`admission.py:37`、`pump_parts/turn.py:166`）：
   三份**逐字相同**。
3. **`_journal` 两份、且两份不同**（这是复核才发现的关键差异）：`turn.py:170` 的版本调用
   `JournalEntry(...).validate()`，`bundle_actions.py:42` 的版本**不调用**。所以它不是"重复"，
   是**同一件事的两套契约**——一条路径校验 journal 词汇，另一条不校验。
4. **`_msg_field` 两份**（`turn.py:179`、`interaction/render.py:14`）：逐字相同（仅 noqa 注释差）。

## What Changes

- **让死码复活并取代内联**：`gates.py` 的 exhaustion 分支改为调用
  `bundle_actions.write_unanswered_questions(handle, [question])`——同一件事只剩一份实现，
  且**写入变成 atomic**（该函数本来就用 `atomic.atomic_write_text`）。
- **`_now_iso` 三份 → 一份**：落在 `runtime/bundle/journal.py`（journal 写入的既有归属，
  阶段 4 已把 `tail_journal` 放在那里）。
- **`_journal` 两份 → 一份，且取严格契约**：统一为**带 `.validate()`** 的版本。这是本 change
  唯一的语义赌注——若 `bundle_actions` 现有调用方写的 category/event 不合词汇，统一后会**当场
  抛 `RuleViolation`**。这是**有意的探针**：那说明现有代码在写不合规的 journal 条目。
  若真发生，按 Deviation Register 记下并停下请裁决，**不**以"保留宽松版"方式悄悄抹平。
- **`_msg_field` 两份 → 一份**：新增 `runtime/adapters/messages.py` 的 `message_field`
  （framework 消息形状适配器的归属层），两处消费者改为 import。
- **公共面保持**：`pump.py` 继续可达 `_journal` / `_now_iso` / `_msg_field`（测试与既有调用
  面用这些名字）；改为重新导出。

**不变量**：journal 条目内容与顺序逐字不变 · `unordered_questions` 文件内容逐字不变 ·
`make verify` 与 `make smoke` 全绿（含 252 与 30 用例数）· 公共面零缺失。

## Capabilities

### New Capabilities

<!-- none: 只合并实现位置与调用路径，不新增可观察行为或契约面。 -->

### Modified Capabilities

<!-- none: journal 词汇、写入语义、失败面都不变——**除了**内联写法变 atomic（那是把已有
     正确写法用在该用的地方，不是新增保证）。若 apply 中 `_journal` 统一触发既有调用方的
     RuleViolation，按 Deviation Register 停下请裁决。 -->

## Impact

- **改**：`runtime/pump_parts/gates.py`（exhaustion 分支改调用）· `runtime/bundle/bundle_actions.py`
  （去掉本地 `_now_iso`/`_journal`，改 import）· `runtime/bundle/admission.py`（同上）·
  `runtime/pump_parts/turn.py`（同上）· `runtime/interaction/render.py`（改用共享适配器）·
  `runtime/pump.py`（重新导出保持公共面）。
- **新增**：`runtime/adapters/messages.py`。
- **登记**：`required-paths.toml` 增新模块。
- **不动**：任何 journal 词汇与 `domain/journal_policy.py` · `deerflow/` · 测试（**测试一行不改**，
  除 `required-paths` 与可能的登记面）· CAS 空转（事实 12，走 bug 轨，非本 change）。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/bundle/journal.py`
  —— 它拥有"journal 条目怎么写"这一决定；本 change 把散落的写入助手收到它名下。
- **Seam classification:** wiring —— 实现位置与调用路径的合并；写入的**语义**（条目字段、
  原子性）不变。
- **Question:** 同一件事的三类重复（死码/内联、`_now_iso` ×3、`_journal` ×2 契约不一、`_msg_field` ×2）
  能否各自收敛为一份实现——而 journal 条目与 exhaustion 文件逐字不变、公共面零缺失、测试不改一行？
- **Necessary adjacent/external contracts:** `domain/journal_policy.py`（answers: journal 词汇与
  校验归它；本 change 不动它，取它的严格面）· `runtime/bundle/atomic.py`（answers: 原子写入的
  owner；本 change 只是终于用上它）· `tests/contract/*` 与 `tests/unit/runtime/*`（answers:
  逐字事件序列与 questions 文件的断言方；它们不改，是本 change 的判据）·
  `openspec/governance/check_project_architecture.py`（answers: 新模块的层归属与导入方向）。
- **Evidence seam:** `make verify`（252）· `make smoke`（30）· journal 序列与 exhaustion 文件的
  前后逐字对照 · `pump` 公共面捕获对照 · 架构 checker 与体积闸。
- **Not in scope:** CAS 空转（事实 12，行为正确性，走 bug 轨需授权）· `domain/journal_policy.py`
  的词汇表 · 任何测试文件 · `_msg_field` 之外的跨层适配器整理。
- **Triggered review policies:** local-context, change-admission
