# Tasks

## 1. 根 AGENTS.md 等式修正

- [x] 1.1 第 8 行 pin 等式改写为后代关系表述（D1 措辞），逐字计数确认
  ≤2425、`DOC_BUDGETS` 不动；grep 全仓确认无其他 `= 上游 v2.1.0` 等式残留。

## 2. 语料入库（原样复制 + 索引登记）

- [x] 2.1 `cp -R` 语料 38 文件到 `_backlog/_reference/deerflow-application-corpus/`，
  逐字不动；`diff -r` 对源确认零差异（记录到 Delivery Record）。
- [x] 2.2 `_reference/README.md` 目录表加语料条目行（出处：源路径 + 钉定
  `v2.1.0` = `345f08be` + 复制日期 + Node 22 实测）+ 目录组织节加一条。
- [x] 2.3 复制品内 `node verify.mjs` → exit 0（语料自检确认复制完整）。

## 3. 钉定纪律（deerflow-downstream profile）

- [x] 3.1 `change-guidance/profiles/deerflow-downstream/deerflow-downstream.md`
  补钉定纪律小节（D3 三句话：钉定引用+核验方法 / 文档=快照以源码核验为准 /
  re-pin 重审在案论断）。

## 4. 验证与回执

- [x] 4.1 负例自证：`git merge-base --is-ancestor 345f08be ceebf97f` → exit 0
  取证记录（等式修正依据，写入 Delivery Record）。
- [x] 4.2 治理回执：doc-hygiene / change-guidance / 治理 unittest 套件（含
  pin-agreement）退出码直测全绿；根 AGENTS 字符直测打印。

## 5. 归档前义务

- [x] 5.1 repo 根 closeout gate（退出码直测）；`deep_research_harness/` 下
  `UV_OFFLINE=1 make verify`；repo 根 `openspec validate pin-upstream-claims
  --strict` 与 `git diff HEAD --check`。
- [x] 5.2 gitlink 取证四件套 + `git diff --submodule=short`——确认 `deerflow/`
  未动；`openspec --version` 与 skill `generatedBy` 一致。

## 6. 归档与回写

- [x] 6.1 archive → `openspec/changes/archive/2026-10-08-pin-upstream-claims/`。
- [x] 6.2 回写 plan C3 条目（✅ 已落地 + 裁决 A 记录）。

## Deviation Register

- none: 实现与已批准的 design/tasks 一致；等式残留排查在 `README.md:93` 发现
  同病一处并按 task 1.1 精神一并修正（同语义决策、同 owner 面扩展，非 scope
  偏离——已记入影响面）。

## Delivery Record

- **外部行为**: 根 AGENTS.md 与 README.md 对 gitlink 的表述与 git 事实一致
  （`ceebf97f` = v2.1.0 的后代、digest 分支，非 tag）；语料证据库（38 文件）
  进仓自包含，换机器可读可自检；对上游的论断从此有成文钉定纪律（钉定引用 +
  核验方法 / 文档=快照以源码为准 / re-pin 重审）。
- **影响面**: `AGENTS.md`（一行，2419/2425 字符）、`README.md`（一行残留修正）、
  `_backlog/_reference/`（新增 `deerflow-application-corpus/` 38 文件 +
  `README.md` 索引两处）、`change-guidance/profiles/deerflow-downstream/
  deerflow-downstream.md`（Pinning Discipline 节）。gitlink 未动、零运行时面、
  预算表未动。
- **实际跑了什么**: `diff -r` 源↔复制品 → 零差异；复制品 `node verify.mjs`
  → exit 0（Node 22）；`git -C deerflow merge-base --is-ancestor 345f08be
  ceebf97f` → exit 0（等式修正依据）；治理 unittest 套件（含 pin-agreement）
  → exit 0；doc-hygiene / change-guidance / closeout gate → 各 exit 0；
  `UV_OFFLINE=1 make verify` → exit 0；`openspec validate --strict` 与
  `git diff HEAD --check` → exit 0；skill 对齐 1.14.0。
- **未执行的检查**: 语料 19 页结论的语义正确性未重验（其 `_coverage` 十轮核验
  记录在案为依据，本 change 只保证复制完整）；`verify.mjs` 不进 CI（明示决策，
  非遗漏）；上游新 release 的重审未触发（触发条件未发生，纪律已登记）。
- **AI 参与披露**: 本 change 由 coding agent（GLM，经 DeepSeek Harness）起草并
  实现，维护者拍板语料处置（Option A）与范围，对交付负最终责任。
