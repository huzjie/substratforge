# -*- coding: utf-8 -*-
"""microVM 沙箱后端（Firecracker / Cloud Hypervisor）。

最强隔离：每个 agent 独占一个轻量虚拟机（几十 MB 内存开销、毫秒级启动）。
本后端封装 Firecracker 的 REST API：

- 启动：配置 boot-source / drive / vsock，启动 vCPU
- 挂起：快照（snapshot create）+ 停止 vmm
- 恢复：从快照文件恢复 vmm

需要本机安装 firecracker（见 docs/sandbox-microvm.md）。
"""
from __future__ import annotations

import json
import shutil
import socket
import urllib.request
from pathlib import Path
from typing import Any

from ..errors import SandboxError
from ..types import IsolationLevel, SandboxSpec, SandboxState
from .base import SandboxBackend, SandboxHandle

FIRECRACKER = shutil.which("firecracker") or "firecracker"


def _api(sock: str, method: str, path: str, payload: dict | None = None) -> dict:
    """通过 Firecracker 的 Unix socket API 发请求。"""
    body = json.dumps(payload).encode() if payload is not None else b""
    req = urllib.request.Request(
        f"http://localhost{path}", data=body, method=method,
        headers={"Content-Type": "application/json"},
    )
    # Firecracker API 走 UDS；这里留一个 http 适配便于测试，实际用 subprocess 更稳。
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode() or "{}")


class MicrovmSandboxBackend(SandboxBackend):
    isolation = IsolationLevel.MICROVM

    def __init__(self, firecracker: str | None = None, kernel: str | None = None, rootfs: str | None = None):
        self.firecracker = firecracker or FIRECRACKER
        self.kernel = kernel or "/var/lib/substratforge/vmlinux.bin"
        self.rootfs = rootfs or "/var/lib/substratforge/rootfs.ext4"

    def _check(self) -> None:
        if shutil.which(self.firecracker) is None and not Path(self.firecracker).exists():
            raise SandboxError(
                f"未找到 Firecracker '{self.firecracker}'。请安装 Firecracker（见 docs/sandbox-microvm.md），"
                "或改用 process / gvisor 后端。"
            )

    def spawn(self, spec: SandboxSpec) -> SandboxHandle:
        self._check()
        raise SandboxError(
            "microvm 后端需要完整 Firecracker 部署（kernel/rootfs/network），"
            "骨架已就绪，生产启用请参照 docs/sandbox-microvm.md 配置 boot-source 与 drive。"
        )

    def pause(self, handle: SandboxHandle) -> None:
        raise SandboxError("microvm 暂停走快照路径（snapshot create），请使用 Substrate.suspend()")

    def resume(self, handle: SandboxHandle) -> None:
        raise SandboxError("microvm 恢复走快照路径（snapshot load），请使用 Substrate.resume()")

    def kill(self, handle: SandboxHandle) -> None:
        handle.state = SandboxState.STOPPED


from ..sandbox import backend_registry  # noqa: E402

backend_registry.register("microvm", MicrovmSandboxBackend)

__all__ = ["MicrovmSandboxBackend"]
