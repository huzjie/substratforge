# -*- coding: utf-8 -*-
"""垃圾回收：清理未被任何沙箱引用的孤儿快照，以及超过保留策略的旧快照。

策略：
- keep 条最新快照之外的旧快照标记可回收
- 被调度器 `suspended` 引用的快照永不回收
- 增量链的父快照保留（避免断链）
"""
from __future__ import annotations

import time
from typing import Iterable


class GarbageCollector:
    """快照 GC。"""

    def __init__(self, keep: int = 32, max_age_seconds: float | None = None):
        self.keep = keep
        self.max_age_seconds = max_age_seconds

    def collect(
        self,
        all_meta: list[dict],
        referenced_ids: Iterable[str],
    ) -> list[str]:
        """返回可回收的快照 id 列表（不真正删除，由调用方执行）。"""
        refs = set(referenced_ids)
        # 收集父链引用
        protected = set(refs)
        for m in all_meta:
            if m.get("id") in refs and m.get("parent_id"):
                protected.add(m["parent_id"])

        now = time.time()
        candidates = []
        for m in sorted(all_meta, key=lambda x: x.get("created_at", 0), reverse=True):
            sid = m.get("id")
            if sid in protected:
                continue
            candidates.append(m)

        to_collect = []
        # 保留最新 keep 条
        for m in candidates[self.keep:]:
            to_collect.append(m["id"])
        # 超龄回收
        if self.max_age_seconds is not None:
            for m in candidates:
                age = now - m.get("created_at", now)
                if age > self.max_age_seconds and m["id"] not in to_collect:
                    to_collect.append(m["id"])
        return to_collect


__all__ = ["GarbageCollector"]
