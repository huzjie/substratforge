# -*- coding: utf-8 -*-
"""沙箱后端包：进程级 / gVisor / microVM 三档隔离。

通过 :func:`get_backend` 按隔离等级取后端；后端在此包的
子模块导入时自动注册到全局 registry。
"""
from __future__ import annotations

from ..core.registry import make_registry
from ..types import IsolationLevel

backend_registry = make_registry("sandbox")


def get_backend(level: IsolationLevel | str):
    """按隔离等级返回沙箱后端。"""
    name = level.value if isinstance(level, IsolationLevel) else level
    return backend_registry.get(name)


# 导入以触发注册（顺序无碍，但先注册最通用的 process）
from . import process  # noqa: E402,F401
from . import gvisor  # noqa: E402,F401
from . import microvm  # noqa: E402,F401

__all__ = ["get_backend", "backend_registry"]
