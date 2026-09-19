# 基准测试

运行 `python examples/density_bench.py` 可测：

- 单次挂起耗时（冻结 + 快照 + 释放）
- 单次恢复耗时（重建 + 拉起）
- 单机冷停靠密度（suspended 数量）

Agent Substrate 的官方数据：单机打包 1000+ 休眠环境、500ms 恢复、
每秒 500+ suspend/resume。本实现的目标是在进程级后端复现同量级行为，
gVisor/microVM 后端进一步逼近生产 SLA。
