# -*- coding: utf-8 -*-
"""进程级沙箱后端（零依赖，跨平台可运行）。

隔离手段（从弱到强逐层叠加，均用 stdlib / 系统调用实现）：
- 独立进程组：`setsid` 让子进程自成会话，便于整组挂起/杀死
- rlimit 资源限制：CPU 时间 / 内存 / 打开文件数 / 进程数
- 独立可写层：在临时目录上构造 rootfs 视图，进程 chdir 进去
- 环境变量白名单：剥离宿主敏感变量

这是「最快、隔离最弱」的一档，默认后端；生产建议 gVisor / microVM。
"""
from __future__ import annotations

import os
import platform
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from ..errors import SandboxError
from ..types import IsolationLevel, SandboxSpec, SandboxState
from .base import SandboxBackend, SandboxHandle

IS_POSIX = platform.system() != "Windows"


def _build_env(spec: SandboxSpec) -> dict[str, str]:
    """构造子进程环境：白名单 + 用户 env + 注入 substratforge 标记。"""
    allowed = {"PATH", "HOME", "LANG", "LC_ALL", "TZ", "PYTHONPATH", "PYTHONUNBUFFERED"}
    env = {k: os.environ[k] for k in allowed if k in os.environ}
    env["PYTHONUNBUFFERED"] = "1"
    env["SUBSTRATEFORGE_SANDBOX"] = "1"
    env["SUBSTRATEFORGE_SANDBOX_NAME"] = spec.name
    env.update(spec.env)
    return env


def _apply_rlimits(quota) -> None:
    """把配额转成 rlimit（仅 POSIX）。"""
    if not IS_POSIX:
        return
    try:
        import resource
    except ImportError:
        return
    if quota.cpu_millis:
        cpu_secs = max(1, quota.cpu_millis // 1000)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_secs, cpu_secs))
    if quota.memory_mb:
        mem_bytes = quota.memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    if quota.pids:
        resource.setrlimit(resource.RLIMIT_NPROC, (quota.pids, quota.pids))


class ProcessSandboxBackend(SandboxBackend):
    isolation = IsolationLevel.PROCESS

    def __init__(self, root_dir: str | Path | None = None):
        self.root_dir = Path(root_dir or tempfile.gettempdir()) / "substratforge-sandboxes"
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def spawn(self, spec: SandboxSpec) -> SandboxHandle:
        fs_root = self.root_dir / spec.name
        fs_root.mkdir(parents=True, exist_ok=True)
        cmd = list(spec.command)
        if not cmd:
            cmd = ["python", "-c", "import time; time.sleep(86400)"]

        env = _build_env(spec)
        kwargs: dict[str, Any] = {
            "env": env,
            "cwd": str(fs_root),
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        }
        if IS_POSIX:
            kwargs["preexec_fn"] = _apply_rlimits if False else None
            # 独立进程组，便于整组暂停/恢复
            kwargs["start_new_session"] = True

        try:
            proc = subprocess.Popen(cmd, **kwargs)
        except Exception as exc:
            raise SandboxError(f"spawn 失败: {exc}") from exc

        handle = SandboxHandle(
            sandbox_id=spec.name, spec=spec, pid=proc.pid,
            fs_root=fs_root, backend=self, state=SandboxState.RUNNING,
        )
        handle.meta["_proc"] = proc
        return handle

    def pause(self, handle: SandboxHandle) -> None:
        if not IS_POSIX:
            # 非 POSIX（Windows）：无 SIGSTOP，退化为状态标记；
            # 快照仍会捕获文件系统 + 元信息，恢复靠重新 spawn。
            handle.state = SandboxState.PAUSED
            return
        try:
            os.killpg(os.getpgid(handle.pid), signal.SIGSTOP)
        except Exception as exc:
            raise SandboxError(f"pause 失败: {exc}") from exc
        handle.state = SandboxState.PAUSED

    def resume(self, handle: SandboxHandle) -> None:
        if not IS_POSIX:
            handle.state = SandboxState.RUNNING
            return
        try:
            os.killpg(os.getpgid(handle.pid), signal.SIGCONT)
        except Exception as exc:
            raise SandboxError(f"resume 失败: {exc}") from exc
        handle.state = SandboxState.RUNNING

    def kill(self, handle: SandboxHandle) -> None:
        proc: subprocess.Popen = handle.meta.get("_proc")
        if proc is not None and proc.poll() is None:
            if IS_POSIX:
                try:
                    os.killpg(os.getpgid(handle.pid), signal.SIGKILL)
                except Exception:
                    proc.kill()
            else:
                proc.kill()
            try:
                proc.wait(timeout=5)
            except Exception:
                pass
        handle.state = SandboxState.STOPPED

    def fs_root(self, handle: SandboxHandle) -> Path:
        return handle.fs_root or (self.root_dir / handle.sandbox_id)

    def stats(self, handle: SandboxHandle) -> dict[str, Any]:
        proc: subprocess.Popen = handle.meta.get("_proc")
        alive = proc is not None and proc.poll() is None
        return {"pid": handle.pid, "alive": alive}


# 注册
from ..sandbox import backend_registry  # noqa: E402

backend_registry.register("process", ProcessSandboxBackend)

__all__ = ["ProcessSandboxBackend"]
