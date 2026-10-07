# Design

## Context

- 实测事实（本 goal B 项侦察，本地 runs/d_20261007 快照）：`available_skills=None`
  = 框架注入**全目录索引**（约 30 个 skill 的名称+描述+路径 XML 段，system prompt
  33589 字节）；deep-research 在索引中；正文按需加载（渐进披露）；"强制加载"未实现。
- 声明槽（a8fe53a）：config `skills:` → `assembly.resolve_skills`（缺省严格 None）
  → `build_client(available_skills=...)` 透传；SKL guard 钉住缺省姿态与解析规则。
- test_wiring_smoke 对 snapshot 只断言键存在、不锁内容——两梯声明窄面不会碰倒既有
  断言；fixture 脚本模型不读 prompt，行为不受窄面影响。

## Goals / Non-Goals

**Goals:**

- 研究运行的模型可见 skill 目录 = 恰好 deep-research（两梯一致）。
- 收窄生效有零凭证机械证据：config-as-contract 守卫 + 真实 CLI 旅程的窄索引断言。
- fixture 演练链路（装配/状态/准入/报告/诊断）零回归。

**Non-Goals:**

- 不强制加载/方法论遵循质量（真实梯评审另立项）；不加宽声明面；不动 skill 正文、
  tool 执法、admission、subagent 的 skill 面。

## Decisions

1. **两梯都声明，不只 base**：fixture 声明后，既有 CLI 旅程直接端到端证明
   config→resolve→透传→窄索引 全链（零凭证）；只声明 base 则窄面只能靠合成
   build_client 调用证明，弱一档。两梯一致也让"研究运行一律窄面"语义无分叉。
2. **不做声明名预校验，用旅程当绊线**：预校验需读框架投影目录布局
   （`skills_view/public/<name>/`），耦合布局细节；而旅程断言"deep-research 在、
   无关 skill 不在"同时覆盖"框架静默丢弃"与"名字失效"两种故障——一条断言两用，
   且证据在真实链路上。
3. **守卫形态 = config-as-contract**：在既有 `test_skill_declaration.py` 加两断言
   （base 声明恰为 [deep-research]、fixture 同）——声明面是被钉住的决策，改它必红，
   走 owning change。不引入新文件。
4. **文档更正与声明同步**：research-process.md 的 binding 表
   （`available_skills=None`（完整 skill 面）行）与 control-map §9 未实现清单的
   括注（"当前 available_skills=None"）都过时了——随本 change 一并更正为
   "两梯声明窄面 deep-research；None=全目录默认仍存在于未声明时"。

## Alternatives

- **只声明 base，fixture 保持 None**：否——见决策 1，证据弱一档且两梯语义分叉。
- **assembly 预校验声明名 against 投影目录**：否——见决策 2，耦合框架私有布局，
  旅程断言已覆盖该故障类。
- **顺带做强制加载**（把 skill 正文直接拼进首条消息）：否——那是真正的认知变更
  （改变 agent 的任务分派），需要独立 node-agent 立项与真实梯质量证据；本 change
  只收窄可见目录。
- **加宽到 deep-research + github-deep-research + systematic-literature-review**：
  否——用户裁决 B1 = 收窄到 1；加宽是另一个 owning change 的一句话。

## Unresolved Questions

- 无——收窄面、守卫形态、证据路径均已定。
