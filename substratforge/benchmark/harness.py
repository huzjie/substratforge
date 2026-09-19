# -*- coding: utf-8 -*-
"""基准运行器：串行跑多个基准，聚合结果。"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BenchmarkResult:
    """单个基准的结果。"""
    name: str
    duration_seconds: float
    metrics: dict[str, Any] = field(default_factory=dict)
    passed: bool = True
    error: str = ""

    def as_dict(self) -> dict:
        return {
            "name": self.name, "duration_seconds": round(self.duration_seconds, 3),
            "metrics": self.metrics, "passed": self.passed, "error": self.error,
        }


class BenchmarkHarness:
    """基准运行器。"""

    def __init__(self):
        self._benchmarks: list = []

    def register(self, name: str, fn) -> None:
        self._benchmarks.append((name, fn))

    def run_all(self) -> list[BenchmarkResult]:
        results = []
        for name, fn in self._benchmarks:
            t0 = time.perf_counter()
            try:
                metrics = fn()
                results.append(BenchmarkResult(
                    name=name, duration_seconds=time.perf_counter() - t0,
                    metrics=metrics, passed=True,
                ))
            except Exception as exc:  # noqa: BLE001
                results.append(BenchmarkResult(
                    name=name, duration_seconds=time.perf_counter() - t0,
                    passed=False, error=str(exc),
                ))
        return results


__all__ = ["BenchmarkHarness", "BenchmarkResult"]
