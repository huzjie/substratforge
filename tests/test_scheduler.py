# -*- coding: utf-8 -*-
import time

from substratforge.scheduler.eviction import LRUEviction, get_policy
from substratforge.scheduler.packing import BinPacker
from substratforge.sandbox.quota import HostCapacity
from substratforge.types import ResourceQuota


def test_lru_eviction():
    entries = [("a", 1.0, 5), ("b", 2.0, 1), ("c", 3.0, 2)]
    evicted = LRUEviction().evict(entries, limit=1)
    assert evicted == ["a", "b"]


def test_bin_packing():
    cap = HostCapacity(memory_mb=512, cpu_millis=1000)
    items = {"x": ResourceQuota(memory_mb=300), "y": ResourceQuota(memory_mb=300)}
    bins = BinPacker(cap).pack(items)
    assert len(bins) == 2  # 每个 300MB，512MB 箱子只能各放一个


def test_get_policy():
    assert get_policy("lru").name.value == "lru"
