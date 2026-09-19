# -*- coding: utf-8 -*-
"""快照引擎：编排内存捕获 + 文件系统打包 + 增量 + 压缩 + 存取。"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..errors import SnapshotError
from ..sandbox.base import SandboxHandle
from ..types import SnapshotFormat, SnapshotInfo, new_id, now
from ..utils import ensure_dir, sha256_bytes, json_dumps_compact
from .compress import Compressor
from .delta import DeltaEncoder
from .fs import FilesystemLayer
from .mem import MemoryCapture


class SnapshotEngine:
    """快照引擎。"""

    def __init__(
        self,
        snapshot_dir: str | Path,
        storage=None,
        format: SnapshotFormat = SnapshotFormat.TAR,
        compression: str = "zstd",
        delta: bool = True,
    ):
        self.snapshot_dir = ensure_dir(Path(snapshot_dir))
        self.storage = storage
        self.format = format
        self.compressor = Compressor(compression)
        self.delta_enabled = delta
        self.fs = FilesystemLayer()
        self.mem = MemoryCapture()

    def capture(self, handle: SandboxHandle, tags: dict[str, str] | None = None,
                parent_id: str | None = None) -> SnapshotInfo:
        """采集一个沙箱的完整快照。"""
        t0 = time.perf_counter()
        fs_root = handle.fs_root
        if fs_root is None or not fs_root.exists():
            raise SnapshotError(f"沙箱 {handle.sandbox_id} 缺少文件系统根，无法快照")

        # 1. 内存 / 进程元信息
        mem_bytes = self.mem.capture(handle)
        # 2. 文件系统打包（tar）
        fs_bytes = self.fs.tar(fs_root)
        # 3. 组装 manifest
        manifest = {
            "version": 1,
            "sandbox_id": handle.sandbox_id,
            "spec": handle.spec.as_dict(),
            "memory": self.mem.meta(handle),
            "captured_at": now(),
            "tags": tags or {},
        }
        manifest_bytes = json_dumps_compact(manifest).encode("utf-8")

        # 4. 三部分拼接成一个归档
        raw = self._bundle(manifest_bytes, mem_bytes, fs_bytes)

        # 5. 增量编码（相对父快照只存差异）
        parent_bytes = b""
        if self.delta_enabled and parent_id and self.storage:
            parent_bytes = self.storage.get_bytes(parent_id) or b""
        encoded = DeltaEncoder.encode(raw, parent_bytes) if parent_bytes else raw

        # 6. 压缩
        compressed = self.compressor.compress(encoded)

        info = SnapshotInfo(
            id=new_id("snap-"),
            sandbox_id=handle.sandbox_id,
            size_bytes=len(raw),
            compressed_bytes=len(compressed),
            format=self.format,
            parent_id=parent_id if parent_bytes else None,
            checksum=sha256_bytes(compressed),
            tags=tags or {},
        )

        # 7. 落盘（本地或外部存储）
        if self.storage:
            self.storage.put(info.id, compressed, info.as_dict())
        else:
            (self.snapshot_dir / f"{info.id}.snap").write_bytes(compressed)

        info.meta = {"capture_ms": round((time.perf_counter() - t0) * 1000, 2)}
        return info

    def restore(self, info: SnapshotInfo) -> tuple[dict[str, Any], bytes]:
        """还原快照为 (manifest, filesystem_bytes)。"""
        if self.storage:
            compressed = self.storage.get_bytes(info.id)
        else:
            compressed = (self.snapshot_dir / f"{info.id}.snap").read_bytes()
        if compressed is None:
            raise SnapshotError(f"快照 {info.id} 不存在")
        encoded = self.compressor.decompress(compressed)
        raw = encoded
        if info.parent_id:
            if self.storage:
                parent_bytes = self.storage.get_bytes(info.parent_id) or b""
            else:
                parent_bytes = (self.snapshot_dir / f"{info.parent_id}.snap").read_bytes()
            raw = DeltaEncoder.decode(encoded, parent_bytes)
        manifest_bytes, mem_bytes, fs_bytes = self._unbundle(raw)
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        return manifest, fs_bytes

    def materialize(self, info: SnapshotInfo, target: Path) -> dict[str, Any]:
        """把快照还原到目标目录（供重新拉起沙箱）。"""
        manifest, fs_bytes = self.restore(info)
        self.fs.untar(fs_bytes, target)
        return manifest

    # ---- 归档布局 ----
    def _bundle(self, manifest: bytes, mem: bytes, fs: bytes) -> bytes:
        parts = [manifest, mem, fs]
        header = b"".join(len(p).to_bytes(8, "big") for p in parts)
        return header + b"".join(parts)

    def _unbundle(self, raw: bytes) -> tuple[bytes, bytes, bytes]:
        if len(raw) < 24:
            raise SnapshotError("快照归档损坏：头部过短")
        sizes = [int.from_bytes(raw[i:i + 8], "big") for i in range(0, 24, 8)]
        off = 24
        out = []
        for sz in sizes:
            out.append(raw[off:off + sz])
            off += sz
        return out[0], out[1], out[2]


__all__ = ["SnapshotEngine"]
