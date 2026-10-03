# Known Limitations（当前已知限制）

> 面向接手者的存续限制清单（与 change design 的 `## Alternatives` 分层不重复：
> Alternatives 记随 change 的否决取舍，此文档记**存续中的**产品已知限制）。
> 每条限制标注其来源 change 与当前处置。

| 限制 | 来源 | 处置 |
| --- | --- | --- |
| 框架 LLM 调用失败不抛异常，而是降级为一条带 `deerflow_error_fallback` 标记的正常 AI 消息——框架行为本身不变 | establish-embedded-wiring 冒烟发现 | **harness 守卫已落地（surface-llm-error-fallback）**：run engine 检测标记 → 转 `failed-resume` + terminal journal 记录 error_type，不再静默 completed；集成冒烟实证（脚本模型故意抛错→全链路 failed-resume） |
| 集成冒烟/旅程测试不在 CI 里跑（CI 无依赖安装步；unit gate 保持纯 stdlib） | establish-embedded-wiring 设计决策 1 | 有意为之并记录在案；集成 lane 经 `make smoke` 在本地同步环境运行 |

| 深研究递归上限：embedded stream 默认 100（client.py:293，per-call overrides 而非 AppConfig 顶层键）；深研究 ~10 轮工具即触顶；守卫已使其响亮失败但尚不能跑完 | harden-run-continuity 复跑发现 | 已修（pass-recursion-limit：make_stream_fn 单缝注入，实证 23→86→209 消息）|

| 深研究 checkpoint 体积：1000 步级深研究的每步快照使单 bundle 的 checkpoint.sqlite 可膨胀至 GB 级（实测 1GB/五代）| refine-slim-restart 真跑发现 | 待议：按代压实/快照频率调参（框架 database.checkpoint_delta 旋钮在配置面可调）|
| 大 bundle 上 state.json 瞬时缺失（1GB checkpoint 邻域，fail-loud StateCorruption 兜底，无静默损坏）| refine-slim-restart gen-7 尝试 | 待诊断（疑似 FS 压力）|
