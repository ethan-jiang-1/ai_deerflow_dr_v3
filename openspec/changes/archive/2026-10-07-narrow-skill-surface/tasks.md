# Tasks

> 红绿纪律：退出码直测。工作目录 `deep_research_harness/`（除标注仓库根）。

## 1. 守卫红证 + 声明落地

- [x] 1.1 红证先行：`tests/contract/test_skill_declaration.py` 增 `LadderDeclarationTest`
  ——断言 base.yaml 与 fixture.yaml 的 `skills` 各恰为 `["deep-research"]`。此刻两梯
  均未声明 → 红。记录红输出。
- [x] 1.2 声明落地：`config/base.yaml` 与 `config/fixture.yaml` 的 skills 注释段改为
  实声明 `skills: [deep-research]`（注释保留语义说明：收窄可见面，不强制使用）。
  Verify: 1.1 转绿，`PYTHONPATH=src python3 -m unittest tests.contract.test_skill_declaration
  -v` 退出码 0。
- [x] 1.3 全量 verify：`make verify` 退出码 0（test ID +2，无意外增删）。

## 2. 旅程窄索引断言（smoke 车道）

- [x] 2.1 `tests/integration/test_cli_journey.py` 的 create 旅程增窄面断言：跑完 create
  后读该 bundle 的 `diagnostics/assembly-snapshot.json`，断言 system_prompt 含
  `deep-research` 且不含 `podcast-generation`（无关 skill 代表）。此刻若框架不尊重
  声明则红——正是绊线。Verify（uv 环境）:
  `UV_CACHE_DIR="$PWD/../.uv-cache" uv run --no-sync python -m unittest discover -s
  tests/integration -p 'test_cli_journey.py' -v` 退出码 0。
- [x] 2.2 全量双车道：`make verify` 退出码 0；`make smoke` 退出码 0。

## 3. 文档更正与收口

- [x] 3.1 文档：`docs/research-process.md` binding 表与 skill 面事实行更正（两梯声明
  deep-research 窄面；None=全目录默认仅存于未声明时；"强制加载"仍未实现且不在本
  change）；`docs/control-map.md` §9 未实现清单括注同步。Verify（仓库根）:
  `python3 openspec/governance/check_doc_hygiene.py` 退出码 0。
- [x] 3.2 收口门禁（仓库根）：change-guidance / architecture / project-specs /
  `openspec validate --strict` / closeout gate / `git diff --check` 全部退出码直测 0；
  回执记录 revision、退出码、snapshot 实证（窄索引字节数对比全目录 33589 字节）；
  使用级质量（agent 是否遵循方法论）显式 UNVERIFIED——真实梯证据待用户提供凭证。
  归档后根 README 计数 ritual 同步。
