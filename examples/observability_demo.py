# -*- coding: utf-8 -*-
"""可观测性演示：指标 + 追踪。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge import Substrate
from substratforge.observability.metrics import MetricsRegistry
from substratforge.observability.tracing import Tracer


def main():
    reg = MetricsRegistry()
    suspends = reg.counter("substrate_suspends_total", help="total suspends")
    tracer = Tracer()

    s = Substrate.from_config({"storage": {"backend": "memory"}, "snapshot": {"compression": "gzip"}})
    name = "obs-demo"
    s.spawn(name, command=["python", "-c", "import time; time.sleep(86400)"])

    with tracer.context("suspend", sandbox=name):
        s.suspend(name)
    suspends.inc()

    with tracer.context("resume", sandbox=name):
        s.resume(name)

    s.destroy(name)
    print(reg.render_prometheus())
    for span in tracer.spans():
        print(f"{span.name}: {span.duration_ms}ms")


if __name__ == "__main__":
    main()
