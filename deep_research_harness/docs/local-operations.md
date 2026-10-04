# Local Operations

> 本地命令的坑与环境注意点。命令全集与动词语义的唯一入口是 [`../COMMANDS.md`](../COMMANDS.md)
> （三处一致性由 command-surface-guard 机器守着）；本文件只缓存 environment 招供不了的细节。

## 环境

- `uv sync` 准备框架依赖环境（`../.uv-cache` 暖过之后只需毫秒级）；`make smoke` 与
  `make create` 都依赖它。
- `make verify` 是纯 stdlib：不依赖 `uv sync`，`UV_OFFLINE=1` 兼容，离线可跑。
- `profiles/` 目前没有已注册 profile；本地运行 profile 的权威将来落在 owning change。

## 坑（详见 [`../playbook/run-research.md`](../playbook/run-research.md) 的坑节）

- real 梯（`--config base` / `CONFIG=base`）需要本目录 `.env` 凭证。凭证属用户保留区：
  缺了就问，绝不代建。fixture 梯零凭证。
- `make create` 里裸写 `--config` 会被 make 本身吃掉（`unrecognized option`）——换梯走
  `CONFIG=` 变量。
- `make smoke` 里以 `RuntimeError: deliberate fixture failure` 收尾的 traceback 是响亮
  失败测试在通过——看退出码，别看噪音。
