# API 参考

## Substrate 主引擎

| 方法 | 说明 |
|---|---|
| `Substrate.from_config(config)` | 从配置构建引擎 |
| `spawn(name, image, command, isolation, ...)` | 创建沙箱 |
| `suspend(name, tags)` | 挂起 -> 快照 -> 释放 |
| `resume(name, snapshot_id)` | 从快照恢复 |
| `destroy(name)` | 销毁 |
| `get(name)` / `list_sandboxes()` | 查询 |
| `list_snapshots()` | 列出快照 |
| `tick()` | 调度心跳（自动挂起/驱逐） |
| `stats()` | 调度统计 |
| `demo()` | 零依赖演示 |

## 关键类型

- `SandboxState`：pending/running/paused/suspending/suspended/resuming/stopping/stopped/failed/destroyed
- `IsolationLevel`：process/gvisor/microvm
- `SandboxSpec` / `SnapshotInfo` / `ResourceQuota`

## REST 端点

见 `serving/api.py` 与 README「REST API」章节。
