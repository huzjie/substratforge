# -*- coding: utf-8 -*-
"""内存存储：用于测试 / 演示，进程退出即失效。"""
from __future__ import annotations

from typing import Any, Optional

from ..types import StorageBackend
from .base import SnapshotStore


class MemoryStore(SnapshotStore):
    backend = StorageBackend.MEMORY

    def __init__(self):
        self._data: dict[str, bytes] = {}
        self._meta: dict[str, dict] = {}

    def put(self, snapshot_id: str, data: bytes, meta: dict[str, Any]) -> None:
        self._data[snapshot_id] = data
        self._meta[snapshot_id] = dict(meta)

    def get_bytes(self, snapshot_id: str) -> Optional[bytes]:
        return self._data.get(snapshot_id)

    def delete(self, snapshot_id: str) -> None:
        self._data.pop(snapshot_id, None)
        self._meta.pop(snapshot_id, None)

    def list(self) -> list[dict[str, Any]]:
        return list(self._meta.values())


from ..storage import store_registry  # noqa: E402

store_registry.register("memory", MemoryStore)

__all__ = ["MemoryStore"]
