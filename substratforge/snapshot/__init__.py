# -*- coding: utf-8 -*-
"""快照引擎：把沙箱完整状态（内存描述 + 文件系统）序列化 / 恢复。

核心链路（挂起）:
    suspend(handle)
      -> backend.pause(handle)             # 冻结进程
      -> fs.tar(rootfs)                    # 打包可写层
      -> mem.capture(handle)               # 采集进程元信息
      -> compress / dedup / 增量编码
      -> storage.put(snapshot)

核心链路（恢复）:
    resume(snapshot)
      -> storage.get -> 解码 -> 还原 fs
      -> backend.spawn(还原的 spec)         # 重新拉起进程
      -> backend.resume / 状态置 RUNNING
"""
from .engine import SnapshotEngine
from .mem import MemoryCapture
from .fs import FilesystemLayer
from .delta import DeltaEncoder
from .compress import Compressor

__all__ = ["SnapshotEngine", "MemoryCapture", "FilesystemLayer", "DeltaEncoder", "Compressor"]
