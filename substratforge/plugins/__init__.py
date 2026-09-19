# -*- coding: utf-8 -*-
"""插件系统：动态加载第三方沙箱后端 / 快照格式 / 驱逐策略 / 压缩器。

设计：插件是一个带 `setup(manager)` 入口的 Python 模块，通过
entry point 或目录扫描被发现，调用 setup 向对应 registry 注册实现。
"""
from .base import Plugin, PluginInfo
from .manager import PluginManager
from .loader import discover_plugins, load_plugin_module

__all__ = ["Plugin", "PluginInfo", "PluginManager", "discover_plugins", "load_plugin_module"]
