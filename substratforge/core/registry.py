# -*- coding: utf-8 -*-
"""通用组件注册表：按名登记后端实现，运行时按配置实例化。

沙箱后端、存储后端、驱逐策略都走同一套注册机制，扩展新后端只需
``@register("name")`` 装饰一个类。
"""
from __future__ import annotations

from typing import Any, Callable, TypeVar, Generic, Type

from ..errors import ConfigurationError

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self, kind: str):
        self.kind = kind
        self._entries: dict[str, T] = {}

    def register(self, name: str, factory: T) -> T:
        self._entries[name] = factory
        return factory

    def get(self, name: str) -> T:
        if name not in self._entries:
            raise ConfigurationError(
                f"未注册的 {self.kind} 后端: {name!r}，可用: {sorted(self._entries)}"
            )
        return self._entries[name]

    def names(self) -> list[str]:
        return sorted(self._entries)

    def __contains__(self, name: str) -> bool:
        return name in self._entries


def make_registry(kind: str) -> Registry:
    return Registry(kind)


__all__ = ["Registry", "make_registry"]
