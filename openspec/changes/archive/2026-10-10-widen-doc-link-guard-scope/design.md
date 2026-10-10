# Design: widen-doc-link-guard-scope

See proposal.md — Why. The link engine (`MARKDOWN_LINK_RE` + skip rules +
fragment/query stripping) already exists and is proven by the live tree; this change
only widens the declared surface list and gives the rule its missing spec home.

## Decisions

1. **扩面用新清单，不动既有两份**：`LINKED_ASSET_DOCS` 独立成 tuple，`_rule_links`
   与 `_rule_encoding_newline` 的迭代组从二元 `(("entry-chain", ENTRY_DOCS),
   ("docs-layer", DOC_LAYER_DOCS))` 扩为三元。不并入 `DOC_LAYER_DOCS`——那份清单同时
   喂 `_rule_docs_scope`（docs/ 树范围完整性），tests/tools 文件不在 docs/ 树下，
   并入会误触发范围规则。
2. **self-test 负例进 checker 自带电池**：checker 已有 `--self-test` 红例电池
   （root README 计数漂移等同模式）；新增"资产文档死链"案例，形状照抄现有负例
   （临时树 + 注入违规 + 断言非零 + 点名）。不新开 pytest 文件——治理套件的位置
   约定是 checker 自测在脚本内。
3. **锚点不校验，限制成文**：行号锚（`pump.py#L277` 类）随实现漂移，校验会制造
   假红；spec 明文排除（"excluded by declared limitation, not by omission"），
   checker docstring 同步声明。
4. **归档面明确豁免**：`openspec/changes/archive/` 与 `_backlog/_archived/` 的政策
   地位是"Historical context only"，链接不追溯；spec 场景明文写出，防止未来有人
   "补全"守卫时把归档拖进受管面。

## Alternatives Rejected

- **新开独立 `check_md_links.py` + CI 加步**：否——需要 ci-governance spec delta +
  workflow marker + fixture 同步（promote-lint-to-ci 的全套舞步），而 doc-hygiene
  已在 canonical 序列；扩面是同引擎改清单，切片更小、无新工作流面。
- **全库 tracked .md 全扫**：否——`_research/` 语料为逐字冻结的外部消化产物、
  归档面按政策豁免；全扫会把"历史真实性"误当"现行导航"来守卫。
- **锚点存在性校验**：否——见决策 3。

## Verification

self-test 红（注入死链 → 点名）→ 扩面绿（真树 `check_doc_hygiene` exit 0，568 链接
已人工预清）→ 治理 unittest 套件全绿 → closeout gate 0 → strict validate → archive
（ADDED requirement 随归档 sync 进 doc-truthfulness 主 spec——本轮刚修过两处漏 sync，
归位步骤这次当场做）。
