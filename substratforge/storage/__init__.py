# -*- coding: utf-8 -*-
"""快照仓库：把快照字节存到本地 / S3 / MinIO，带 GC。

统一接口 :class:`SnapshotStore`：

- put(snapshot_id, bytes, meta)     写入一条快照
- get_bytes(snapshot_id) -> bytes   读取快照字节
- delete(snapshot_id)               删除
- list() -> [meta]                  列举

通过 registry 按 ``storage.backend`` 配置取值。
"""
from ..core.registry import make_registry
from ..types import StorageBackend

store_registry = make_registry("storage")

from .base import SnapshotStore  # noqa: E402,F401
from .local import LocalStore  # noqa: E402,F401
from .memory import MemoryStore  # noqa: E402,F401
from .s3 import S3Store, MinioStore  # noqa: E402,F401
from .gc import GarbageCollector  # noqa: E402,F401

__all__ = [
    "SnapshotStore", "LocalStore", "MemoryStore", "S3Store", "MinioStore",
    "GarbageCollector", "store_registry",
]
