# Tasks

## 1. 写明语义

- [x] 1.1 governance README CI 门禁段补双端触发语义一句（"上游参考·语料卷二
  05"标注）。

## 2. 验证与归档

- [x] 2.1 governance checker / doc-hygiene / closeout gate / validate --strict
  退出码直测全绿；gitlink 四件套 + skill 对齐。
- [x] 2.2 交付记录填实；archive → 回写 plan C5 落判。

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记。

## Delivery Record

- **外部行为**: "契约双端触发"语义在 governance README 写明——单 job 全序列是主仓双端触发原则在本仓形态的等价实现（上游参考标注钉定 v2.1.0）。
- **影响面**: `openspec/governance/README.md` 一段一句；workflow/checker 零改动。
- **实际跑了什么**: ci-governance checker / doc-hygiene / closeout gate / validate --strict 退出码直测全绿。
- **未执行的检查**: 无新机制可验（本 change 仅写明既有结构事实）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者授权全程推进，对交付负最终责任。
