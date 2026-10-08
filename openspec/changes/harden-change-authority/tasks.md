# Tasks

## 1. 规则文本落地（`change-guidance/core/change-practice.md`）

- [ ] 1.1 Change Admission 节补 scope rule：实现工件（design/tasks）只排序与
  验证、不重新设计；设计决策归 owning spec/delta 与 design.md；偏离进对应
  change 的 Deviation Register，不顺手改、不隐瞒。
- [ ] 1.2 新增四类陈述小节（~6 行）：引用上游/语料结论标注 运行时事实 / 上游
  要求 / 应用仓建议 / 仓库自定；上游制度类条目永远标"上游参考"，不冒充本仓
  要求（出处标注钉定版本）。
- [ ] 1.3 Delivery Evidence 节补一行 slice 收尾纪律：每个 slice 收尾跑
  lint+test 并重读 spec 评审检查单（从 control-placement 触发泛化为常规）。
- [ ] 1.4 自查增量 ≤ ~25 行、"要求+一句为什么"体例。

## 2. checker 扩展（`check_change_guidance.py` + `change_guidance_kernel.py`）

- [ ] 2.1 内核新增两段常设段的语法常量与解析（`## Deviation Register`、
  `## Delivery Record`、四字段标签、`none:` 行格式），复用现有解析助手风格。
- [ ] 2.2 校验接入：tasks.md 存在的活跃 change——两段在场；register 非空
  （`none: <rationale>` 或 ≥1 条登记）；Delivery Record 四字段标签在场。
  tasks.md 不存在 → 跳过；scoped 与 standalone 两模式同规则；Program 形态
  适配验证（冲突回 design 重裁）。
- [ ] 2.3 违规信息点名 change、缺失段/字段与期望格式（对齐现有 violation
  code 风格）；checker docstring 登记新规则语义（@impl 标签惯例）。

## 3. 负例 focused tests（`openspec/tests/governance/test_change_authority.py`）

- [ ] 3.1 四类 case，直调 checker、断言退出码与点名信息：合规 fixture（两段
  在场 + `none:` + 四标签）→ exit 0；缺 Deviation Register → exit 1 点名；
  register 空段（无 none 无条目）→ exit 1 点名；缺任一 Delivery Record 字段
  → exit 1 点名。
- [ ] 3.2 确认 CI unittest discover（`openspec/tests/governance`）纳入新文件；
  全套件绿。

## 4. dogfood 自证（本 change 即第一个被咬的对象）

- [ ] 4.1 本 tasks.md 的两段常设段通过新规则（见下方两节）；checker 对本
  change scoped 校验 exit 0。
- [ ] 4.2 standalone 扫描全树 exit 0（含既有治理面不回归）。

## 5. 归档前义务（config.yaml rules.tasks 硬性收尾）

- [ ] 5.1 repo 根 `python3 openspec/governance/check_project_gate.py --phase
  closeout`（退出码直测）；`deep_research_harness/` 下 `UV_OFFLINE=1 make
  verify`；repo 根 `openspec validate harden-change-authority --strict` 与
  `git diff HEAD --check`。
- [ ] 5.2 gitlink 取证四件套 + `git diff --submodule=short`——确认 `deerflow/`
  未动；确认 `openspec --version` 与 `.agents/skills/*/SKILL.md` `generatedBy`
  一致。
- [ ] 5.3 Delivery Record 四段填实（下方节）、Deviation Register 终值核对。

## 6. 归档与回写

- [ ] 6.1 archive → `openspec/changes/archive/2026-10-08-harden-change-authority/`。
- [ ] 6.2 回写 plan C2 条目（✅ 已落地 + 落点裁决摘要）。

## Deviation Register

- none: 规划期无偏离；实现期出现偏离时逐条覆盖本行登记（偏离了什么 / 裁决
  依据 / 落在哪个工件）。

## Delivery Record

- **外部行为**: （closeout 前填实——本 change 让维护者/agent 看到什么）
- **影响面**: （closeout 前填实——改了哪些层）
- **实际跑了什么**: （closeout 前填实——命令 + 退出码）
- **未执行的检查**: （closeout 前填实——没跑什么、为什么、谁接住）
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者逐行拍板范围与规范语义，对交付负最终责任。
