# -*- coding: utf-8 -*-
"""本地文件系统存储：快照存为一个文件 + 一个 .meta.json。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from ..errors import StorageError
from ..types import StorageBackend
from ..utils import ensure_dir
from .base import SnapshotStore


class LocalStore(SnapshotStore):
    backend = StorageBackend.LOCAL

    def __init__(self, root: str | Path):
        self.root = ensure_dir(Path(root))

    def _data_path(self, sid: str) -> Path:
        return self.root / f"{sid}.snap"

    def _meta_path(self, sid: str) -> Path:
        return self.root / f"{sid}.meta.json"

    def put(self, snapshot_id: str, data: bytes, meta: dict[str, Any]) -> None:
        try:
            self._data_path(snapshot_id).write_bytes(data)
            self._meta_path(snapshot_id).write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"本地写入失败: {exc}") from exc

    def get_bytes(self, snapshot_id: str) -> Optional[bytes]:
        p = self._data_path(snapshot_id)
        if not p.exists():
            return None
        return p.read_bytes()

    def delete(self, snapshot_id: str) -> None:
        for p in (self._data_path(snapshot_id), self._meta_path(snapshot_id)):
            p.unlink(missing_ok=True)

    def list(self) -> list[dict[str, Any]]:
        out = []
        for mp in sorted(self.root.glob("*.meta.json")):
            try:
                out.append(json.loads(mp.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue
        return out


from ..storage import store_registry  # noqa: E402

store_registry.register("local", LocalStore)

__all__ = ["LocalStore"]
