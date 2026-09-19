# -*- coding: utf-8 -*-
"""安全策略：最小隔离等级准入 + 配额校验。"""
from __future__ import annotations

from ..errors import IsolationError, QuotaExceededError
from ..types import IsolationLevel, ResourceQuota, SandboxSpec

#: 隔离强度排序（用于最小隔离等级比较）
_ORDER = {IsolationLevel.PROCESS: 0, IsolationLevel.GVISOR: 1, IsolationLevel.MICROVM: 2}


class SecurityPolicy:
    """安全策略。"""

    def __init__(self, min_isolation: IsolationLevel | str = IsolationLevel.PROCESS,
                 default_quota: ResourceQuota | None = None):
        self.min_isolation = (
            min_isolation if isinstance(min_isolation, IsolationLevel)
            else IsolationLevel(min_isolation)
        )
        self.default_quota = default_quota or ResourceQuota()

    def enforce_isolation(self, spec: SandboxSpec) -> None:
        """若 spec 隔离等级低于最低要求，抛 IsolationError。"""
        if _ORDER[spec.isolation] < _ORDER[self.min_isolation]:
            raise IsolationError(
                f"沙箱 {spec.name} 隔离等级 {spec.isolation.value} 低于最低要求 {self.min_isolation.value}"
            )

    def enforce_quota(self, spec: SandboxSpec) -> None:
        """若 spec 配额超过默认上限，抛 QuotaExceededError。"""
        q, d = spec.quota, self.default_quota
        if d.memory_mb and q.memory_mb > d.memory_mb:
            raise QuotaExceededError(f"内存 {q.memory_mb}MB 超过上限 {d.memory_mb}MB")
        if d.pids and q.pids > d.pids:
            raise QuotaExceededError(f"进程数 {q.pids} 超过上限 {d.pids}")


def enforce_min_isolation(level: str, required: str) -> bool:
    """比较两个隔离等级字符串，返回是否满足最小要求。"""
    return _ORDER[IsolationLevel(level)] >= _ORDER[IsolationLevel(required)]


__all__ = ["SecurityPolicy", "enforce_min_isolation"]
