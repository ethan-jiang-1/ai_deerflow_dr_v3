# 测试输入样本

样本是被测试消费的数据。可执行断言见 [测试资产地图](../README.md)，可被 YAML 加载的模型/工具 provider 在 [runtime/fixtures](../../src/deerflow_deep_research/runtime/fixtures/__init__.py)，录制操作在 [tools](../../tools/README.md)。

| 样本 | 消费者 | 来源与局限 |
| --- | --- | --- |
| [clarification-exhaustion.json](recorded/clarification-exhaustion.json) | [渲染 golden](../unit/test_entry_surface.py) | 样本自述来自脚本 run；只锁定渲染，不执行澄清耗尽 |
| [real-small-stream.json](replay/real-small-stream.json) | [事件回放](../unit/test_event_stream_replay.py) | 留存事件形状，含外部工具内容；历史录制元信息不全，不证明事实正确 |
| [real-model-io.jsonl](replay/real-model-io.jsonl) | [留存样本消费者](../integration/test_replay_model.py)（形状契约 + 回放机制参与） | 缺原始输入/model/pin/录制命令；不能独立复核来源，不冒充完整图回放——消费点已声明，只断言可断言面 |
| [real-research-journal.jsonl](replay/real-research-journal.jsonl) | [行为画像断言](../unit/engine/test_behavior_profile.py) | 逐字提取自真实 run `5bb2c343`（2026-10-05，34 事件）的 journal；钉样画像，不断言研究质量为真 |

新增样本按消费者放 recorded（golden）或 replay（事件/模型记录）。同轮登记消费者、录制命令、配置、模型/框架 pin、revision 和用途；历史缺失就声明缺失。只留最小复现输入，提交前审查用户内容、凭证、工具结果和消息。移除 volatile 字段不等于脱敏。

自动测试不得重新录制或覆盖这些留存数据。录制工具的默认覆盖路径和显式临时输出说明见 [tools README](../../tools/README.md)。
