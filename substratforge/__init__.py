# -*- coding: utf-8 -*-
"""substratforge — 高密度智能体基板（Agent Substrate）运行时编排平台。

灵感来自 Google 2026-09 开源到 GKE 的 Agent Substrate：把成千上万个空闲智能体
「挂起」成休眠态、需要时在亚秒级恢复，从而在单机上打包比标准容器高一个数量级
的密度。本仓库提供一个**本地可运行、零外部服务依赖**的开源实现：

- Sandbox   三档隔离沙箱（进程级 / gVisor / microVM），可插拔后端
- Snapshot  挂起时把 agent 的完整状态（内存 + 文件系统）序列化成增量快照
- Scheduler 密度感知调度（装箱 / 驱逐 / 冷热晋升），单机可「停靠」上千休眠环境
- Storage   快照仓库（本地 / S3 / MinIO），增量去重 + 垃圾回收
- Runtime   agent 生命周期状态机 + 心跳看门狗 + 任务队列
- Serving   FastAPI REST + CLI + Python SDK
- Observability  metrics / tracing / 健康检查
- Security   沙箱策略 / 配额 / 审计护栏

用法（零依赖核心即可跑通挂起/恢复演示）：
    from substratforge import Substrate
    s = Substrate.from_config("config.yaml")
    sandbox = s.spawn(name="hello", image="python:3.12", command=["python", "-c", "import time; time.sleep(3600)"])
    snap = s.suspend("hello")            # 挂起 -> 快照落盘
    s.resume("hello")                     # 500ms 内恢复完整状态
    s.destroy("hello")
"""

__version__ = "0.1.0"
__author__ = "substratforge contributors"
__license__ = "MIT"

from .config import Config, load_config
from .errors import (
    SubstrateError, SandboxError, SnapshotError, SchedulerError,
    StorageError, RuntimeError as RuntimeErrorBase, NotFoundError,
    AlreadyExistsError, QuotaExceededError, IsolationError, ConfigurationError,
)
from .types import (
    SandboxState, IsolationLevel, SnapshotFormat, StorageBackend,
    EvictionPolicy, SandboxSpec, SnapshotInfo, ResourceQuota, SchedulerStats,
)
from .core.substrate import Substrate

__all__ = [
    "Substrate",
    "Config", "load_config",
    "SandboxState", "IsolationLevel", "SnapshotFormat", "StorageBackend",
    "EvictionPolicy", "SandboxSpec", "SnapshotInfo", "ResourceQuota", "SchedulerStats",
    "SubstrateError", "SandboxError", "SnapshotError", "SchedulerError",
    "StorageError", "RuntimeErrorBase", "NotFoundError", "AlreadyExistsError",
    "QuotaExceededError", "IsolationError", "ConfigurationError",
    "__version__",
]
