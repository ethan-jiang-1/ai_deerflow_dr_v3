# Tasks

## 1. 三处补丁

- [x] 1.1 CONTEXT-MAP.md 补 `## Common Misreadings` 节（三条，各指向 owner）。
- [x] 1.2 change-practice.md Context Selection 节补"信代码及其测试"一行。
- [x] 1.3 deerflow-downstream.md 补 Upstream Boundaries 小节（五条 + 上游参考
  标注钉定 v2.1.0）。

## 2. 验证与归档

- [x] 2.1 change-guidance checker / doc-hygiene / closeout gate / validate
  --strict 退出码直测全绿。
- [x] 2.2 gitlink 四件套 + skill 对齐；交付记录填实。
- [x] 2.3 archive → 回写 plan C4 落判。

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记。

## Delivery Record

- **外部行为**: 三个高频误读/缺口各有成文的家：CONTEXT-MAP 误读栏（profile 同名异物、"测试绿≠质量"、engine/pump 撞名）；"指南与代码冲突时信代码及其测试"进 change-practice；上游边界五条对策进 deerflow-downstream profile（内嵌形态裁剪，上游参考标注钉定 v2.1.0）。
- **影响面**: `CONTEXT-MAP.md`、`change-guidance/core/change-practice.md`、`change-guidance/profiles/deerflow-downstream/deerflow-downstream.md` 各一小节/一行；预算顶格的根/模块 AGENTS 刻意未动。
- **实际跑了什么**: change-guidance / doc-hygiene / closeout gate / validate --strict 退出码直测全绿；gitlink `ceebf97f` 未动；skill 对齐 1.14.0。
- **未执行的检查**: 误读栏内容与各层 CONTEXT 的语义一致性靠评审（本 change 即 review 对象）；起步页未做（plan 明示可选）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者授权全程推进，对交付负最终责任。
