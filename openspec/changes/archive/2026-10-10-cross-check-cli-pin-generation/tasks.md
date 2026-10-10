# Tasks: cross-check-cli-pin-generation

## 1. 红先（测试先行，checker 无此核对必红）

- [x] 1.1 `test_ci_governance.py`：`_build_tree` 增 `skills_generation` 可选参
      （默认 "1.14.0"，写 `.agents/skills/demo/SKILL.md`）；新增三负例
      （pin≠generatedBy / frontmatter 缺失 / generatedBy 歧义）与一正例（对齐绿）
- [x] 1.2 governance 套件 → 三负例断言"未检出"致红（退出码直测，记录红回执）

## 2. 转绿（checker 实现）

- [x] 2.1 `check_ci_governance.py` 实现代际交叉核对：pin 正则提取 + frontmatter
      generatedBy 收集，缺失/歧义/不一致三类 violation 点名两侧值
- [x] 2.2 governance 套件全绿（退出码直测）+ 真树 `check_ci_governance.py` → 0
      （当前树 pin = generatedBy = 1.14.0）

## 3. 门禁与收口

- [x] 3.1 `openspec validate cross-check-cli-pin-generation --strict` 退出码直测
- [x] 3.2 `check_project_gate.py --phase closeout` 退出码直测
- [ ] 3.3 `openspec archive cross-check-cli-pin-generation -y`；核对主 spec 吸收
      "CLI generation drift fails the checker" 场景

## Deviation Register

- none: 尚未开始 apply；真相源与三类违规以 design 为准，偏离就地登记。

## Delivery Record

- **外部行为**: `check_ci_governance.py` 新增代际交叉核对——workflow 的
  `@fission-ai/openspec@X` pin 与 `.agents/skills/*/SKILL.md` 的 `generatedBy` 比对，
  不一致/事实源缺失/歧义三类皆红并点名两侧值；"两处声明互相佐证即可一起陈旧"的
  1.13.1 型盲区从此 push 即红。ci-governance 主 spec 吸收
  "CLI generation drift fails the checker" 场景。
- **影响面**: `openspec/governance/check_ci_governance.py`（+3 常量、+核对段）、
  `openspec/tests/governance/test_ci_governance.py`（_build_tree +skills_generation、
  +4 用例，15 tests）、`openspec/specs/ci-governance/spec.md`（MODIFIED 吸收）。
- **实际跑了什么**: （退出码直读，apply 工作树）红先：4 新用例中 3 负例未检出 →
  exit 1（15 tests, 3 failures）；实现后套件 → 0、真树 checker → 0、strict → 0、
  closeout → 0、UV_OFFLINE verify → 0。真树首跑曾红——正则未容 frontmatter 缩进
  （fixture 无缩进 vs 真实 SKILL.md 两空格缩进），真树检查当场逮住后修正；keel/polish
  等手写技能无 generatedBy 属合法，集合语义天然容忍。
- **未执行的检查**: 远端 run 结论（随本 change 的 push 一并观测）。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）；
  只读消费 `.agents/skills/` frontmatter（用户保留区，未改未写）。
