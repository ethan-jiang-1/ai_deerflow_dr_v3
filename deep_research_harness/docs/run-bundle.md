# Run Bundle：持久化合同与 artifact 权属

> 一次研究的全部持久状态以 Bundle 为单位。路径合同唯一权威是
> [domain/bundle.py](../src/deerflow_deep_research/domain/bundle.py)；本文是导航与权属表，
> 不是第二事实源。总图见 [控制地图](control-map.md)。

## 生命周期

```text
create：创建 Bundle，前台驱动运行
  -> active：run_engine 消费 stream，写 journal/checkpoint
  -> terminal：completed / cancelled / failed-resume（domain 终态规则）

refine：从终态 Bundle 创建下一代并前台跑完（消息 = 该代方向文档，owner = 调用进程）
status 发现 active 但 owner 已死：转 failed-resume
```

- 路径合同：`runs/d_YYYYMMDD/<bundle-id>/`（日期桶按 **UTC** 分组——本地时区晚间
  创建的 run 会落在"昨天"的桶里，找新 bundle 用 mtime 或 status 的 thread id），
  根是**仓库根的 `runs/`**（应用子树
  之外，`deep_research_harness/` 内不存运行数据）；`runs/` 被 gitignore，不提交。
  环境变量 `DEEP_RESEARCH_RUNS_ROOT` 可重定向根（测试/工具/非默认 checkout）。
  旧数据曾位于应用内 `scopes/`，已整体迁移；Bundle 记录不含绝对路径，搬移后照常可读。
- **没有集中式 registry 或恢复库**：删除一个 Bundle 是永久删除，不影响其他运行。
- `state.json` 是运行状态**唯一权威**：写入使用 revision CAS 与 directory lease；
  并发/跨进程语义只有本地有限测试（不是多用户 worker 证明）。

## artifact 权属表

每个对象：谁写、是什么、能看出什么、**不能推出什么**。

| 对象 | 谁写 | 是什么 / 能看出什么 | 不能推出什么 |
| --- | --- | --- | --- |
| `state.json` | [bundle_state](../src/deerflow_deep_research/runtime/bundle/bundle_state.py) | 运行状态唯一权威：状态、generation、thread、composition、pin、**交付 disposition**（admitted+路径/rejected/no-answer；None=未记录） | completed ≠ 质量达标；delivery 未记录（旧状态/写入前崩溃）仍需 belt 检查 |
| `request/problem.txt`、`request/refine-N.txt` | bundle_actions | 原始问题与各代方向 | — |
| `checkpoint.sqlite` | 框架 checkpointer（经 [client](../src/deerflow_deep_research/runtime/adapters/client.py) 注入） | DeerFlow / LangGraph 的 thread 上下文：消息与工具结果 | 不是完整供应商原始请求/响应日志；查看需框架 checkpointer |
| `work/` | 运行工作区 | 中间产物 | 不是已接纳证据 |
| `evidence/` | [admission](../src/deerflow_deep_research/runtime/bundle/admission.py) | 通过准入的证据与 `submissions.jsonl` 哈希链 | 搜索结果**不自动物化**进 evidence；有此目录 ≠ 完整证据库 |
| `final/report-genN.md` | admission（validator 先裁决） | 通过准入的最终报告投影 | 不等于模型写的所有 sandbox 文件都进入 final |
| `diagnostics/journal.jsonl` | [run_engine](../src/deerflow_deep_research/runtime/run_engine.py) / [journal](../src/deerflow_deep_research/runtime/bundle/journal.py) | 事件时间线：聚合工具名、回答尾部摘要、subagent 事件、终态、准入 disposition | 不是每次搜索的完整参数与结果 |
| `diagnostics/assembly-snapshot.json` | [snapshot middleware](../src/deerflow_deep_research/runtime/adapters/snapshot_middleware.py) | 首次模型调用的 system prompt、可见工具、模型名、pin | 不是全部轮次上下文；不能独自证明 skill 原文实际被读取 |
| `diagnostics/searches/` | [search_log](../src/deerflow_deep_research/runtime/bundle/search_log.py) | 每次 web_search/web_fetch 的可直读记录：query/URL + 完整结果 + 时间戳（`gen{N}-{seq}-{tool}.json`，call_id 去重） | 是过程诊断不是已接纳证据；引用复核的物理基础，但不自动比对真实性 |

## 一次 run 的证据关联

同一 Bundle 目录 + `state.json` 的 `thread_id` 是全部关联键——文件之间没有
机器外键，靠目录归属与 journal 条目对齐。按时间顺序走一遍：

```text
state.json（thread_id、composition、pin、终态）
  → diagnostics/assembly-snapshot.json   这次装配了什么（模型、可见工具、pin）
  → checkpoint.sqlite                    按 thread 存的完整消息/工具结果
  → diagnostics/searches/                每次搜索/抓取的可直读记录（query + 完整结果）
  → diagnostics/journal.jsonl            事件时间线：tool 调用、subagent、
                                         终态、admission disposition
  → evidence/submissions.jsonl           提交哈希链（可验证完整性）
  → final/report-genN.md                 通过准入的报告投影
```

每步能推出 / 不能推出什么：

| 走到这一步 | 能推出 | 不能推出 |
| --- | --- | --- |
| state.json | 状态、generation、thread、composition、pin | 质量；报告是否已被 admit |
| assembly-snapshot | 本次可见工具与模型、prompt 首帧 | skill 原文实际被读取 |
| checkpoint | 实际消息流与工具结果 | 完整供应商请求/响应日志 |
| journal | 事件顺序、准入 disposition、终态原因 | 每次搜索的完整参数 |
| submissions 链 | 提交内容的完整性与顺序 | 未提交内容（搜索不自动物化） |
| final | 通过准入的交付物 | 质量、未采纳的 sandbox 文件 |

`inspect` 是把以上一次看全的入口（journal 时间线 + 已接纳统计 + 装配快照）；
判断"完成"仍需三查（下节），判断"质量"需真实梯 + 人工评审。

## 状态 ≠ 交付 ≠ 质量

判断一次运行"交付了吗"主要**两查 state**（正交事实已在 state 里）：

1. **终态**：`state.json` 的 status 到达 completed / cancelled / failed-resume；
2. **交付行**：`delivery` 字段——admitted（含报告路径）/ rejected / no-answer；None = 未记录（变更前旧状态或写入前崩溃），此时用 belt：journal 的 validation disposition + `final/` 文件有无。

当前 run engine **先写 terminal 再提交最终报告**，因此看到 completed 的瞬间报告
可能还在准入流程中。质量达标（引用真实、覆盖充分）是第四件事，没有任何 lane
自动证明它——见 [研究过程地图](research-process.md) 的证据判断方法。

## 观察命令的分工

| 命令 | 看什么 | 不看什么 |
| --- | --- | --- |
| `status` | state 摘要、近期 journal、owner PID 存活 | 不重放事件 |
| `watch` | journal 投影直播，terminal 退出 | 不驱动研究 |
| `inspect` | journal 时间线、已接纳产物统计、装配快照 | 是投影，不补出缺失内容 |

命令语义权威：[COMMANDS](../COMMANDS.md)；操作旅程：[playbook](playbook/run-research.md)。
测试：Bundle 落盘 → [test_bundle_runtime](../tests/unit/runtime/test_bundle_runtime.py)；
状态读取诊断 → [test_state_read_diagnosis](../tests/unit/runtime/test_state_read_diagnosis.py)；
CLI 旅程（真实框架）→ [test_cli_journey](../tests/integration/test_cli_journey.py)。
