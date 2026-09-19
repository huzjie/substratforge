# -*- coding: utf-8 -*-
"""SLA 校验：挂起/恢复延迟是否满足预算。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SLAResult:
    """SLA 校验结果。"""
    name: str
    observed_ms: float
    budget_ms: float
    passed: bool

    def as_dict(self) -> dict:
        return {
            "name": self.name, "observed_ms": self.observed_ms,
            "budget_ms": self.budget_ms, "passed": self.passed,
        }


class SLA:
    """SLA 规则集合。"""

    def __init__(self, resume_budget_ms: int = 500, suspend_budget_ms: int = 1000):
        self.resume_budget_ms = resume_budget_ms
        self.suspend_budget_ms = suspend_budget_ms

    def check_resume(self, observed_ms: float) -> SLAResult:
        return SLAResult("resume", round(observed_ms, 2), self.resume_budget_ms,
                         observed_ms <= self.resume_budget_ms)

    def check_suspend(self, observed_ms: float) -> SLAResult:
        return SLAResult("suspend", round(observed_ms, 2), self.suspend_budget_ms,
                         observed_ms <= self.suspend_budget_ms)


__all__ = ["SLA", "SLAResult"]
