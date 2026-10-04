# Known Limitations（当前已知限制）

> 面向接手者的存续限制清单（与 change design 的 `## Alternatives` 分层不重复：
> Alternatives 记随 change 的否决取舍，此文档记**存续中的**产品已知限制）。
> 每条限制标注其来源 change 与当前处置。

| 限制 | 来源 | 处置 |
| --- | --- | --- |
| 框架 LLM 调用失败不抛异常，而是降级为一条带 `deerflow_error_fallback` 标记的正常 AI 消息——框架行为本身不变 | establish-embedded-wiring 冒烟发现 | **harness 守卫已落地（surface-llm-error-fallback）**：run engine 检测标记 → 转 `failed-resume` + terminal journal 记录 error_type，不再静默 completed；集成冒烟实证（脚本模型故意抛错→全链路 failed-resume） |
| ~~集成冒烟/旅程测试不在 CI 里跑~~ **已解决（ci-integration-lane）**：CI 增加 setup-uv + `make smoke` 步（fixture 梯零凭证），unit gate 仍纯 stdlib | establish-entry-surface | GitHub 真机 step 级验证 success |

| 深研究递归上限：embedded stream 默认 100（client.py:293，per-call overrides 而非 AppConfig 顶层键）；深研究 ~10 轮工具即触顶；守卫已使其响亮失败但尚不能跑完 | harden-run-continuity 复跑发现 | 已修（pass-recursion-limit：make_stream_fn 单缝注入，实证 23→86→209 消息）|

| 深研究 checkpoint 体积（曾实测 1GB/五代，full 模式每步全量快照）| refine-slim-restart 真跑发现 | **已修（switch-checkpoint-delta）**：配置声明 delta 模式 + snapshot_frequency 10；短跑实测 144K vs 192K，深跑增长模式结构性移除；读路径与报告落位真跑验证。存留告诫：delta 依赖框架的 delta-history patch（langgraph 1.2.12 高于验证版 1.2.9，警告仍在 stderr 非失败）|
| 大 bundle 上 state.json 瞬时缺失（1GB checkpoint 邻域，fail-loud StateCorruption 兜底，无静默损坏）| refine-slim-restart gen-7 尝试 | 待诊断（疑似 FS 压力）|
| unit lane 网络守卫已落地（guard-unit-lane-network）：unit 测试结构性禁外联——digest 自评缺口 #1 在 v3 预防性闭合 | guard-unit-lane-network | 守卫即结构，负例在案 |
