# Design

## Context

- 失败类别清单（pump.py + state_machine.py 源码核实，本轮盘点）：journal 终态事件六种
  ——`run_completed` / `run_cancelled` / `framework_error`（带异常类型名）/
  `llm_error_fallback`（带 error_type）/ `stop_reason`（带 reason）/
  `clarification bound exhausted`；外加被动转移——`status` 读到 active + 死 owner PID
  才转 `failed-resume`，**这一类没有终态 journal**。完成态另有 delivery 三态
  （admitted/rejected/no-answer/None）需 belt。
- 现有投影：`status`（state 摘要 + delivery 行 + 最近 5 条 journal + owner PID 存活）、
  `watch`（journal 直播投影）、`inspect`（全时间线 + admitted 统计 + snapshot）。三者
  都不分类、不指认环节、不关联证据文件。
- 六动词集合是规范冻结面（entry-surface 主 spec "exactly ... six"），加动词必须
  MODIFIED 该 requirement 并逐字携带存续文本与 scenario——delta 已按此写。
- `test_command_surface` 守卫 COMMANDS/Makefile/CLI 三处动词清单一致：新增动词会让它
  变红，这是同轮同步三处的既有机制。
- 无终态 journal 的 owner 死亡类无法在纯 journal 回放中复现，单测用构造 state
  （status=active + 死 PID）直接喂分类器——分类器的输入合同因此必须是
  （state, journal entries, diagnostics 存在性）三元组，而非只有 journal。

## Goals / Non-Goals

**Goals:**

- `diagnose` 一条命令回答：什么类别、断在哪个环节、下一步看哪个文件。
- 分类器零 I/O、零框架 import、七类互斥不碰撞、typed 进 typed 出。
- 只读边界可测：命令前后 Bundle 工件逐字节相同。

**Non-Goals:**

- 不修失败本身、不自动重试；不解析 checkpoint.sqlite；不改 status/watch/inspect 行为；
  不做统计质量评估；分类结果不回写 state（不新增 delivery 类事实）。

## Decisions

1. **分类器落 `domain/diagnosis.py`，typed 合同**：输入 = `BundleState` +
   journal entries（`JournalEntry` 列表）+ diagnostics 文件存在性表；输出 = 一个 typed
   Diagnosis（class、stage、evidence 指针列表、人类可读 detail）。分类规则是纯函数
   `classify(...) -> Diagnosis`，互斥判定顺序 = 先 terminal journal 事件、再 active+死
   PID、再 completed 未交付、active 直接"仍在运行"。domain 是对的 owner：输入全是
   domain 拥有的词汇（journal_policy/state_machine），规则纯、无 I/O；engine 保持
   准入裁决专职，不收诊断。
2. **类别与证据指针一一绑定**（从 pump 逐一对应）：
   - `model_call_failed` ← `llm_error_fallback` 事件 → 环节：DeerFlow 绑定（模型调用）
     → 看什么：journal 里该事件 detail、`diagnostics/assembly-snapshot.json`（配了什么
     模型/凭证梯）；
   - `framework_crash` ← `framework_error` → 环节：宿主运行时 → journal detail 异常名、
     `checkpoint.sqlite`（框架上下文）；
   - `framework_stopped` ← `stop_reason` → 环节：宿主运行时 → journal detail reason；
   - `clarification_exhausted` ← exhaustion 事件 → 环节：交互面（澄清预算）
     → `diagnostics/unanswered-clarifications.json`（问题原文）；
   - `cancelled` ← `run_cancelled` → 环节：操作者决定 → cancel 请求的 journal 记录；
   - `owner_died` ← active + 死 PID（无终态事件）→ 环节：运行泵进程 → `state.json` 的
     owner PID 与 thread id（去日志/进程表找）；
   - `completed_undelivered` ← `run_completed` 且 delivery None/rejected → 环节：准入
     （validator/gate）→ `diagnostics/journal.jsonl` 的 validation disposition、
     `final/` 目录有无。
3. **互斥与优先级**：terminal journal 事件优先于 state 推断（journal 是过程事实）；
   `owner_died` 只在无终态事件且 state=active 且 PID 死时判定；`completed_undelivered`
   只在 `run_completed` 且 delivery ≠ admitted 时判定（no-answer 也算未交付——诚实）。
   两条终态事件同时存在（不该发生）→ 分类器报 `ambiguous` 并列出全部事件，不猜。
4. **verb 面最小化**：`cmd_diagnose` = resolve_bundle + read_state + read_entries +
   classify + render；argparse 注册进 legal set；渲染函数进 `render.py`（诊断三行式：
   类别名、环节、证据指针列表），复用既有 phrase 风格。命令面一致性交给
   `test_command_surface` 变红驱动。
5. **集成旅程复用 raising fixture**：smoke 已有"raising model → framework fallback →
   failed-resume"的形状（test_wiring_smoke），CLI 旅程里用它跑 `create`（预期失败退出）
   然后 `diagnose` 断言 `model_call_failed` 类别与证据指针。零凭证、真 CLI 子进程。

## Alternatives

- **扩展现有 `status` 加 `--diagnose`**：否——status 的合同是"state 摘要 + 最近
  journal"，塞入分类会让一个动词两种深度；diagnose 独立动词保持六个既有动词语义零改动，
  代价是必须 MODIFIED 六动词 requirement（已在 delta 按 spec 规则逐字处理）。
- **分类器落 `engine/`**：否——engine 是确定性裁决 owner（validator/gate/verdicts），
  诊断是投影不是裁决；放 engine 会暗示分类结果有准入语义。
- **分类器直接读文件系统**：否——I/O 留在 verb 层（bundle_state/read_entries 已有
  owner），纯函数接收已读事实，单测不需要临时目录即可覆盖全部类别。
- **把 owner 死亡检测做成主动写终态**：否——那是 status 既有行为（读时转移），diagnose
  不改变写路径；分类器只把"这种状态"如实分类。

## Unresolved Questions

- 渲染的行措辞与证据指针的粒度（指目录 vs 指文件名模式）：apply 期按 render 既有风格
  校准，spec 只锁"类别 + 环节 + 证据指针"三要素。
- `ambiguous` 类是否需要专属退出码：apply 期定，倾向普通退出 0 + 文本明示（诊断是
  投影，不承载门禁语义）。
