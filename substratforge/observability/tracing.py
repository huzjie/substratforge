# -*- coding: utf-8 -*-
"""轻量追踪：为挂起/恢复等关键路径打 span，产出树状耗时。

零依赖；生产可对接 OpenTelemetry（见 docs/observability-otel.md），
本模块提供语义等价的最小实现，方便本地可视化分析瓶颈。
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Span:
    """一个追踪区间。"""
    name: str
    trace_id: str
    parent_id: Optional[str] = None
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    start: float = field(default_factory=time.perf_counter)
    end: Optional[float] = None
    attrs: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        if self.end is None:
            return 0.0
        return (self.end - self.start) * 1000

    def as_dict(self) -> dict:
        return {
            "name": self.name, "trace_id": self.trace_id, "span_id": self.span_id,
            "parent_id": self.parent_id, "duration_ms": round(self.duration_ms, 2),
            "attrs": self.attrs,
        }


class Tracer:
    """追踪器。"""

    def __init__(self):
        self._stack: list[Span] = []
        self._spans: list[Span] = []

    def start(self, name: str, **attrs) -> Span:
        parent = self._stack[-1] if self._stack else None
        span = Span(name=name, trace_id=parent.trace_id if parent else uuid.uuid4().hex,
                    parent_id=parent.span_id if parent else None)
        span.attrs.update(attrs)
        self._stack.append(span)
        return span

    def end(self, span: Span) -> Span:
        if self._stack and self._stack[-1] is span:
            self._stack.pop()
        span.end = time.perf_counter()
        self._spans.append(span)
        return span

    def context(self, name: str, **attrs):
        """上下文管理器用法：with tracer.context("suspend", id=...): ..."""
        from contextlib import contextmanager

        @contextmanager
        def _cm():
            sp = self.start(name, **attrs)
            try:
                yield sp
            finally:
                self.end(sp)
        return _cm()

    def spans(self) -> list[Span]:
        return list(self._spans)


__all__ = ["Tracer", "Span"]
