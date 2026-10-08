# Tasks

## 1. 闭环页落地（主落点 `openspec/README.md`）

- [x] 1.1 按 design D3 骨架重写 `openspec/README.md`：保留既有 Reading Map 五条
  路由不动；新增 `## 开发闭环（一页走通）` 六步编号列表——①意图（
  [_backlog](../../_backlog/README.md) plan → 毕业判据 = 能写出 Change Focus）
  ②权威归属（[Policy Route](change-guidance/README.md) + 应用 owner 表）③slice
  交付（propose 停在拍板边界、红绿先行、文档随 owning slice）④证据分层（链接
  车道表）⑤验证形态（`make verify` / `make smoke` / 治理 checker 序列 / closeout
  gate 退出码直测）⑥交付记录与归位（回执 + [closeout 义务](governance/selected-change-closeout.md)
  + archive → specs/ 主干）。每步一句话 + 链接，不复制 owner 正文。
- [x] 1.2 新增 `## 证据分层：四件不同的事` 小节：本仓命名（离线单元与契约
  mirror / 装配 smoke / 真实梯观察 / 冷启动发布），每层一句话"证明什么/不证明
  什么"并链接 [testing-and-evaluation](../../deep_research_harness/docs/testing-and-evaluation.md)
  车道表；结尾一句"一层通过不代表下一层成立"。
- [x] 1.3 新增 `## 门禁等级（读规则先问在哪层）` 小节：四分词汇（成文标准 /
  机器门禁 / 自我声明 / 仓库外不可核实），每级一个本仓实例举偶；标注出处为
  上游参考（DeerFlow 应用开发语料·卷二组织立场，钉定 v2.1.0），不冒充本仓要求。
- [x] 1.4 控制页面在 ~70 行内；自查"路由不复制"——任何 owner 的正文句不得
  整句出现在本页。

## 2. 配套登记（两处一行级小改）

- [x] 2.1 `_backlog/README.md` 总流程节末补一行路由："全景一页走通见
  [openspec/README.md](../openspec/README.md) 开发闭环"。
- [x] 2.2 `openspec/change-guidance/local/deep-research.md` Reader Roles 表补
  `openspec/README.md` 行：Primary reader = 维护者/coding agent，Job = 走通开发
  闭环、引用证据分层与门禁等级词汇。

## 3. 验证与回执（runner 写下，退出码直测）

- [x] 3.1 负例控制：临时破坏闭环页一个相对链接，运行
  `python3 openspec/governance/check_doc_hygiene.py`，确认非零退出并点名断链；
  恢复后同命令退出码 0。证明既有链接守卫咬住新内容。
- [x] 3.2 证据回执：`python3 openspec/governance/check_doc_hygiene.py` 与
  `python3 openspec/governance/check_change_guidance.py` 退出码 0（直测，不经
  管道）；确认 DOC_BUDGETS 无漂移（根 AGENTS.md 未动）。
- [x] 3.3 旅程自证：逐个点开闭环页六步的全部链接，确认可点达真实 owner（本
  任务即操作者面旅程证据，随回执记录）。

## 4. 归档前义务（config.yaml rules.tasks 硬性收尾）

- [x] 4.1 repo 根运行 `python3 openspec/governance/check_project_gate.py
  --phase closeout`（退出码直测）；`deep_research_harness/` 下独立运行
  `UV_OFFLINE=1 make verify`；repo 根运行 `openspec validate
  land-development-loop-map --strict` 与 `git diff HEAD --check`。
- [x] 4.2 记录范围证据：`git status --porcelain=v1 --untracked-files=all`、
  `git ls-files --stage deerflow`、`git submodule status -- deerflow`、
  `git -C deerflow status --porcelain=v1 --untracked-files=all`，复核
  `git diff --submodule=short`——确认 gitlink 未动。
- [x] 4.3 确认 `openspec --version` 与 `.agents/skills/*/SKILL.md` 的
  `generatedBy` frontmatter 一致（只读检查；不一致则登记为 drift，由用户
  裁决后再归档）。
- [x] 4.4 归档后回写：`_backlog/plans/2026-10-08-application-corpus-adoption.md`
  的 C1 条目标注已落地（C2 以本页词汇为锚点开工）。
