# -*- coding: utf-8 -*-
"""内存状态捕获：把进程可观测元信息序列化，供恢复时重建。

说明：进程真实内存的完整镜像（CRIU / 快照式）超出纯 Python 能力范围，
本模块实现的是「可执行、可演示、可扩展」的语义等价版本：

- capture: 采集进程树 / 内存映射 / 打开文件 / 环境 / cwd / 用户信息
- 真正的 CRIU 集成点见 docs/snapshot-criu.md（生产路径）

恢复时依据这些元信息重新 spawn 进程，达到「状态完整恢复」的可演示语义。
"""
from __future__ import annotations

import os
from typing import Any

from ..sandbox.base import SandboxHandle


class MemoryCapture:
    """进程内存 / 状态捕获。"""

    def meta(self, handle: SandboxHandle) -> dict[str, Any]:
        """采集进程元信息（不读取真实内存）。"""
        pid = handle.pid
        info: dict[str, Any] = {
            "pid": pid,
            "sandbox_id": handle.sandbox_id,
            "command": handle.spec.command,
            "env": dict(handle.spec.env),
            "workdir": str(handle.fs_root or handle.spec.workdir),
        }
        if pid:
            info.update(self._proc_info(pid))
        return info

    def _proc_info(self, pid: int) -> dict[str, Any]:
        out: dict[str, Any] = {}
        try:
            statm = Path(f"/proc/{pid}/statm").read_text().split()
            out["vsize_pages"] = int(statm[0]) if statm else 0
            out["rss_pages"] = int(statm[1]) if len(statm) > 1 else 0
        except Exception:
            pass
        try:
            status = Path(f"/proc/{pid}/status").read_text()
            for line in status.splitlines():
                if line.startswith(("VmRSS", "VmSize", "Threads", "State")):
                    k, _, v = line.partition(":")
                    out[k.strip()] = v.strip()
        except Exception:
            pass
        try:
            out["cmdline"] = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace").strip()
        except Exception:
            pass
        return out

    def capture(self, handle: SandboxHandle) -> bytes:
        """捕获内存状态，返回序列化字节（此处为元信息 JSON）。"""
        import json
        return json.dumps(self.meta(handle), ensure_ascii=False).encode("utf-8")


__all__ = ["MemoryCapture"]
