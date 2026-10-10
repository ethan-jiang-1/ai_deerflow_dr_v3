# Design: align-ci-openspec-pin

## Context

三处版本事实：本地 `openspec --version` = 1.14.0；`.agents/skills/*/SKILL.md`
`generatedBy` = 1.14.0；workflow npm pin = 1.13.1（checker 常量同）。checker 只核对
workflow vs 自身常量——两处一起陈旧即全绿，这是与 change ① 同型的"声明只对自身互证"
盲区。spec（ci-governance）不含版本字面量，版本由声明表 own。

## Goals / Non-Goals

- Goals：workflow + checker 常量 + fixture 三处同步 1.14.0；workflow 的
  "generation-aligned" 注释恢复为真；本地/远端 strict-validation 代际一致。
- Non-Goals：checker 对 frontmatter 的机器交叉核对（新规则另立卡）；workflow 结构；
  其它依赖版本。

## Approach

红先：改 checker 常量（两处：WORKFLOW_REQUIRED_MARKERS 与任何独立 pin 声明）→ 真树
checker 红（workflow 仍是 1.13.1）+ fixture 套件红 → workflow npm pin 与 fixture 同步
1.14.0 → 转绿。governance/README 不含版本字面量，无需改。

## Alternatives

- **顺带让 checker 交叉核对 frontmatter**——输在：新规则需要新的 declaring 面与负例，
  独立成卡才能红先（本 change 只做代际对齐这一件事）。
- **反向把本地/skills 降回 1.13.1**——输在：本地 CLI 1.14.0 已产出两笔归档 change 与
  全部 13 spec 的现行 validate 状态，降级是逆着事实走。

## Open Questions

none: 方向（升 1.14.0）、范围（三处同步）、红先路径均定案。
