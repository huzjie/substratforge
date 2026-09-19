# -*- coding: utf-8 -*-
"""内容寻址存储：按 sha256 存块，跨快照自动去重。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..errors import StorageError
from ..utils import ensure_dir


class ContentAddressedStore:
    """CAS：对象按哈希命名，快照是对象引用列表。"""

    def __init__(self, root: str | Path):
        self.root = ensure_dir(Path(root))
        self.objects = self.root / "objects"
        ensure_dir(self.objects)

    def _oid(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def put_blob(self, data: bytes) -> str:
        oid = self._oid(data)
        path = self.objects / oid
        if not path.exists():
            path.write_bytes(data)
        return oid

    def get_blob(self, oid: str) -> bytes:
        path = self.objects / oid
        if not path.exists():
            raise StorageError(f"对象不存在: {oid}")
        return path.read_bytes()

    def put_snapshot(self, snapshot_id: str, data: bytes, chunk: int = 65536) -> list[str]:
        """把快照数据按块存入 CAS，返回块引用列表。"""
        refs = [self.put_blob(data[i:i + chunk]) for i in range(0, len(data), chunk)]
        (self.root / f"{snapshot_id}.refs").write_text(json.dumps(refs))
        return refs

    def get_snapshot(self, snapshot_id: str) -> bytes:
        refs_file = self.root / f"{snapshot_id}.refs"
        if not refs_file.exists():
            raise StorageError(f"快照不存在: {snapshot_id}")
        refs = json.loads(refs_file.read_text())
        return b"".join(self.get_blob(r) for r in refs)


__all__ = ["ContentAddressedStore"]
