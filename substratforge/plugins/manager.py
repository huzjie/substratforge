# -*- coding: utf-8 -*-
"""插件管理器：加载 / 卸载 / 列举插件。"""
from __future__ import annotations

from ..sandbox import backend_registry as sandbox_registry
from ..scheduler import policy_registry
from ..storage import store_registry
from .base import Plugin, PluginInfo


class PluginManager:
    """插件管理器。"""

    def __init__(self):
        self._plugins: dict[str, Plugin] = {}
        self.registries = {
            "sandbox": sandbox_registry,
            "eviction": policy_registry,
            "storage": store_registry,
        }

    def register_plugin(self, plugin: Plugin) -> None:
        """加载一个插件（调用其 setup）。"""
        plugin.setup(self)
        self._plugins[plugin.info.name] = plugin

    def unload(self, name: str) -> None:
        self._plugins.pop(name, None)

    def list(self) -> list[PluginInfo]:
        return [p.info for p in self._plugins.values()]


__all__ = ["PluginManager"]
