# -*- coding: utf-8 -*-
"""统一异常体系。

每个子系统都抛出继承自 :class:`SubstrateError` 的专用异常，便于上层按域捕获，
也便于在 REST 层映射成合适的 HTTP 状态码（见 serving/api.py 的 exception handler）。
"""


class SubstrateError(Exception):
    """所有 substratforge 异常的基类。"""

    #: 可选错误码，用于 API 响应里的 ``code`` 字段
    code = "substrate_error"

    def __init__(self, message: str, *, detail: dict | None = None):
        super().__init__(message)
        self.message = message
        self.detail = detail or {}


class ConfigurationError(SubstrateError):
    """配置缺失或非法。"""
    code = "configuration_error"


class SandboxError(SubstrateError):
    """沙箱创建 / 运行 / 销毁失败。"""
    code = "sandbox_error"


class SnapshotError(SubstrateError):
    """快照序列化 / 恢复 / 增量合并失败。"""
    code = "snapshot_error"


class SchedulerError(SubstrateError):
    """调度决策（装箱 / 驱逐 / 晋升）失败。"""
    code = "scheduler_error"


class StorageError(SubstrateError):
    """快照仓库读写 / 上传下载失败。"""
    code = "storage_error"


class RuntimeError(SubstrateError):
    """agent 生命周期 / 心跳 / 任务队列错误。"""
    code = "runtime_error"


class NotFoundError(SubstrateError):
    """请求的资源（沙箱 / 快照 / 任务）不存在。"""
    code = "not_found"


class AlreadyExistsError(SubstrateError):
    """请求创建的资源已存在。"""
    code = "already_exists"


class QuotaExceededError(SubstrateError):
    """超出资源配额（CPU / 内存 / 磁盘 / 沙箱数）。"""
    code = "quota_exceeded"


class IsolationError(SubstrateError):
    """隔离等级不满足安全要求（如策略要求 gVisor 但只有进程级后端）。"""
    code = "isolation_error"


__all__ = [
    "SubstrateError", "ConfigurationError", "SandboxError", "SnapshotError",
    "SchedulerError", "StorageError", "RuntimeError", "NotFoundError",
    "AlreadyExistsError", "QuotaExceededError", "IsolationError",
]
