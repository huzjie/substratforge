# -*- coding: utf-8 -*-
"""延迟基准：单个沙箱反复挂起/恢复的延迟分布。"""
from __future__ import annotations

import statistics
import time


class LatencyBenchmark:
    """延迟基准。"""

    def __init__(self, substrate, iterations: int = 50):
        self.substrate = substrate
        self.iterations = iterations

    def run(self) -> dict:
        s = self.substrate
        name = "latency-probe"
        s.spawn(name, command=["python", "-c", "import time; time.sleep(86400)"])

        suspends, resumes = [], []
        for _ in range(self.iterations):
            t0 = time.perf_counter()
            s.suspend(name)
            suspends.append((time.perf_counter() - t0) * 1000)

            t1 = time.perf_counter()
            s.resume(name)
            resumes.append((time.perf_counter() - t1) * 1000)

        s.destroy(name)

        return {
            "iterations": self.iterations,
            "suspend_p50_ms": round(statistics.median(suspends), 2),
            "suspend_p95_ms": round(sorted(suspends)[int(self.iterations * 0.95) - 1], 2),
            "resume_p50_ms": round(statistics.median(resumes), 2),
            "resume_p95_ms": round(sorted(resumes)[int(self.iterations * 0.95) - 1], 2),
        }


__all__ = ["LatencyBenchmark"]
