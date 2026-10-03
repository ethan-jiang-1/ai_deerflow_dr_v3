# Known Limitations（当前已知限制）

> 面向接手者的存续限制清单（与 change design 的 `## Alternatives` 分层不重复：
> Alternatives 记随 change 的否决取舍，此文档记**存续中的**产品已知限制）。
> 每条限制标注其来源 change 与当前处置。

| 限制 | 来源 | 处置 |
| --- | --- | --- |
| 框架 LLM 调用失败不抛异常，而是降级为一条带 `deerflow_error_fallback` 标记的正常 AI 消息——run 会"正常完成"，失败被包装在内容里 | establish-embedded-wiring 冒烟发现 | 未修复（框架行为）；watch/journal 里该消息可见，渲染层如实显示；后续可加检测守卫识别 fallback 标记并转 failed-resume |
| 集成冒烟/旅程测试不在 CI 里跑（CI 无依赖安装步；unit gate 保持纯 stdlib） | establish-embedded-wiring 设计决策 1 | 有意为之并记录在案；集成 lane 经 `make smoke` 在本地同步环境运行 |
