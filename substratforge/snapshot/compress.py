# -*- coding: utf-8 -*-
"""压缩器：zstd / gzip / lz4 / none，多后端可插拔。

优先使用可选第三方库（zstandard / lz4），缺失时退回 zlib(gzip) 或
不压缩，保证零依赖也能跑通。
"""
from __future__ import annotations

import zlib

from ..errors import ConfigurationError

_ALGOS = ("zstd", "gzip", "lz4", "none")


class Compressor:
    """压缩器。"""

    def __init__(self, algo: str = "zstd"):
        if algo not in _ALGOS:
            raise ConfigurationError(f"不支持的压缩算法: {algo!r}，可用: {_ALGOS}")
        self.algo = algo

    def compress(self, data: bytes) -> bytes:
        if self.algo == "none":
            return data
        if self.algo == "gzip":
            return zlib.compress(data, level=6)
        if self.algo == "zstd":
            try:
                import zstandard  # type: ignore
                return zstandard.ZstdCompressor(level=3).compress(data)
            except ImportError:
                return zlib.compress(data, level=6)
        if self.algo == "lz4":
            try:
                import lz4.frame  # type: ignore
                return lz4.frame.compress(data)
            except ImportError:
                return zlib.compress(data, level=6)
        return data

    def decompress(self, data: bytes) -> bytes:
        if self.algo == "none":
            return data
        if self.algo == "gzip":
            return zlib.decompress(data)
        # zstd / lz4 有魔数，可用魔数嗅探
        if data[:4] == b"\x28\xb5\x2f\xfd":  # zstd magic
            try:
                import zstandard  # type: ignore
                return zstandard.ZstdDecompressor().decompress(data)
            except ImportError:
                raise ConfigurationError("快照为 zstd 压缩，但未安装 zstandard")
        if data[:4] == b"\x04\x22\x4d\x18":  # lz4 magic
            try:
                import lz4.frame  # type: ignore
                return lz4.frame.decompress(data)
            except ImportError:
                raise ConfigurationError("快照为 lz4 压缩，但未安装 lz4")
        # 退回 gzip/zlib
        try:
            return zlib.decompress(data)
        except zlib.error:
            return data


__all__ = ["Compressor"]
