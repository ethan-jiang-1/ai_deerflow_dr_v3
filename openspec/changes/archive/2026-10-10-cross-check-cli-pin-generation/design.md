# Design: cross-check-cli-pin-generation

## Context

三处版本事实中的两处（workflow pin、checker 常量）互证即可全绿——1.13.1 事故证明
"声明只对自身互证"是结构性盲区。真相源是 `.agents/skills/*/SKILL.md` 的
`generatedBy`（openspec CLI 再生技能时写入，即产出本仓 spec/change 的 CLI 代际）。
当前树：pin = generatedBy = 1.14.0，新规则上线即绿。

## Goals / Non-Goals

- Goals：checker 三类违规（不一致/缺失/歧义）+ 4 个测试用例（红先）+ spec delta。
- Non-Goals：修改 skills；自动 bump；其它工具链版本的交叉核对。

## Approach

1. **解析**：workflow 文本上正则 `@fission-ai/openspec@([\w.-]+)` 取 pin（唯一）；
   `Path(root/".agents/skills").glob("*/SKILL.md")` 逐文件抓 `generatedBy:\s*"?(.?*)"?`
   值集合。无 pin（marker 已拦）不重复报；重点三类：
   - generatedBy 集为空（skills 缺失/无 frontmatter）→ `generation source missing`
   - 集合 >1 → `ambiguous generation record`（点名各值）
   - pin ∉ 集合 → `generation mismatch`（点名 pin 与 recorded）
2. **红先**：`test_ci_governance.py` 增 3 负例 + 1 正例（fixture 树加
   `.agents/skills/demo/SKILL.md`）→ 全红（checker 无此核对）→ 实现转绿。
3. **fixture 改造**：`_build_tree` 增可选 `skills_generation: str | None = "1.14.0"`
   写入 demo skill——既有用例不动（默认对齐），负例显式传异值/None。

## Alternatives

- **只立卡不实现**——输在：卡是记忆，门禁是行为；该盲区已实际放过一次 1.13.1 双陈旧。
- **真相源换成 openspec CLI 本地版本（`openspec --version`）**——输在：checker 是
  零依赖 stdlib、CI 与本地都可能没有同版本 CLI 可调；frontmatter 是入库的静态事实，
  任何人任何机器读到同一答案。
- **真相源换成 changes/archive 最新归档的 CLI 版本**——输在：归档工件不记录生成 CLI
  版本，需要翻 .openspec.yaml 之外的痕迹，事实源弱于 frontmatter。

## Open Questions

none: 真相源（frontmatter）、三类违规、红先路径均定案。
