# Runtime Architecture

> 骨架占位。权威边界（Run Bundle、graph、evidence、sandbox、public-control）随
> run-bundle 生命周期 change 与接线 change 充实；本文件届时成为运行时权威边界文档。

v3 的方向性事实（详见根目录 boundary plan）：

- 研究认知引擎 = DeerFlow 原生能力：lead agent 加载 `deep-research` skill，按需派生
  subagent；框架侧没有静态研究图。
- Harness 保留：Run Bundle 生命周期（start/resume/status/cancel/refine）、确定性控制
  边界（validator / evidence ledger / gate）、显式组成（`all_real` / `fixture` / `mixed`）、
  可观察可操作。
- DeerFlow 是宿主运行时，不 import 本包；接线形态（反射工具 / controller skill / 薄外层）
  由首个接线 change 定义。
