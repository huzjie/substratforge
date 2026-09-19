# -*- coding: utf-8 -*-
"""生命周期钩子：在关键路径前后注入用户逻辑（告警、计费、自定义清理）。"""
from __future__ import annotations

from typing import Callable


class Hooks:
    """钩子注册与派发。"""

    EVENTS = (
        "before_spawn", "after_spawn",
        "before_suspend", "after_suspend",
        "before_resume", "after_resume",
        "before_destroy", "after_destroy",
    )

    def __init__(self):
        self._hooks: dict[str, list[Callable]] = {e: [] for e in self.EVENTS}

    def on(self, event: str, fn: Callable) -> None:
        if event not in self._hooks:
            raise ValueError(f"未知事件: {event}")
        self._hooks[event].append(fn)

    def emit(self, event: str, *args, **kwargs) -> None:
        for fn in self._hooks.get(event, []):
            fn(*args, **kwargs)


__all__ = ["Hooks"]
