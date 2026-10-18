# Tasks

## 1. Evidence first

- [x] 1.1 Confirm nothing invokes the script: CI workflows, Makefile, the gate, the seven checkers, and every test  ✓ 五处全零：`.github/workflows/*.yml` · `make verify` · `check_project_gate.py` 与七个 checker · 任何测试。
- [x] 1.2 List every place the script is referenced at all, and classify each as registration, documentation, history, or a real caller  ✓ 仅四类引用：自己的 `required-paths.toml` 登记 · `governance/README.md` 组件表一行 · 父卡 · 一个归档 change 的历史 tasks。**没有一类是真实调用者。**
- [x] 1.3 Re-check the program/workstream mode's actual use (not just the file count where its markers appear) and record the corrected verdict  ✓ 重查 program 模式的**实际使用**（不只看标记出现在几个文件）：`2026-10-07-surface-runtime-structure` 真的以 program 形式写过（3 个 workstream）⇒ 更正为**保留**。

## 2. Retire the component

- [x] 2.1 Remove the script  ✓ `git rm openspec/governance/portable_change_guidance_export.py`（140 行）。
- [x] 2.2 Remove its registration, its documentation row, and any budget entry, so no reference dangles  ✓ 删 `required-paths.toml` 登记行与 `governance/README.md` 表行；体积表本无该条目（实测）。
- [x] 2.3 Sync whatever inventory pin asserts the required-path inventory  ✓ 清单 pin 无需同步——套件 253 全过（`test_split_manifest.py` 从 `required-paths.toml` 派生，不单独钉该条目）。

## 3. Correct the parent card

- [x] 3.1 Record the retirement with the reason (no caller) — so a later reader sees a deliberate removal  ✓ 父卡写明退役理由：**无调用者**（并附五处零引用的取证）。
- [x] 3.2 Correct the earlier claim about the program mode, stating what the wrong judgement was based on, and mark that item as *keep* with its evidence  ✓ 父卡更正 #3，**写明原判断错在哪**（只数出现文件数、没看是否真被当 program 用），并附重判证据。
- [x] 3.3 Record the known gap (the kept mode has no battery control) as a tracked follow-up, without expanding this change  ✓ 已知缺口（保留的模式零电池控制）记为跟踪项，**本把不扩张**（补覆盖与「剔除」方向相反，另开一把）。

## 4. Verify and close out

- [x] 4.1 Confirm the architecture checker, doc-hygiene, and the full suite pass, and that the removed path is gone from every inventory  ✓ 架构 checker exit 0（登记无悬挂）· doc-hygiene exit 0 · 套件 exit 0（253）。
- [x] 4.2 Run the full gate set (governance suite, seven checkers, closeout gate, harness lanes) and verify every exit code is 0  ✓ 治理套件 253 全绿 · 七 checker + closeout gate 全 0 · `make verify` 252。
- [x] 4.3 Verify the program mode is untouched: no diff in its code, docs, or config; the product side is untouched too  ✓ program 模式的代码/文档/config **一行未动**（本把 diff 不含它们）· 产品代码与 harness 面零改动。
- [x] 4.4 Confirm the managed line budget went **down**  ✓ 纯减法：删掉 140 行组件（它不在体积表内——体积表只管治理实现文件，故受管行数不变；行数减少体现在仓库而非该表）。
- [x] 4.5 Fill this change's `## Delivery Record` with the four required labels and the raw receipts  ✓ 见下 `## Delivery Record`。

## Delivery Record

- **外部行为**: **对产品与其余守卫零影响**——删掉的是一个没有任何调用者的组件。可见变化：`openspec/governance/` 少 140 行与一个「必需路径」登记；`governance/README.md` 组件表少一行。**program/workstream 模式一行未动**（本轮判为保留）。治理套件用例数不变（**253**）——因为它本来就没有任何测试。
- **影响面**: 删 `openspec/governance/portable_change_guidance_export.py`（140 行）· `required-paths.toml` 一行 · `openspec/governance/README.md` 一行 · 父卡（#3 更正 + #4 执行 + 已知缺口）。**未动**：体积表（该文件不在表内，实测）· `test_split_manifest.py`（其清单从 required-paths.toml 派生）· program 模式代码/文档/config · 产品代码。
- **实际跑了什么**: 五处零引用的取证（CI / Makefile / gate / 七 checker / 测试）· 删除后**架构 checker exit 0**（证明登记与磁盘一致、无悬挂）· doc-hygiene exit 0 · 治理套件 exit 0（253）· 七 checker 逐个 exit 0 · closeout gate exit 0 · `make verify` exit 0（252）· program 模式零 diff · harness 改动行数 0。
- **未执行的检查**: **program 模式仍无电池控制**（已知缺口，记为跟踪项，本把刻意不扩张）· 未验证「将来若需导出引导系统」的取回路径（在 git 历史里，未演练）· 父卡其余裁决项（计数器表数量列 · suspend 面 · 毕业门/可关闭字段）各自独立一把 · 真实模型梯未跑（纯组件退役）。

## Deviation Register

- 更正一条我自己上一轮写下的**错误判断**（不是本把的偏差，但必须留痕）：父卡原写 program/workstream「没有任何真实 change 用过」，实测**用过一次**（3 工作流 program）。错因是**只统计了标记出现的文件数就下结论**，没有核实那些文件里它是否真被当作 program 使用。已在父卡写明错因并改为「保留」。**教训：计数是线索，不是结论——「出现过」与「被使用过」是两件事。**
- 脚本级失误**第四次**：写本记录时又在双引号字符串里套了双引号（`"剔除"`）⇒ `SyntaxError`、整段未生效（未勾仍 14）。已改用「」重跑。这已是本会话同类第四次，属我必须改掉的书写习惯。
- none: 除上述两项外无设计偏离；删除与登记/文档同步一次到位，未产生悬挂引用（上一把的 fix-up 教训已内化：先做同步，再跑门禁）。
