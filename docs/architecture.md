# 架构设计

## 分层

```
Serving (REST / CLI / SDK)
        │
   Substrate (主引擎：spawn/suspend/resume/destroy/tick)
        │
   ┌────┼──────────┬───────────┬──────────┐
   │    │          │           │          │
Sandbox Snapshot  Scheduler  Storage   Runtime
   │    │          │           │          │
Security + Observability（横切）
```

## 状态机

沙箱状态转移（见 `runtime/lifecycle.py`）：

```
PENDING -> RUNNING <-> PAUSED
                |          |
                v          v
             SUSPENDING -> SUSPENDED
                             |
                             v
                          RESUMING -> RUNNING
RUNNING/PAUSED -> STOPPING -> STOPPED -> DESTROYED
```

挂起（suspend）走 `RUNNING -> SUSPENDING -> SUSPENDED`，
恢复（resume）走 `SUSPENDED -> RESUMING -> RUNNING`。

## 挂起链路

1. `Substrate.suspend(id)`
2. 生命周期切 `SUSPENDING`
3. `backend.pause(handle)` 冻结进程（SIGSTOP / runsc pause）
4. `SnapshotEngine.capture(handle)`：
   - `MemoryCapture` 采集进程元信息
   - `FilesystemLayer.tar` 打包可写层
   - `DeltaEncoder` 相对父快照做块级增量
   - `Compressor` 压缩
5. `Storage.put(snapshot)` 落盘
6. `backend.kill(handle)` 释放运行环境
7. 生命周期切 `SUSPENDED`，调度器登记冷态

## 恢复链路

1. `Substrate.resume(id)`
2. 生命周期切 `RESUMING`
3. `SnapshotEngine.materialize` 还原文件系统到恢复目录
4. `backend.spawn(spec)` 重新拉起进程
5. 生命周期切 `RUNNING`
6. 调度器晋升记录 + 心跳复位

## 密度调度

- **空闲挂起**：心跳看门狗发现 idle 超阈值 -> tick() 自动 suspend
- **冷停靠驱逐**：suspended 数量超上限 -> 按 LRU/LFU/FIFO 淘汰真正删除
- **晋升预算**：resume 计时，超 `resume_budget_ms` 记录告警
