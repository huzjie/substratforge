# -*- coding: utf-8 -*-
"""吞吐基准：单位时间内的挂起/恢复操作数。"""
from __future__ import annotations

import time


class ThroughputBenchmark:
    """吞吐基准。"""

    def __init__(self, substrate, duration_seconds: float = 5.0):
        self.substrate = substrate
        self.duration = duration_seconds

    def run(self) -> dict:
        s = self.substrate
        name = "throughput-probe"
        s.spawn(name, command=["python", "-c", "import time; time.sleep(86400)"])

        ops = 0
        deadline = time.perf_counter() + self.duration
        while time.perf_counter() < deadline:
            s.suspend(name)
            s.resume(name)
            ops += 1
        s.destroy(name)

        return {
            "duration_seconds": self.duration,
            "ops": ops,
            "ops_per_second": round(ops / self.duration, 1),
        }


__all__ = ["ThroughputBenchmark"]
