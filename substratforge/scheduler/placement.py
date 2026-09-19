# -*- coding: utf-8 -*-
"""放置引擎：新沙箱落在哪个宿主 / 恢复时回到哪个宿主。

- 冷停靠（dormant）放置：优先落在「已有同租户 / 同标签」的宿主，利于去重
- 恢复放置：优先回到原宿主（快照本地命中），否则选负载最低宿主
"""
from __future__ import annotations

from typing import Optional

from ..types import SandboxSpec


class PlacementEngine:
    """放置决策。"""

    def __init__(self):
        self._hosts: dict[str, dict] = {}

    def register_host(self, host: str, labels: dict | None = None) -> None:
        self._hosts.setdefault(host, {"labels": labels or {}, "load": 0})

    def choose_for_spawn(self, spec: SandboxSpec) -> str:
        """为新沙箱选宿主：优先同标签、其次最低负载。"""
        best, best_score = "local", None
        for host, meta in self._hosts.items():
            overlap = len(set(meta["labels"].items()) & set(spec.labels.items()))
            score = (overlap, -meta["load"])
            if best_score is None or score > best_score:
                best, best_score = host, score
        return best

    def choose_for_resume(self, snapshot_host: Optional[str]) -> str:
        """为恢复选宿主：优先原宿主（快照本地命中）。"""
        if snapshot_host and snapshot_host in self._hosts:
            return snapshot_host
        if self._hosts:
            return min(self._hosts, key=lambda h: self._hosts[h]["load"])
        return "local"

    def bump_load(self, host: str, delta: int) -> None:
        if host in self._hosts:
            self._hosts[host]["load"] += delta


__all__ = ["PlacementEngine"]
