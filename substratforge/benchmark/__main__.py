# -*- coding: utf-8 -*-
"""``python -m substratforge.benchmark`` 入口：跑全套基准。"""
import sys

from .. import Substrate
from .density import DensityBenchmark
from .latency import LatencyBenchmark
from .report import ReportGenerator
from .throughput import ThroughputBenchmark


def main() -> int:
    s = Substrate.from_config()
    results = []

    def _run(name, bench):
        r = bench.run()
        results.append(type("R", (), {
            "name": name, "duration_seconds": 0.0,
            "metrics": r, "passed": True, "error": "",
            "as_dict": lambda self, r=r: {"name": self.name, "metrics": r},
        })())
        return r

    print("[benchmark] density ...")
    print(_run("density", DensityBenchmark(s, n=20)))
    print("[benchmark] latency ...")
    print(_run("latency", LatencyBenchmark(s, iterations=20)))
    print("[benchmark] throughput ...")
    print(_run("throughput", ThroughputBenchmark(s, duration_seconds=3.0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
