# -*- coding: utf-8 -*-
"""gVisor 沙箱后端（runsc）。

gVisor 通过拦截 syscall 提供进程级虚拟化，隔离强度介于进程与 VM 之间，
是 Google Agent Substrate 默认的一档。本后端封装 ``runsc`` CLI：

- 通过 OCI 配置（config.json）声明 rootfs / 命令 / 资源限制
- 挂起 = ``runsc pause <cid>``；恢复 = ``runsc resume <cid>``
- 需要本机安装 gVisor（见 docs/sandbox-gvisor.md）

未安装 runsc 时，spawn 会抛出明确的 SandboxError 提示安装路径。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..errors import SandboxError
from ..types import IsolationLevel, SandboxSpec, SandboxState
from .base import SandboxBackend, SandboxHandle

RUNSC = shutil.which("runsc") or "runsc"


def _oci_config(spec: SandboxSpec, rootfs: str) -> dict:
    """构造最小 OCI runtime spec（JSON）。"""
    env = [f"{k}={v}" for k, v in spec.env.items()]
    return {
        "ociVersion": "1.0.2",
        "process": {
            "terminal": False,
            "user": {"uid": 0, "gid": 0},
            "args": spec.command or ["/bin/sh", "-c", "sleep 86400"],
            "env": env,
            "cwd": spec.workdir,
        },
        "root": {"path": rootfs, "readonly": False},
        "hostname": spec.name,
        "linux": {
            "resources": {
                "memory": {"limit": spec.quota.memory_mb * 1024 * 1024} if spec.quota.memory_mb else {},
                "cpu": {"quota": spec.quota.cpu_millis * 1000, "period": 1000000} if spec.quota.cpu_millis else {},
                "pids": {"limit": spec.quota.pids} if spec.quota.pids else {},
            },
            "namespaces": [
                {"type": "pid"}, {"type": "network"}, {"type": "ipc"},
                {"type": "uts"}, {"type": "mount"},
            ],
        },
    }


class GvisorSandboxBackend(SandboxBackend):
    isolation = IsolationLevel.GVISOR

    def __init__(self, runsc: str | None = None, rootfs: str | None = None):
        self.runsc = runsc or RUNSC
        self.default_rootfs = rootfs or "/var/lib/substratforge/rootfs"

    def _check(self) -> None:
        if shutil.which(self.runsc) is None and not Path(self.runsc).exists():
            raise SandboxError(
                f"未找到 gVisor 运行时 '{self.runsc}'。请安装 gVisor（见 docs/sandbox-gvisor.md），"
                "或改用 process / microvm 后端。"
            )

    def spawn(self, spec: SandboxSpec) -> SandboxHandle:
        self._check()
        bundle = Path(tempfile.mkdtemp(prefix=f"substratforge-{spec.name}-"))
        rootfs = spec.metadata.get("rootfs", self.default_rootfs)
        cfg = _oci_config(spec, rootfs)
        (bundle / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
        cid = f"substratforge-{spec.name}"
        try:
            subprocess.run([self.runsc, "run", "-bundle", str(bundle), cid],
                           check=True, capture_output=True, timeout=30)
        except Exception as exc:
            raise SandboxError(f"gVisor run 失败: {exc}") from exc
        handle = SandboxHandle(
            sandbox_id=spec.name, spec=spec, fs_root=Path(rootfs),
            backend=self, state=SandboxState.RUNNING,
        )
        handle.meta["_cid"] = cid
        handle.meta["_bundle"] = str(bundle)
        return handle

    def _cid(self, handle: SandboxHandle) -> str:
        return handle.meta.get("_cid", f"substratforge-{handle.sandbox_id}")

    def pause(self, handle: SandboxHandle) -> None:
        subprocess.run([self.runsc, "pause", self._cid(handle)], check=True, capture_output=True)
        handle.state = SandboxState.PAUSED

    def resume(self, handle: SandboxHandle) -> None:
        subprocess.run([self.runsc, "resume", self._cid(handle)], check=True, capture_output=True)
        handle.state = SandboxState.RUNNING

    def kill(self, handle: SandboxHandle) -> None:
        subprocess.run([self.runsc, "delete", "-force", self._cid(handle)], capture_output=True)
        handle.state = SandboxState.STOPPED


from ..sandbox import backend_registry  # noqa: E402

backend_registry.register("gvisor", GvisorSandboxBackend)

__all__ = ["GvisorSandboxBackend"]
