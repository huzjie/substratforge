# -*- coding: utf-8 -*-
from substratforge import Substrate
from substratforge.benchmark.density import DensityBenchmark


def test_density_benchmark(tmp_path):
    s = Substrate.from_config({
        "sandbox": {"root_dir": str(tmp_path / "sb")},
        "storage": {"backend": "memory"},
        "snapshot": {"compression": "gzip"},
    })
    r = DensityBenchmark(s, n=3).run()
    assert r["sandboxes"] == 3
    assert r["suspend_avg_ms"] >= 0
