# -*- coding: utf-8 -*-
"""驱逐策略：冷停靠区（suspended）超限时，按策略挑选要真正删除的快照。

策略接口：``evict(entries, limit) -> list[entry_id]``
entries 为 [(id, last_access, access_count)]。
"""
from __future__ import annotations

from typing import Iterable, Sequence

from ..core.registry import make_registry
from ..types import EvictionPolicy

policy_registry = make_registry("eviction_policy")


class _Entry:
    __slots__ = ("id", "last_access", "count")

    def __init__(self, eid: str, last_access: float, count: int):
        self.id = eid
        self.last_access = last_access
        self.count = count


def _to_entries(entries: Sequence[tuple]) -> list[_Entry]:
    return [_Entry(e[0], float(e[1]), int(e[2]) if len(e) > 2 else 0) for e in entries]


class LRUEviction:
    """最近最少使用：淘汰 last_access 最久远的。"""
    name = EvictionPolicy.LRU

    def evict(self, entries: Sequence[tuple], limit: int) -> list[str]:
        ents = sorted(_to_entries(entries), key=lambda e: e.last_access)
        return [e.id for e in ents[:max(0, len(ents) - limit)]]


class LFUEviction:
    """最不常使用：淘汰访问次数最少的。"""
    name = EvictionPolicy.LFU

    def evict(self, entries: Sequence[tuple], limit: int) -> list[str]:
        ents = sorted(_to_entries(entries), key=lambda e: (e.count, e.last_access))
        return [e.id for e in ents[:max(0, len(ents) - limit)]]


class FIFOEviction:
    """先进先出：淘汰创建最早的（以 last_access 近似）。"""
    name = EvictionPolicy.FIFO

    def evict(self, entries: Sequence[tuple], limit: int) -> list[str]:
        ents = sorted(_to_entries(entries), key=lambda e: e.last_access)
        return [e.id for e in ents[:max(0, len(ents) - limit)]]


class NoEviction:
    """不驱逐（允许无限增长，仅当显式配置时）。"""
    name = EvictionPolicy.NONE

    def evict(self, entries: Sequence[tuple], limit: int) -> list[str]:
        return []


for _cls in (LRUEviction, LFUEviction, FIFOEviction, NoEviction):
    policy_registry.register(_cls.name.value, _cls())


def get_policy(name: str):
    return policy_registry.get(name if isinstance(name, str) else name.value)


__all__ = ["LRUEviction", "LFUEviction", "FIFOEviction", "NoEviction", "get_policy", "policy_registry"]
