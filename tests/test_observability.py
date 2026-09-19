# -*- coding: utf-8 -*-
from substratforge.observability.metrics import MetricsRegistry
from substratforge.observability.tracing import Tracer
from substratforge.observability.health import HealthChecker


def test_metrics_prometheus():
    reg = MetricsRegistry()
    reg.counter("substrate_suspends_total", help="total suspends").inc()
    out = reg.render_prometheus()
    assert "substrate_suspends_total 1" in out


def test_tracer():
    t = Tracer()
    with t.context("suspend", id="x"):
        pass
    assert len(t.spans()) == 1
    assert t.spans()[0].name == "suspend"


def test_health():
    hc = HealthChecker()
    hc.register("store", lambda: "ok")
    assert hc.check_all()["status"] == "ok"
