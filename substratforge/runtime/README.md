# Agent 运行时

- `lifecycle.py`：状态机（显式转移表），杜绝非法迁移
- `heartbeat.py`：心跳看门狗，产出「可挂起」与「失联」候选
- `task.py`：线程安全任务队列 + 动作处理器注册

三者协同：心跳发现空闲 -> 投递 `suspend` 任务 -> 生命周期切到 SUSPENDING
-> 快照落盘 -> SUSPENDED；resume 请求 -> RESUMING -> RUNNING。
