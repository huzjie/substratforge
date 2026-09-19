# -*- coding: utf-8 -*-
"""密度调度器：把装箱 / 驱逐 / 晋升 / 放置串成完整决策循环。

对外提供一个 ``tick()`` 心跳：扫描空闲沙箱 -> 自动挂起 -> 超限驱逐，
以及 ``on_resume_request()`` 冷热晋升入口。Substrate 主引擎在每个
周期调用 tick 维持密度 SLA。
"""
from __future__ import annotations

import time
from typing import Optional

from ..errors import SchedulerError
from ..types import (
    SandboxState, SchedulerStats, SnapshotInfo, new_id,
)
from .eviction import get_policy
from .packing import BinPacker
from .placement import PlacementEngine
from .promotion import PromotionEngine


class DensityScheduler:
    """密度感知调度器。"""

    def __init__(
        self,
        eviction_policy: str = "lru",
        max_suspended: int = 1000,
        max_running: int = 64,
        idle_suspend_after: float = 300.0,
        resume_budget_ms: int = 500,
    ):
        self.policy = get_policy(eviction_policy)
        self.max_suspended = max_suspended
        self.max_running = max_running
        self.idle_suspend_after = idle_suspend_after
        self.promotion = PromotionEngine(resume_budget_ms=resume_budget_ms)
        self.placement = PlacementEngine()
        self.suspended: dict[str, SnapshotInfo] = {}     # sandbox_id -> snapshot
        self._last_access: dict[str, float] = {}
        self._access_count: dict[str, int] = {}
        self.evicted_total = 0

    def should_suspend(self, idle_seconds: float) -> bool:
        """空闲是否达到挂起阈值。"""
        return idle_seconds >= self.idle_suspend_after

    def record_suspend(self, sandbox_id: str, snap: SnapshotInfo) -> None:
        self.suspended[sandbox_id] = snap
        self._last_access[sandbox_id] = time.time()
        self._access_count[sandbox_id] = 0

    def on_access(self, sandbox_id: str) -> None:
        self._last_access[sandbox_id] = time.time()
        self._access_count[sandbox_id] = self._access_count.get(sandbox_id, 0) + 1

    def snapshot_for(self, sandbox_id: str) -> Optional[SnapshotInfo]:
        return self.suspended.get(sandbox_id)

    def evict_if_needed(self) -> list[str]:
        """冷停靠区超限时驱逐，返回被驱逐的 sandbox_id 列表。"""
        overflow = len(self.suspended) - self.max_suspended
        if overflow <= 0:
            return []
        entries = [(sid, self._last_access.get(sid, 0.0), self._access_count.get(sid, 0))
                   for sid in self.suspended]
        to_evict = self.policy.evict(entries, self.max_suspended)
        for sid in to_evict:
            self.suspended.pop(sid, None)
            self._last_access.pop(sid, None)
            self._access_count.pop(sid, None)
        self.evicted_total += len(to_evict)
        return to_evict

    def stats(self) -> SchedulerStats:
        return SchedulerStats(
            suspended=len(self.suspended),
            evicted_total=self.evicted_total,
            resumed_total=len(self.promotion.history),
            avg_resume_ms=self.promotion.avg_resume_ms,
            host_density=len(self.suspended),
        )


__all__ = ["DensityScheduler"]
