# -*- coding: utf-8 -*-
"""限流器：令牌桶，用于限制挂起/恢复操作速率，保护宿主。"""
from __future__ import annotations

import threading
import time


class TokenBucket:
    """令牌桶限流器。"""

    def __init__(self, rate: float, capacity: float):
        self.rate = rate              # 令牌/秒
        self.capacity = capacity      # 桶容量
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def allow(self, tokens: float = 1.0) -> bool:
        with self._lock:
            now = time.monotonic()
            self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
            self._last = now
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False


__all__ = ["TokenBucket"]
