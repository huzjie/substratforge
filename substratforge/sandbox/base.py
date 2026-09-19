# -*- coding: utf-8 -*-
"""沙箱后端抽象基类。

一个沙箱后端负责「真实地把一个进程 / 环境跑起来」，以及
「挂起（暂停进程）」「恢复（继续进程）」「终止」。快照序列化由
snapshot 层负责，后端只需暴露可挂起的进程句柄与文件系统根。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..types import IsolationLevel, ResourceQuota, SandboxSpec, SandboxState


class SandboxBackend(ABC):
    """沙箱后端接口。"""

    isolation: IsolationLevel

    @abstractmethod
    def spawn(self, spec: SandboxSpec) -> "SandboxHandle":
        """按规格启动沙箱，返回句柄。"""

    @abstractmethod
    def pause(self, handle: "SandboxHandle") -> None:
        """挂起进程（内存驻留，可秒级恢复）。"""

    @abstractmethod
    def resume(self, handle: "SandboxHandle") -> None:
        """恢复被挂起的进程。"""

    @abstractmethod
    def kill(self, handle: "SandboxHandle") -> None:
        """强制终止沙箱进程。"""

    def fs_root(self, handle: "SandboxHandle") -> Path:
        """返回沙箱可写层的根目录（用于快照层打包文件系统）。"""
        raise NotImplementedError

    def stats(self, handle: "SandboxHandle") -> dict[str, Any]:
        """返回实时资源占用（CPU / 内存 / PIDs）。"""
        return {}


class SandboxHandle:
    """沙箱运行句柄：把后端、进程标识、文件系统根、实时状态绑在一起。"""

    def __init__(
        self,
        sandbox_id: str,
        spec: SandboxSpec,
        pid: int | None = None,
        fs_root: Path | None = None,
        backend: SandboxBackend | None = None,
        state: SandboxState = SandboxState.RUNNING,
    ):
        self.sandbox_id = sandbox_id
        self.spec = spec
        self.pid = pid
        self.fs_root = fs_root
        self.backend = backend
        self.state = state
        self.meta: dict[str, Any] = {}

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SandboxHandle {self.sandbox_id} state={self.state.value}>"


__all__ = ["SandboxBackend", "SandboxHandle"]
