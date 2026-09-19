# -*- coding: utf-8 -*-
"""示例压缩器插件：bzip2（演示如何注册新压缩算法）。"""
import bz2


def setup(manager):
    from ...snapshot.compress import Compressor, _ALGOS
    # 通过猴子补丁方式注册 bz2 到 Compressor（演示；生产建议扩展 Compressor）
    def _bz2_compress(data: bytes) -> bytes:
        return bz2.compress(data)
    def _bz2_decompress(data: bytes) -> bytes:
        return bz2.decompress(data)
    Compressor._bz2_compress = staticmethod(_bz2_compress)
    Compressor._bz2_decompress = staticmethod(_bz2_decompress)


__all__ = ["setup"]
