# -*- coding: utf-8 -*-
"""插件基类与元信息。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PluginInfo:
    """插件元信息。"""
    name: str
    version: str = "0.0.0"
    description: str = ""
    kind: str = "unknown"          # sandbox | snapshot | eviction | compressor
    entry_point: str = ""          # "module:attr"
    meta: dict[str, Any] = field(default_factory=dict)


class Plugin:
    """插件基类：子类实现 ``setup`` 完成注册。"""

    info: PluginInfo

    def setup(self, manager) -> None:
        """注册插件实现到 manager。"""
        raise NotImplementedError


__all__ = ["Plugin", "PluginInfo"]
