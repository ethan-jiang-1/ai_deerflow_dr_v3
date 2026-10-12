# 开发工具

这里只放显式执行的录制/诊断工具。产品入口是 [cli.py](../cli.py)，自动测试在 [tests](../tests/README.md)，运行数据属于 Bundle。

| 工具 | 命令 | 输入 / 副作用 |
| --- | --- | --- |
| [record_stream.py](record_stream.py) | `make record-stream PROBLEM="…" CONFIG=fixture` | 真 client + fixture 模型，创建 Bundle，默认覆盖事件样本 |
| 同一录制工具 | `make record-stream PROBLEM="…" CONFIG=base` | 真模型/外部工具，消耗 API，保存未脱敏内容 |

`make` 默认 CONFIG=fixture；直接运行脚本的历史默认是 base。选择时写清梯，不凭工具名字猜是否调用外部 API。

```bash
# 只看帮助，不调用模型、不写 Bundle
python3 tools/record_stream.py --help
# 测试录制机制，写到单独位置
uv run --no-sync python tools/record_stream.py "测试问题" fixture --output /tmp/event-sample.json --runs-root /tmp/recording-bundles
```

默认输出是 [real-small-stream.json](../tests/fixtures/replay/real-small-stream.json)。录制直接覆盖选定文件，更新留存样本前确认覆盖意图并审查内容；不把录制当自动更新快照。脚本只保存事件，不经过 pump（运行泵）的终态和报告准入，因此录制结束不代表 Bundle 完成。

## 从录制到回放样本（E-2 完整图回放的工作流）

1. 真跑录制：`DEERFLOW_RECORD_SINK=<路径> make create PROBLEM="…" CONFIG=record`（真模型 + 模型 I/O journal + 元信息 sidecar；composition 仍 `all_real`）。
2. 审查与脱敏：检查 journal 与搜索语料中的用户内容和敏感数据（纪律见 [tests/README](../tests/README.md) 的录制节）。
3. 落成 fixture：按 [e2-complete-journey](../tests/fixtures/replay/e2-complete-journey/) 的形态（模型 journal + 搜索语料 + provenance sidecar）放入 `tests/fixtures/replay/`，登记消费者与来源。
4. 回放消费：[test_complete_graph_replay](../tests/integration/test_complete_graph_replay.py) 以顺序供行零凭证驱动真框架图全程（报告逐字复现 admit）。

机制与边界（usage/token 不保留、顺序供行设计）见[替身阶梯第 3 级](../docs/testing-and-evaluation.md)。

文件选择规则：用户动词放 runtime/interaction；可信装配放 runtime；行为断言放 tests；输入数据放 tests/fixtures；显式开发操作放 tools。不要建立一个同时放启动、部署、测试和录制的通用 scripts 目录。`deerflow/scripts/` 属于上游框架，与本目录职责分开。
