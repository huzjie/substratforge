# -*- coding: utf-8 -*-
"""运行时限额：并发恢复数、恢复速率等宿主保护限额。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeLimits:
    """运行时限额。"""
    max_concurrent_resumes: int = 8
    max_concurrent_suspends: int = 8
    max_snapshots_per_sandbox: int = 32
    max_task_queue: int = 4096

    def as_dict(self) -> dict:
        return {
            "max_concurrent_resumes": self.max_concurrent_resumes,
            "max_concurrent_suspends": self.max_concurrent_suspends,
            "max_snapshots_per_sandbox": self.max_snapshots_per_sandbox,
            "max_task_queue": self.max_task_queue,
        }


__all__ = ["RuntimeLimits"]
