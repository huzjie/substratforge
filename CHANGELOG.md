# 变更日志

## [0.1.0] - 2026-09-19

### 新增
- 三档隔离沙箱后端（process / gvisor / microvm）
- 快照引擎（tar + 块级增量 + zstd/gzip/lz4 压缩）
- 密度感知调度器（装箱 / 空闲挂起 / 驱逐 / 晋升）
- 快照存储（本地 / S3 / MinIO / 内存）+ GC
- agent 运行时（生命周期状态机 + 心跳看门狗 + 任务队列）
- 服务层（FastAPI REST + CLI + Python SDK）
- 可观测性（Prometheus 指标 + span 追踪 + 健康检查）
- 安全（最小隔离准入 + 配额 + 护栏 + 审计）
- 插件系统 + 基准测试框架
