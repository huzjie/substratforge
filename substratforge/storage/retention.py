# -*- coding: utf-8 -*-
"""保留策略：决定哪些快照可删除。"""
from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class RetentionPolicy:
    """保留策略。"""
    keep_latest: int = 10
    keep_hourly: int = 24
    keep_daily: int = 7
    max_age_seconds: float | None = None

    def decide(self, meta: list[dict]) -> list[str]:
        """返回可删除的快照 id 列表。"""
        now = time.time()
        keep = set()
        for m in sorted(meta, key=lambda x: x.get("created_at", 0), reverse=True)[:self.keep_latest]:
            keep.add(m["id"])
        to_delete = []
        for m in meta:
            sid = m["id"]
            if sid in keep:
                continue
            if self.max_age_seconds is not None:
                if now - m.get("created_at", now) > self.max_age_seconds:
                    to_delete.append(sid)
        return to_delete


__all__ = ["RetentionPolicy"]
