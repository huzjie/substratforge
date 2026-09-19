# -*- coding: utf-8 -*-
"""存储后端抽象基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class SnapshotStore(ABC):
    """快照仓库接口。"""

    @abstractmethod
    def put(self, snapshot_id: str, data: bytes, meta: dict[str, Any]) -> None:
        """写入快照。"""

    @abstractmethod
    def get_bytes(self, snapshot_id: str) -> Optional[bytes]:
        """读取快照字节，不存在返回 None。"""

    @abstractmethod
    def delete(self, snapshot_id: str) -> None:
        """删除快照。"""

    @abstractmethod
    def list(self) -> list[dict[str, Any]]:
        """列举快照元信息。"""

    def exists(self, snapshot_id: str) -> bool:
        return self.get_bytes(snapshot_id) is not None


__all__ = ["SnapshotStore"]
