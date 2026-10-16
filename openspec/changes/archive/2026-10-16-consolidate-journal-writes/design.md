# Design

## Context

动机见 `proposal.md` — Why。这里只记塑造形态的实测事实与约束。

**复核结果（每条都有 file:line，2026-10-16 实测）**

| 项 | 现状 | 差异 |
|---|---|---|
| `write_unanswered_questions` | `bundle_actions.py:170`，**0 调用者**，用 `atomic.atomic_write_text` | 死码 |
| gates.py 内联同件事 | `pump_parts/gates.py:96-105`，**裸 `write_text` + mkdir** | JSON 形状逐字相同；**原子性不同** |
| `_now_iso` | `bundle_actions.py:38` / `admission.py:37` / `turn.py:166` | **三份逐字相同** |
| `_journal` | `bundle_actions.py:42`（**不校验**）/ `turn.py:170`（**`.validate()`**） | **契约不同，不是纯重复** |
| `_msg_field` | `turn.py:179` / `interaction/render.py:14` | 逐字相同（noqa 注释差） |

**`JournalEntry.validate()` 的严格度**：`check_category(category)` + 时间戳非空 + event 非空
（`domain/journal_policy.py:50-56`）。统一到严格版后，**任何写未注册 category 的调用方会当场抛
`RuleViolation`**。

**三条硬约束**

1. **测试一行不改**：`tests/` 全冻结（本次的判据是既有断言，不是我新写的测试）。
2. **公共面保持**：`pump._journal` / `pump._now_iso` / `pump._msg_field` 必须继续可达（阶段 4
   的教训：双层跳转再导出会被 linter 反复删，要用显式豁免块）。
3. **`git diff --stat -- src` 只应出现本 change 声明的文件**。

## Goals / Non-Goals

**Goals:** 四类重复各收敛为一份实现；exhaustion 写入走 atomic；journal 条目与 questions 文件逐字不变；
三车道 + 门禁全绿。

**Non-Goals:** 不动 journal 词汇与 `journal_policy.py`；不动 CAS（事实 12）；不动任何测试文件。

## Decisions

### D-1｜死码复活并取代内联（而非删死码）

- **选**：删掉 `gates.py` 的内联写法，改为调用既有的 `write_unanswered_questions`。
- **为什么不是反过来删函数**：两者 JSON 形状逐字相同，但**函数那份用 atomic**。删函数 = 保留
  裸写；调用函数 = 同一件事只剩一份实现**且**那条路径终于原子。
- **代价**：exhaustion 分支少 8 行；多一次函数调用。
- **换来**：facts 文件不再可能被撕裂（`questions.json` 是失败转移前要落地的证据）。
- 备选：两部分都删、直接内联 atomic——否决：等于把"怎么写 questions"这件事继续散在调用点。

### D-2｜`_now_iso` 收敛到 `bundle/journal.py`

- **选**：`journal.py` 提供 `now_iso()`；三处 import。
- **为什么放这里**：`_now_iso` 只服务于 journal 条目的时间戳；`journal.py` 已是 journal 写入的
  owner（阶段 4 把 `tail_journal` 移入此处）。三份逐字相同 ⇒ 零语义风险。
- 备选：放 `domain/`——否决：时间戳是写入实现细节，不是领域词汇。

### D-3｜`_journal` 收敛到**严格版**，并当作探针

- **选**：`journal.py` 提供 `journal_entry(handle, category, event, detail)`，内部
  `JournalEntry(...).validate()`；`bundle_actions` 与 `turn` 都用它。
- **为什么取严格版**：宽松版看着"更安全"（不会抛），实际是**少了守卫**——`turn.py` 那条路径
  已经在享受词汇校验。取严格版让两条路径获得同等保护。
- **这是有意的探针**：若 `bundle_actions` 现有调用方写的 category/event 不合词汇，统一后套件会
  红——**那是一个真发现**（现有代码在写不合规条目），按 Deviation Register 记下并停下请裁决，
  不靠"保留宽松版"抹平。
- 备选：取宽松版——否决：那是**降低**守卫强度，且会让 `turn` 侧丢掉校验。

### D-4｜`_msg_field` 落到 `runtime/adapters/messages.py`

- **选**：新增 `runtime/adapters/messages.py` 的 `message_field()`，`turn.py` 与 `render.py` 改为 import。
- **为什么新模块**：它是 framework 消息形状的适配器（dict 或对象），两处消费者分属
  `pump_parts/`（流适配）与 `interaction/`（投影）——**同层 runtime 内的共享归 `adapters/`**，
  该包已是 framework 边界的归属（`adapters/client.py`）。
- **代价**：一个 4 行函数一个新模块 + 登记。
- **换来**：框架消息形状只有一个读法；`render.py` 不再自带一份。

### D-5｜公共面用显式再导出保持

- **选**：`pump.py` 从 `pump_parts.turn` 继续再导出 `_journal` / `_now_iso` / `_msg_field`（这些名
  在阶段 4 的公共面捕获里，且既有调用面用它们）。
- **代价**：再导出块需要 `# noqa: F401` 豁免（阶段 4 已被咬过一次）。
- **换来**：公共面零缺失。

## Risks / Trade-offs

- [统一 `_journal` 触发既有调用方的 RuleViolation] → 这正是 D-3 的探针价值；套件会红，我记偏差并
  停下请裁决（**不**改词汇表、**不**回退到宽松版来"修绿"）。
- [exhaustion 写入路径变化导致文件内容变了] → 两者 JSON 形状逐字相同（同一 `json.dumps` 参数）；
  任务里另加一次前后逐字对照。
- [新模块撞导入矩阵] → `runtime/adapters/messages.py` 只依赖标准库，消费者都在 runtime 层内；
  跑架构 checker。
- [再导出被 linter 删除] → 阶段 4 的既定做法：`__all__` + 块级 noqa。

## Migration Plan

1. `bundle/journal.py` 增 `now_iso()` 与 `journal_entry()`（严格版）。
2. `bundle_actions.py` / `admission.py` / `pump_parts/turn.py` 改 import；`pump.py` 再导出。
3. `runtime/adapters/messages.py` 新增 `message_field()`；`turn.py` 与 `render.py` 改 import。
4. `gates.py` 的 exhaustion 分支改调用 `write_unanswered_questions`。
5. 登记 `required-paths.toml`；三车道 + 门禁；公共面与 questions 文件前后对照。

**回滚**：无运行时状态；回滚 = 撤销该步 diff。
