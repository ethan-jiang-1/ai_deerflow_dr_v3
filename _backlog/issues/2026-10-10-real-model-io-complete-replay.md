# Issue: E —— real-model-io 完整图回放（零凭证驱动完整研究旅程）

> 立卡: 2026-10-10 ｜ 状态: 推敲中 ｜ 类型: Task ｜ 毕业门: 未过 ｜ 可关闭: 否

**问题与期望结果：** CLS-017 遗留 E 项（"立项才动"）获驾驭者立项承诺（2026-10-10：费用与脱敏
均放行，脱敏终审章仍归驾驭者）。目标：录制一次真实深研究旅程的完整模型 I/O（含多轮 key 链
与录制元信息），使完整图可在零凭证下回放（create → 检索轮 → 报告 → 准入），把替身阶梯级 3
从"机制在案"推进到"真实记录接入图的旅程证明"。

**当前情况（2026-10-10 探测）：**
- `RecordingChatModel` 已支持包裹真实模型（`inner` 模式）——机制在案，未接运行时。
- **录制格式缺口**：现行 journal 只存 `{key, output}` 的 content（fixtures/README 在案
  "不保留完整 tool_calls/usage 协议"）——深研究模型轮靠 tool_calls 驱动检索，不扩展 schema
  则录完也无法回放研究行为。这是"完整图必然 ReplayMiss"的另一半根因。
- 接线缝：`config/*.yaml` 的 `use:`（base=框架真模型 `PatchedChatDeepSeek`，fixture=harness
  假模型）；`cli.py create` 的 `--config` 直传且 else 分支已把非 fixture 配置如实记
  composition=all_real；**checked-in 配置是 spec 封闭集 {base, fixture}**（deerflow-wiring
  "Configuration resolution is explicit"）——`record` 是第三份，属规范语义 delta。
- 根目录 `.env` 在（真跑凭证可用，127B/600，未读内容）；DeepSeek 价位（base.yaml
  `PatchedChatDeepSeek`）。
- 既有纪律：脱敏=录制内容入库前人工终审（fixtures/README"移除 volatile 字段不等于脱敏"）；
  录制问题选公开监管类话题（延续 EASA 先例）。

**未决问题：** E-2 研究问题待驾驭者点名（默认：公开监管类深研究主题，如 EASA UAS
合规清单调研；内容天然干净便于脱敏终审）。其余按证据自决：journal 扩展 tool_calls 字段
（向后兼容，旧行仍按 content 回放）；usage/token 仍不录（与级 4 token 边界一致）。

**下一步：** E-1 change `journal-real-model-io`（录制旋钮 + journal 协议扩展 + 红绿，零 API
花费）→ E-2 真跑录制（费用发生点）→ 机器脱敏初筛 + 驾驭者终审 → E-3 零凭证完整图回放测试
+ fixture 入库 → 本卡关闭。

## 方案与取舍

| 片 | 内容 | 谁来 |
|---|---|---|
| E-1 接线与协议 | `runtime/recording.py`（JournalingMixin + JournalingDeepSeek，`DEERFLOW_RECORD_SINK` 旋钮 + 元信息 sidecar）；journal 行扩展可选 `tool_calls` 字段（记录+回放重建 AIMessage，向后兼容）；`config/record.yaml`（composition 仍 all_real）；required-paths/COMMANDS/文档同步；deerflow-wiring delta（配置封闭集 +record） | agent（红绿，内层剧本模型，零 API） |
| E-2 真跑录制 | `DEEP_RESEARCH_RUNS_ROOT` 下录制跑：`DEERFLOW_RECORD_SINK=<path> CONFIG=record make create PROBLEM=<公开话题>`；sidecar 记 model/pin/命令/问题 | agent 触发（费用承诺已给） |
| E-2.5 脱敏 | 机器初筛（key 模式/个人信息模式扫描，命中行指给驾驭者）+ **人工终审章**（章在驾驭者） | agent 初筛 + 驾驭者终审 |
| E-3 回放落地 | journal 入库为 fixture；零凭证完整图回放测试（fixture 配置 + ReplayChatModel 吃 journal → create 全旅程 → 报告落位 → 准入）；阶梯级 3"尚无真实记录接入图"注记翻面 | agent |

**不进**：usage/token 录制（与级 4 token 边界一致——journal 无结构化字段，不伪造维度）；
F（陈述级接地）与 G（方差）维持 CLS-017 裁决；录制工具的自动脱敏（纪律在案：不存在安全
脱敏器，只有人工终审）。

## 验收标准

| 行为 | 缝类 | 通过/失败信号 | 证据 owner |
|---|---|---|---|
| 旋钮接线 | wiring | `DEERFLOW_RECORD_SINK` 未设 → 构造响亮失败；设了 → 每次 _generate 追加 journal 行 | unit |
| journal 含 tool_calls | deterministic-guardrail | 剧本内层发 tool_calls 轮 → journal 行带 tool_calls 字段；回放重建 AIMessage(content, tool_calls) | unit/integration |
| 向后兼容 | deterministic-guardrail | 旧格式行（无 tool_calls）仍按 content 回放（现存 real-model-io 样本不破） | unit |
| 配置封闭集 | wiring | `--config record` 构造走 record.yaml；composition 记 all_real；spec delta 在案 | contract test + spec |
| E-3 零凭证完整图 | deterministic-guardrail | fixture 配置 + journal → create 全旅程完成、报告经 hold point 落 final/、准入 admit；拔掉 API 凭证跑（真零凭证） | integration |

## 落地关联

change 家族：E-1 `journal-real-model-io`（本卡首个 change）→ E-3 回放测试 change。本卡在
E-3 归档后关闭（CLS-021+），去向登记。

## 关闭条件

做：E-3 change archive + 全门禁绿 + 脱敏终审章在案 + 本卡迁 `_archived/_settled_issues/`。
