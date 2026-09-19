# -*- coding: utf-8 -*-
"""遥测事件：结构化记录关键路径事件，供指标/追踪消费。"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class TelemetryEvent:
    """一条遥测事件。"""
    name: str
    ts: float = field(default_factory=time.time)
    attrs: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"name": self.name, "ts": self.ts, "attrs": self.attrs}


class Telemetry:
    """遥测收集器。"""

    def __init__(self):
        self._events: list[TelemetryEvent] = []

    def record(self, name: str, **attrs) -> None:
        self._events.append(TelemetryEvent(name=name, attrs=attrs))

    def drain(self) -> list[dict]:
        events = [e.as_dict() for e in self._events]
        self._events.clear()
        return events

    def __len__(self) -> int:
        return len(self._events)


__all__ = ["Telemetry", "TelemetryEvent"]
