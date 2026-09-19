# -*- coding: utf-8 -*-
"""密度基准：测量单机可停靠的休眠环境数 + 挂起/恢复耗时。"""
from __future__ import annotations

import time

from ..types import SandboxSpec


class DensityBenchmark:
    """密度基准。"""

    def __init__(self, substrate, n: int = 20):
        self.substrate = substrate
        self.n = n

    def run(self) -> dict:
        s = self.substrate
        names = [f"density-{i}" for i in range(self.n)]
        for n in names:
            s.spawn(n, command=["python", "-c", "import time; time.sleep(86400)"])

        t0 = time.perf_counter()
        for n in names:
            s.suspend(n)
        suspend_total = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        for n in names:
            s.resume(n)
        resume_total = (time.perf_counter() - t1) * 1000

        for n in names:
            s.destroy(n)

        return {
            "sandboxes": self.n,
            "suspend_total_ms": round(suspend_total, 1),
            "suspend_avg_ms": round(suspend_total / self.n, 2),
            "resume_total_ms": round(resume_total, 1),
            "resume_avg_ms": round(resume_total / self.n, 2),
            "density_per_host": self.n,
        }


__all__ = ["DensityBenchmark"]
