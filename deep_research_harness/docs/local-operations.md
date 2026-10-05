# Local Operations

> 本地命令的坑与环境注意点。命令全集与动词语义的唯一入口是 [`../COMMANDS.md`](../COMMANDS.md)
> （三处一致性由 command-surface-guard 机器守着）；本文件只缓存 environment 招供不了的细节。

## 环境

- `uv sync` 准备框架依赖环境（`../.uv-cache` 暖过之后只需毫秒级）；`make smoke` 与
  `make create` 都依赖它。
- `make verify` 是纯 stdlib：不依赖 `uv sync`，`UV_OFFLINE=1` 兼容，离线可跑。
- `profiles/` 目前没有已注册 profile；本地运行 profile 的权威将来落在 owning change。

## 坑

坑清单唯一持有处在 [`docs/playbook/run-research.md`](playbook/run-research.md) 的坑节（`--config` 被 make 吃掉、`.env` 保留区、smoke 响亮失败噪音等）；本文件不再复制，见坑即去 playbook。
