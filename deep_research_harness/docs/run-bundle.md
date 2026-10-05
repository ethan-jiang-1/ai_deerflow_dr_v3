# Run Bundle：持久化合同与 artifact 权属

> 一次研究的全部持久状态以 Bundle 为单位。路径合同唯一权威是
> [domain/bundle.py](../src/deerflow_deep_research/domain/bundle.py)；本文是导航与权属表，
> 不是第二事实源。总图见 [控制地图](control-map.md)。

## 生命周期

```text
create：创建 Bundle，前台驱动运行
  -> active：run_engine 消费 stream，写 journal/checkpoint
  -> terminal：completed / cancelled / failed-resume（domain 终态规则）

refine：从终态 Bundle 创建下一代 active（写入方向，不自动执行研究）
status 发现 active 但 owner 已死：转 failed-resume
```

- 路径合同：`scopes/d_YYYYMMDD/<bundle-id>/`，`scopes/` 被 gitignore，不提交。
- **没有集中式 registry 或恢复库**：删除一个 Bundle 是永久删除，不影响其他运行。
- `state.json` 是运行状态**唯一权威**：写入使用 revision CAS 与 directory lease；
  并发/跨进程语义只有本地有限测试（不是多用户 worker 证明）。

## artifact 权属表

每个对象：谁写、是什么、能看出什么、**不能推出什么**。

| 对象 | 谁写 | 是什么 / 能看出什么 | 不能推出什么 |
| --- | --- | --- | --- |
| `state.json` | [bundle_state](../src/deerflow_deep_research/runtime/bundle_state.py) | 运行状态唯一权威：状态、generation、thread、composition、pin | completed ≠ 报告必然被 admit ≠ 研究质量达标 |
| `request/problem.txt`、`request/refine-N.txt` | bundle_actions | 原始问题与各代方向 | — |
| `checkpoint.sqlite` | 框架 checkpointer（经 [client](../src/deerflow_deep_research/runtime/client.py) 注入） | DeerFlow / LangGraph 的 thread 上下文：消息与工具结果 | 不是完整供应商原始请求/响应日志；查看需框架 checkpointer |
| `work/` | 运行工作区 | 中间产物 | 不是已接纳证据 |
| `evidence/` | [admission](../src/deerflow_deep_research/runtime/admission.py) | 通过准入的证据与 `submissions.jsonl` 哈希链 | 搜索结果**不自动物化**进 evidence；有此目录 ≠ 完整证据库 |
| `final/report-genN.md` | admission（validator 先裁决） | 通过准入的最终报告投影 | 不等于模型写的所有 sandbox 文件都进入 final |
| `diagnostics/journal.jsonl` | [run_engine](../src/deerflow_deep_research/runtime/run_engine.py) / [journal](../src/deerflow_deep_research/runtime/journal.py) | 事件时间线：聚合工具名、回答尾部摘要、subagent 事件、终态、准入 disposition | 不是每次搜索的完整参数与结果 |
| `diagnostics/assembly-snapshot.json` | [snapshot middleware](../src/deerflow_deep_research/runtime/snapshot_middleware.py) | 首次模型调用的 system prompt、可见工具、模型名、pin | 不是全部轮次上下文；不能独自证明 skill 原文实际被读取 |

## 状态 ≠ 交付 ≠ 质量

判断一次运行"完成"要**三查**，缺一不可：

1. **终态**：`state.json` 到达 completed / cancelled / failed-resume；
2. **准入结果**：validation disposition（空回答不提交，重复内容可被拒绝）；
3. **交付物**：`final/` 里存在通过准入的报告文件。

当前 run engine **先写 terminal 再提交最终报告**，因此看到 completed 的瞬间报告
可能还在准入流程中。质量达标（引用真实、覆盖充分）是第四件事，没有任何 lane
自动证明它——见 [研究过程地图](research-process.md) 的证据判断方法。

## 观察命令的分工

| 命令 | 看什么 | 不看什么 |
| --- | --- | --- |
| `status` | state 摘要、近期 journal、owner PID 存活 | 不重放事件 |
| `watch` | journal 投影直播，terminal 退出 | 不驱动研究 |
| `inspect` | journal 时间线、已接纳产物统计、装配快照 | 是投影，不补出缺失内容 |

命令语义权威：[COMMANDS](../COMMANDS.md)；操作旅程：[playbook](../playbook/run-research.md)。
测试：Bundle 落盘 → [test_bundle_runtime](../tests/unit/test_bundle_runtime.py)；
状态读取诊断 → [test_state_read_diagnosis](../tests/unit/test_state_read_diagnosis.py)；
CLI 旅程（真实框架）→ [test_cli_journey](../tests/integration/test_cli_journey.py)。
