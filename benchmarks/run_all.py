# -*- coding: utf-8 -*-
"""一键跑全套基准并输出 Markdown 报告。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge import Substrate
from substratforge.benchmark import (
    DensityBenchmark, LatencyBenchmark, ThroughputBenchmark, ReportGenerator,
)


def main():
    s = Substrate.from_config()
    results = []
    for name, bench in [
        ("density", DensityBenchmark(s, n=20)),
        ("latency", LatencyBenchmark(s, iterations=20)),
        ("throughput", ThroughputBenchmark(s, duration_seconds=3.0)),
    ]:
        print(f"[benchmark] {name} ...")
        m = bench.run()
        results.append(type("R", (), {
            "name": name, "duration_seconds": 0.0, "metrics": m,
            "passed": True, "error": "", "as_dict": lambda self, m=m: {"name": self.name, "metrics": m},
        })())
    print()
    print(ReportGenerator.to_markdown(results))


if __name__ == "__main__":
    main()
