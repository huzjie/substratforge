# -*- coding: utf-8 -*-
"""增量快照编码：相对父快照只存差异。

采用「分块 + 滑动窗口」式的简单实现：把待存内容按固定块切分，
与父内容做块级对比，仅保留变化块与索引；父内容里已有的块用
哈希引用。这是 rsync 风格的增量，足够演示挂起/恢复的存储压缩，
生产可替换为内容寻址存储（CAS，见 docs/snapshot-cas.md）。
"""
from __future__ import annotations

import hashlib
import struct

CHUNK = 64 * 1024  # 64KB 分块

_MAGIC = b"SSDELTA1"


class DeltaEncoder:
    """块级增量编码 / 解码。"""

    @staticmethod
    def _chunks(data: bytes) -> list[bytes]:
        return [data[i:i + CHUNK] for i in range(0, len(data), CHUNK)]

    @staticmethod
    def encode(new: bytes, parent: bytes) -> bytes:
        """编码：输出 magic + 块表 + 差异块。"""
        parent_chunks = DeltaEncoder._chunks(parent)
        parent_hashes: dict[str, int] = {}
        for idx, ch in enumerate(parent_chunks):
            parent_hashes.setdefault(hashlib.sha256(ch).digest(), idx)

        new_chunks = DeltaEncoder._chunks(new)
        out = io = bytearray(_MAGIC)
        out += struct.pack(">I", len(parent_chunks))
        out += struct.pack(">I", len(new_chunks))

        refs: list[int] = []
        diff_blocks: list[bytes] = []
        for ch in new_chunks:
            h = hashlib.sha256(ch).digest()
            if h in parent_hashes:
                refs.append(parent_hashes[h])
            else:
                refs.append(-1)
                diff_blocks.append(ch)

        for r in refs:
            out += struct.pack(">i", r)
        for blk in diff_blocks:
            out += struct.pack(">I", len(blk)) + blk
        return bytes(out)

    @staticmethod
    def decode(delta: bytes, parent: bytes) -> bytes:
        """解码：依据引用表 + 差异块还原完整内容。"""
        if not delta.startswith(_MAGIC):
            raise ValueError("非法增量快照")
        off = len(_MAGIC)
        n_parent, n_new = struct.unpack(">II", delta[off:off + 8])
        off += 8
        refs = list(struct.unpack(f">{n_new}i", delta[off:off + 4 * n_new]))
        off += 4 * n_new

        parent_chunks = DeltaEncoder._chunks(parent)
        diff_blocks: list[bytes] = []
        while off < len(delta):
            (blen,) = struct.unpack(">I", delta[off:off + 4])
            off += 4
            diff_blocks.append(delta[off:off + blen])
            off += blen

        out = bytearray()
        di = 0
        for r in refs:
            if r >= 0:
                out += parent_chunks[r]
            else:
                out += diff_blocks[di]
                di += 1
        return bytes(out)


__all__ = ["DeltaEncoder"]
