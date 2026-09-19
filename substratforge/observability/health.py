# -*- coding: utf-8 -*-
"""健康检查：汇总各子系统的健康状态。"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class ComponentHealth:
    """单个组件的健康状态。"""
    name: str
    status: HealthStatus
    detail: str = ""


class HealthChecker:
    """健康检查器。"""

    def __init__(self):
        self._checks: list = []

    def register(self, name: str, fn) -> None:
        self._checks.append((name, fn))

    def check_all(self) -> dict:
        out = {"status": HealthStatus.OK.value, "components": {}}
        any_down = False
        for name, fn in self._checks:
            try:
                detail = fn()
                status = HealthStatus.OK.value
            except Exception as exc:  # noqa: BLE001
                detail = str(exc)
                status = HealthStatus.DOWN.value
                any_down = True
            out["components"][name] = {"status": status, "detail": detail}
        if any_down:
            out["status"] = HealthStatus.DOWN.value
        return out


__all__ = ["HealthChecker", "HealthStatus", "ComponentHealth"]
