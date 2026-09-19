# -*- coding: utf-8 -*-
"""示例驱逐策略插件：随机驱逐（演示用）。"""
import random

from ...types import EvictionPolicy


class RandomEviction:
    """随机淘汰。"""
    name = EvictionPolicy.NONE

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def evict(self, entries, limit: int):
        ents = list(entries)
        self.rng.shuffle(ents)
        return [e[0] for e in ents[:max(0, len(ents) - limit)]]


def setup(manager):
    from ...scheduler import policy_registry
    policy_registry.register("random", RandomEviction())


__all__ = ["RandomEviction", "setup"]
