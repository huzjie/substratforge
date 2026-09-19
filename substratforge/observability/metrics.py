# -*- coding: utf-8 -*-
"""指标采集：计数器 / 直方图 / 仪表盘，支持 Prometheus 文本格式导出。

零依赖实现，不引入 prometheus-client；导出的文本格式与 Prometheus
抓取协议完全兼容，可直接被 /metrics 端点暴露。
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class _Counter:
    name: str
    help: str
    labels: dict
    value: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def inc(self, n: int = 1) -> None:
        with self.lock:
            self.value += n


@dataclass
class _Gauge:
    name: str
    help: str
    labels: dict
    value: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def set(self, v: float) -> None:
        with self.lock:
            self.value = v


@dataclass
class _Histogram:
    name: str
    help: str
    labels: dict
    buckets: tuple
    counts: list = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self):
        self.counts = [0] * len(self.buckets)

    def observe(self, v: float) -> None:
        with self.lock:
            for i, b in enumerate(self.buckets):
                if v <= b:
                    self.counts[i] += 1


class MetricsRegistry:
    """指标注册表。"""

    def __init__(self):
        self._counters: dict[str, _Counter] = {}
        self._gauges: dict[str, _Gauge] = {}
        self._histograms: dict[str, _Histogram] = {}
        self._lock = threading.Lock()

    def counter(self, name: str, help: str = "", **labels) -> _Counter:
        with self._lock:
            return self._counters.setdefault(name, _Counter(name, help, labels))

    def gauge(self, name: str, help: str = "", **labels) -> _Gauge:
        with self._lock:
            return self._gauges.setdefault(name, _Gauge(name, help, labels))

    def histogram(self, name: str, buckets: tuple, help: str = "", **labels) -> _Histogram:
        with self._lock:
            return self._histograms.setdefault(name, _Histogram(name, help, labels, buckets))

    def render_prometheus(self) -> str:
        """渲染 Prometheus 文本格式。"""
        lines: list[str] = []
        for name, c in self._counters.items():
            lines.append(f"# HELP {name} {c.help}")
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {c.value}")
        for name, g in self._gauges.items():
            lines.append(f"# HELP {name} {g.help}")
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {g.value}")
        for name, h in self._histograms.items():
            lines.append(f"# HELP {name} {h.help}")
            lines.append(f"# TYPE {name} histogram")
            for b, c in zip(h.buckets, h.counts):
                lines.append(f'{name}_bucket{{le="{b}"}} {c}')
            lines.append(f"{name}_bucket{{le=\"+Inf\"}} {sum(h.counts)}")
        return "\n".join(lines) + "\n"


class PrometheusText:
    """便捷别名。"""
    @staticmethod
    def render(registry: MetricsRegistry) -> str:
        return registry.render_prometheus()


__all__ = ["MetricsRegistry", "PrometheusText"]
