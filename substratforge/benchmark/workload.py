# -*- coding: utf-8 -*-
"""工作负载生成器：模拟不同特征的 agent 负载（长驻/短命/突发）。"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Workload:
    """一条工作负载描述。"""
    name: str
    command: list
    idle_seconds: float = 0.0


class WorkloadGenerator:
    """工作负载生成器。"""

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def long_running(self, n: int) -> list[Workload]:
        """长驻负载：模拟长期驻留的 agent。"""
        return [Workload(
            name=f"long-{i}",
            command=["python", "-c", "import time; time.sleep(86400)"],
            idle_seconds=self.rng.uniform(30, 300),
        ) for i in range(n)]

    def bursty(self, n: int) -> list[Workload]:
        """突发负载：短命但密集。"""
        return [Workload(
            name=f"burst-{i}",
            command=["python", "-c", "import time; time.sleep(1)"],
            idle_seconds=self.rng.uniform(0, 5),
        ) for i in range(n)]


__all__ = ["WorkloadGenerator", "Workload"]
