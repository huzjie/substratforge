# -*- coding: utf-8 -*-
"""晋升引擎：把冷态沙箱（SUSPENDED）恢复到活跃，受 resume 预算约束。

恢复预算（resume_budget_ms）是 Agent Substrate 的核心 SLA：保证恢复在
亚秒级完成。引擎会测量每次恢复耗时，超预算时记录告警并给出优化建议。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from ..types import new_id


@dataclass
class PromotionResult:
    """一次晋升的结果。"""
    sandbox_id: str
    resumed_ms: float
    within_budget: bool
    snapshot_id: str = ""


class PromotionEngine:
    """冷 -> 热晋升。"""

    def __init__(self, resume_budget_ms: int = 500, restore_fn: Callable | None = None):
        self.resume_budget_ms = resume_budget_ms
        self.restore_fn = restore_fn
        self.history: list[PromotionResult] = []

    def promote(self, sandbox_id: str, snapshot_id: str) -> PromotionResult:
        """执行晋升（调用外部 restore_fn），记录耗时与预算合规性。"""
        t0 = time.perf_counter()
        if self.restore_fn:
            self.restore_fn(sandbox_id, snapshot_id)
        ms = (time.perf_counter() - t0) * 1000
        res = PromotionResult(
            sandbox_id=sandbox_id,
            resumed_ms=round(ms, 2),
            within_budget=ms <= self.resume_budget_ms,
            snapshot_id=snapshot_id,
        )
        self.history.append(res)
        return res

    @property
    def avg_resume_ms(self) -> float:
        if not self.history:
            return 0.0
        return round(sum(r.resumed_ms for r in self.history) / len(self.history), 2)

    @property
    def budget_violations(self) -> int:
        return sum(1 for r in self.history if not r.within_budget)


__all__ = ["PromotionEngine", "PromotionResult"]
