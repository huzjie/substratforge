# -*- coding: utf-8 -*-
"""示例沙箱插件：演示如何注册一个自定义后端。

一个真实后端需实现 spawn/pause/resume/kill 并注册到 backend_registry。
此示例提供最小可运行骨架（echo 后端，不真正隔离）。
"""
from ...sandbox.base import SandboxBackend, SandboxHandle
from ...types import IsolationLevel, SandboxSpec, SandboxState
from ...sandbox import backend_registry


class EchoBackend(SandboxBackend):
    """最小示例后端：登记即可用，不执行真实进程。"""
    isolation = IsolationLevel.PROCESS

    def spawn(self, spec: SandboxSpec) -> SandboxHandle:
        return SandboxHandle(sandbox_id=spec.name, spec=spec,
                             backend=self, state=SandboxState.RUNNING)

    def pause(self, handle: SandboxHandle) -> None:
        handle.state = SandboxState.PAUSED

    def resume(self, handle: SandboxHandle) -> None:
        handle.state = SandboxState.RUNNING

    def kill(self, handle: SandboxHandle) -> None:
        handle.state = SandboxState.STOPPED


def setup(manager):
    """插件入口：注册到 manager（供 PluginManager 调用）。"""
    backend_registry.register("echo", EchoBackend)


__all__ = ["EchoBackend", "setup"]
