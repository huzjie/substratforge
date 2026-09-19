# -*- coding: utf-8 -*-
"""共享数据类型：枚举与轻量 dataclass。

全部为纯 stdlib 实现，不依赖 pydantic，保证核心包零依赖可运行。
REST 层的 pydantic 模型（serving/schemas.py）独立存在，二者字段保持一致。
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class SandboxState(str, Enum):
    """沙箱生命周期状态机。

    ::

        PENDING -> RUNNING -> SUSPENDING -> SUSPENDED
                    |   ^             |
                    v   |             v
                 PAUSED |          RESUME -> RUNNING
                        |
                        +--> STOPPING -> STOPPED -> DESTROYED
    """
    PENDING = "pending"          # 已登记，等待分配资源
    RUNNING = "running"          # 活跃运行中（热）
    PAUSED = "paused"            # 进程挂起但内存驻留（温）
    SUSPENDING = "suspending"    # 正在序列化快照（温 -> 冷）
    SUSPENDED = "suspended"      # 快照已落盘，运行环境已释放（冷）
    RESUMING = "resuming"        # 正在从快照恢复
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    DESTROYED = "destroyed"


#: 可被挂起（进入 SUSPENDING）的状态集合
SUSPENDABLE_STATES = {SandboxState.RUNNING, SandboxState.PAUSED}

#: 冷态集合：已释放运行环境，必须走恢复路径
COLD_STATES = {SandboxState.SUSPENDED, SandboxState.STOPPED, SandboxState.DESTROYED}


class IsolationLevel(str, Enum):
    """隔离强度，从弱到强。调度器与安全策略据此做准入判断。"""
    PROCESS = "process"    # 进程级：fork/exec + rlimit + 独立用户（最快）
    GVISOR = "gvisor"      # gVisor runsc：syscall 拦截（推荐默认）
    MICROVM = "microvm"    # Firecracker/Cloud Hypervisor：硬件虚拟化（最强）


class SnapshotFormat(str, Enum):
    """快照序列化格式。"""
    TAR = "tar"            # tar 流（通用、兼容性好）
    SQUASHFS = "squashfs"  # squashfs（只读、紧凑、可随机访问）
    MEMIMG = "memimg"      # 自定义内存镜像（最快恢复，实验性）


class StorageBackend(str, Enum):
    """快照仓库后端。"""
    LOCAL = "local"
    S3 = "s3"
    MINIO = "minio"
    MEMORY = "memory"


class EvictionPolicy(str, Enum):
    """冷态驱逐 / 淘汰策略。"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    NONE = "none"


@dataclass
class ResourceQuota:
    """单个沙箱的资源配额（0 表示不限制）。"""
    cpu_millis: int = 0          # 千分之一核（如 500 = 0.5 核）
    memory_mb: int = 256         # 内存上限（MB）
    disk_mb: int = 512           # 可写层上限（MB）
    pids: int = 64               # 最大进程数
    network_egress_kbps: int = 0  # 出口带宽限制，0 不限

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class SandboxSpec:
    """创建沙箱的完整规格。"""
    name: str
    image: str = "python:3.12"          # 镜像 / 根文件系统标识
    command: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    workdir: str = "/workspace"
    isolation: IsolationLevel = IsolationLevel.PROCESS
    quota: ResourceQuota = field(default_factory=ResourceQuota)
    labels: dict[str, str] = field(default_factory=dict)
    max_idle_seconds: int = 300          # 超过则自动挂起
    auto_suspend: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["isolation"] = self.isolation.value
        return d


@dataclass
class SnapshotInfo:
    """一条快照的元信息。"""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    sandbox_id: str = ""
    created_at: float = field(default_factory=time.time)
    size_bytes: int = 0
    compressed_bytes: int = 0
    format: SnapshotFormat = SnapshotFormat.TAR
    parent_id: Optional[str] = None       # 增量快照的父快照
    checksum: str = ""
    tags: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["format"] = self.format.value if hasattr(self.format, "value") else self.format
        return d


@dataclass
class SandboxRuntimeInfo:
    """沙箱运行时的实时观测信息。"""
    sandbox_id: str
    state: SandboxState = SandboxState.PENDING
    pid: Optional[int] = None
    isolation: IsolationLevel = IsolationLevel.PROCESS
    cpu_usage_pct: float = 0.0
    memory_rss_mb: float = 0.0
    idle_seconds: float = 0.0
    last_seen: float = field(default_factory=time.time)
    host: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["state"] = self.state.value
        d["isolation"] = self.isolation.value
        return d


@dataclass
class SchedulerStats:
    """调度器聚合统计。"""
    total: int = 0
    running: int = 0
    paused: int = 0
    suspended: int = 0
    pending: int = 0
    evicted_total: int = 0
    resumed_total: int = 0
    avg_resume_ms: float = 0.0
    host_density: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


def new_id(prefix: str = "") -> str:
    """生成带前缀的短 ID。"""
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def now() -> float:
    """单调时间戳（秒）。"""
    return time.time()


__all__ = [
    "SandboxState", "IsolationLevel", "SnapshotFormat", "StorageBackend",
    "EvictionPolicy", "SUSPENDABLE_STATES", "COLD_STATES",
    "ResourceQuota", "SandboxSpec", "SnapshotInfo", "SandboxRuntimeInfo",
    "SchedulerStats", "new_id", "now",
]
