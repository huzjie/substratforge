# -*- coding: utf-8 -*-
"""为保持向后兼容提供的包级注册表别名。

（沙箱 / 存储 / 策略注册表实际定义在各子包中，这里汇总暴露，
便于 ``from substratforge import backend_registry`` 直接访问。）
"""
from .sandbox import backend_registry as sandbox_registry

__all__ = ["sandbox_registry"]
