# Design: add-workflow-dispatch-trigger

## Context

push 后修复提交（仅根 README）不匹配 paths 过滤 → 远端最后 run 恒红且无合法重跑入口。
dispatch 是 GitHub 原生答案：写权限者显式对 HEAD 跑同一 job。

## Goals / Non-Goals

- Goals：`on:` 加 `workflow_dispatch:`；marker 表钉死防无声摘除；fixture + 负例；
  spec delta 把"手动跑同一序列、不增权限不跳步"写进规范面。
- Non-Goals：paths 过滤变更、scheduled 触发、多 job、输入参数化 dispatch。

## Approach

`on:` 块加两行（`workflow_dispatch:`）；checker marker `"workflow_dispatch:"`；fixture
同步 + gut 负例（移除 dispatch 行必须失败）。红先：marker 先行 → 真树 + 套件双红 →
加触发器转绿。

## Alternatives

- **接受"红 run 留在历史、等下次治理 push"**——输在：HEAD 修好而远端 verdict 恒红的
  窗口可以无限长；操作者对门禁状态失去主动权。
- **改 paths 过滤把根 README 纳入**——输在：治的是本例不是本类；根 README 非治理面，
  纳入会让无关编辑强触 CI（违反 spec 的 path-filtered 语义）。
- **gh rerun**——输在：锁定原 SHA，对修好的 HEAD 无意义。

## Open Questions

none: 触发语义（写权限者显式、同一序列、无新增权限）、同步面、红先路径均定案。
