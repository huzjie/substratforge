# -*- coding: utf-8 -*-
"""装箱算法：把活跃沙箱按资源占用压到最少宿主上（first-fit decreasing）。"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..sandbox.quota import HostCapacity, can_fit, sum_quota
from ..types import ResourceQuota


@dataclass
class Bin:
    """一个宿主箱：累计已用配额 + 承载的沙箱名列表。"""
    capacity: HostCapacity
    used: ResourceQuota = field(default_factory=ResourceQuota)
    items: list[str] = field(default_factory=list)

    def fits(self, q: ResourceQuota) -> bool:
        return can_fit(self.capacity, self.used, q)

    def add(self, name: str, q: ResourceQuota) -> None:
        self.items.append(name)
        self.used = sum_quota([self.used, q])


class BinPacker:
    """First-Fit Decreasing 装箱器。"""

    def __init__(self, capacity: HostCapacity):
        self.capacity = capacity

    def pack(self, items: dict[str, ResourceQuota]) -> list[Bin]:
        """把 {name: quota} 装箱，返回宿主列表。"""
        ordered = sorted(items.items(), key=lambda kv: kv[1].memory_mb + kv[1].cpu_millis, reverse=True)
        bins: list[Bin] = []
        for name, q in ordered:
            placed = False
            for b in bins:
                if b.fits(q):
                    b.add(name, q)
                    placed = True
                    break
            if not placed:
                nb = Bin(capacity=self.capacity)
                nb.add(name, q)
                bins.append(nb)
        return bins

    def hosts_needed(self, items: dict[str, ResourceQuota]) -> int:
        """所需宿主数（用于容量规划 / 成本估算）。"""
        return len(self.pack(items))


__all__ = ["BinPacker", "Bin"]
