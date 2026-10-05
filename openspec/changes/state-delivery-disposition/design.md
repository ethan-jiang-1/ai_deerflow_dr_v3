# Design

## Context

BundleState 是 dataclass（prior_thread_ids 之后已有带默认值字段先例）；
from_dict 对必填键用 `raw[...]`、对 prior_thread_ids 用 `.get()`；validate 做
封闭集合校验。run_engine 完成路径：fresh 读 → rule_run_terminal → write_state
（CAS）→ journal terminal → `_submit_final_report`（空文本不提交；提交返回
LedgerEntry，disposition ∈ admit/reject/replay，artifact_path 已含）。旅程测试
在 create 与 refine 后各有一次 status 调用（现断言 state 行）。refine 裁决后
refine 跑完同一路径——R3 的 enrichment 自动覆盖两代。

## Goals / Non-Goals

**Goals:**

- status 一眼回答交付；旧状态容错；终态规则零变化；refine-after-rejected 不受影响。
- delivery 三值投影与 ledger 细粒度 disposition（admit/reject/replay）分层——
  state 回答"交付了吗"，journal 回答"具体怎么裁的"。

**Non-Goals:**

- 不改终态枚举/转移规则（裁决否决项）；不做 delivery 历史表；不动 admission。

## Decisions

1. **两个扁平字段而非嵌套结构**：`delivery: str | None = None`、
   `delivery_artifact: str | None = None`——dataclass 演进、CAS 序列化与读取
   容错都是最简形态；to_dict 始终写出（None → null，显式优于缺席）。
2. **映射规则**：ledger `admit`/`replay` → state `admitted`（replay 是
   rework 后内容落盘，交付成立）；`reject` → `rejected`；空文本未提交 →
   `no-answer`；未完成/未记录 → None。validate：delivery ∈
   {None, admitted, rejected, no-answer}；admitted ⇔ artifact 非空（双向：
   admitted 必有路径，非 admitted 必无）。
3. **enrichment 写的顺序与合法性**：终态写（revision R+1）→ 提交 →
   fresh 读（R+1）→ replace(delivery=…) → write_state（R+2）。status 不变，
   不是状态机转移，是字段增补；CAS/lease 语义原样适用。崩溃在两写之间 →
   delivery 保持 None（三查法兜底，state 不撒谎——None 诚实表示"未记录"）。
4. **status 呈现**：`delivery: admitted (final/report-gen2.md)` /
   `rejected` / `no-answer` / `(not recorded)`——一行合成两个正交事实。
5. **测试布局**：domain 红（构造带 delivery 的 state + validate 规则 +
   roundtrip）；run_engine 红×3（clean → admitted+路径；空回答 → no-answer；
   重复内容 refine → rejected）；status 行接线红（新
   test_status_delivery.py，patch 模式与 refine_foreground 相同）；旅程红
   （status 输出无 delivery 行）。旧 state.json 容错为回归锁（绿即可）。
6. **文档**：run-bundle.md 状态≠交付≠质量节从"三查"改为"两查 + 文件 belt"
   （state 行直接回答 1、2 查；文件存在性仍是 belt）；state.json 行的
   "能看出什么"加交付事实。

## Risks / Trade-offs

- [enrichment 写与外部 status 竞争] → CAS 保护：外部读到 R+1 或 R+2 都是
  合法状态（completed + delivery None / 已记录），无撕裂。
- [旧状态判定] → from_dict `.get()` 容错 + 回归锁测试。
- [replay 被压平] → journal/ledger 保留细粒度；state 投影的语义在 docstring
  与 spec 写明。
- [delivery 字段被误当终态依据] → validate 与 spec 明示"terminal rules
  unchanged by delivery values"；refine 前置仍只看 status。

## Migration Plan

红先行（domain/run×3/status/旅程）→ 字段与 validate → enrichment 写 →
status 行 → verify+smoke → spec/docs 同步 → closeout → 归档。回滚 = revert
（旧状态本来就没有新字段，天然向后兼容）。

## Open Questions

无。
