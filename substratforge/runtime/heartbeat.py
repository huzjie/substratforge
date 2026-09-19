# -*- coding: utf-8 -*-
"""心跳看门狗：追踪每个活跃沙箱的心跳，超时判定失活/僵尸。

- 活跃沙箱周期上报心跳（agent 侧 SDK 或宿主探活）
- 看门狗扫描超时沙箱，产出「可挂起」候选（进入空闲挂起）
- 彻底失联的沙箱标记为 FAILED
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class HeartbeatRecord:
    """单条心跳记录。"""
    sandbox_id: str
    last_beat: float = field(default_factory=time.time)
    beat_count: int = 0


class HeartbeatWatchdog:
    """心跳看门狗。"""

    def __init__(self, idle_timeout: float = 300.0, dead_timeout: float = 3600.0):
        self.idle_timeout = idle_timeout
        self.dead_timeout = dead_timeout
        self._records: dict[str, HeartbeatRecord] = {}

    def beat(self, sandbox_id: str) -> None:
        rec = self._records.setdefault(sandbox_id, HeartbeatRecord(sandbox_id=sandbox_id))
        rec.last_beat = time.time()
        rec.beat_count += 1

    def idle_seconds(self, sandbox_id: str) -> float:
        rec = self._records.get(sandbox_id)
        if rec is None:
            return 0.0
        return time.time() - rec.last_beat

    def remove(self, sandbox_id: str) -> None:
        self._records.pop(sandbox_id, None)

    def idle_candidates(self) -> list[str]:
        """返回空闲超过 idle_timeout 的沙箱（可挂起候选）。"""
        return [sid for sid, rec in self._records.items()
                if time.time() - rec.last_beat >= self.idle_timeout]

    def dead_candidates(self) -> list[str]:
        """返回失联超过 dead_timeout 的沙箱。"""
        return [sid for sid, rec in self._records.items()
                if time.time() - rec.last_beat >= self.dead_timeout]

    def __len__(self) -> int:
        return len(self._records)


__all__ = ["HeartbeatWatchdog", "HeartbeatRecord"]
