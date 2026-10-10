# Tasks: widen-doc-link-guard-scope

## 1. 红：self-test 负例先行

- [ ] 1.1 在 `check_doc_hygiene.py` 的 self-test 电池新增案例：临时树含
      `deep_research_harness/tests/README.md`（含一条指向不存在文件的相对链接）→
      断言 `_rule_links`（扩面后）点名该文件与目标。此刻规则未扩面 → 案例红
      （规则对资产文档沉默）。Verify: `python3 openspec/governance/check_doc_hygiene.py --self-test`
      报新案例失败。
- [ ] 1.2 负例的负例：同一临时树修复链接后案例转绿——证明案例测的是规则而非树。

## 2. 绿：扩面接线

- [ ] 2.1 checker 新增 `LINKED_ASSET_DOCS`（三份文档封闭清单 + 逐行注释声明扩张
      须走 owning change）；`_rule_links` 与 `_rule_encoding_newline` 迭代组扩为三元。
      Verify: `--self-test` 全绿（含 1.1 案例）。
- [ ] 2.2 checker 模块 docstring 补一句受管面与锚点不校验的声明限制。
- [ ] 2.3 真树全绿：`python3 openspec/governance/check_doc_hygiene.py` exit 0
      （1bb28b2 已清 18 死链，568 链接预清在案）。

## 3. 注册与 spec 落地

- [ ] 3.1 governance README `check_doc_hygiene.py` 行措辞更新（"入口链、docs 层与
      测试/工具资产文档的相对链接"）。
- [ ] 3.2 治理 unittest 套件全绿：
      `python3 -m unittest discover -s openspec/tests/governance -q`。
- [ ] 3.3 `openspec validate widen-doc-link-guard-scope --strict` 0；
      closeout gate（`--phase closeout`）0。

## 4. 归档与知识归位

- [ ] 4.1 `openspec archive widen-doc-link-guard-scope`（strict validate 通过）；
      归档 ritual 当场把 ADDED requirement sync 进
      `openspec/specs/doc-truthfulness/spec.md`（本轮 ca82507 修过两处漏 sync，
      归位不欠账）。
- [ ] 4.2 归档后复跑 `check_doc_hygiene` + `check_project_specs` exit 0。

## Deviation Register

- none: 尚未开始 apply；批次与判定以 design 为准，apply 中若出现偏离就地登记。

## Delivery Record

- **外部行为**: （apply 后填写）本 change 落地后的可观察行为变化一句话。
- **影响面**: （apply 后填写）触碰的文件与面清单。
- **实际跑了什么**: （apply 后填写）红绿命令与退出码直读回执。
- **未执行的检查**: （apply 后填写）UNVERIFIED 项如实列出；无则写 none。
- **AI 参与披露**: 本 change 由 coding agent 起草并实现（常设授权，DeepSeek Harness）。
