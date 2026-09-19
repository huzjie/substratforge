# -*- coding: utf-8 -*-
"""资源配额计算与汇总：判断宿主容量是否还能容纳新的活跃沙箱。

调度器在装箱决策前调用这里，避免把宿主内存 / CPU 打爆。
"""
from __future__ import annotations

from dataclasses import dataclass

from ..types import ResourceQuota


@dataclass
class HostCapacity:
    """宿主可用容量（MB / 毫核 / 可写层 MB）。"""
    memory_mb: int = 8192
    cpu_millis: int = 8000
    disk_mb: int = 65536


def sum_quota(quotas: list[ResourceQuota]) -> ResourceQuota:
    """汇总一组配额。"""
    return ResourceQuota(
        cpu_millis=sum(q.cpu_millis for q in quotas),
        memory_mb=sum(q.memory_mb for q in quotas),
        disk_mb=sum(q.disk_mb for q in quotas),
        pids=sum(q.pids for q in quotas),
    )


def can_fit(capacity: HostCapacity, used: ResourceQuota, new: ResourceQuota) -> bool:
    """判断在已用基础上还能否容纳一个新沙箱。"""
    if new.memory_mb and used.memory_mb + new.memory_mb > capacity.memory_mb:
        return False
    if new.cpu_millis and used.cpu_millis + new.cpu_millis > capacity.cpu_millis:
        return False
    if new.disk_mb and used.disk_mb + new.disk_mb > capacity.disk_mb:
        return False
    return True


__all__ = ["HostCapacity", "sum_quota", "can_fit"]
