# -*- coding: utf-8 -*-
"""沙箱生命周期状态机。

用显式转移表约束合法迁移，杜绝非法状态跳转（如从 DESTROYED 恢复）。
状态定义见 types.SandboxState。
"""
from __future__ import annotations

from ..errors import RuntimeError as RuntimeErrorBase
from ..types import SandboxState, COLD_STATES

#: 允许的 (from, to) 转移
TRANSITIONS: set[tuple[SandboxState, SandboxState]] = {
    (SandboxState.PENDING, SandboxState.RUNNING),
    (SandboxState.RUNNING, SandboxState.PAUSED),
    (SandboxState.PAUSED, SandboxState.RUNNING),
    (SandboxState.RUNNING, SandboxState.SUSPENDING),
    (SandboxState.PAUSED, SandboxState.SUSPENDING),
    (SandboxState.SUSPENDING, SandboxState.SUSPENDED),
    (SandboxState.SUSPENDED, SandboxState.RESUMING),
    (SandboxState.RESUMING, SandboxState.RUNNING),
    (SandboxState.RUNNING, SandboxState.STOPPING),
    (SandboxState.PAUSED, SandboxState.STOPPING),
    (SandboxState.STOPPING, SandboxState.STOPPED),
    (SandboxState.STOPPED, SandboxState.DESTROYED),
    (SandboxState.SUSPENDED, SandboxState.DESTROYED),
    (SandboxState.STOPPED, SandboxState.RESUMING),  # 允许从 stopped 恢复
    (SandboxState.FAILED, SandboxState.DESTROYED),
}


class StateMachine:
    """带转移表校验的状态机。"""

    def __init__(self, initial: SandboxState = SandboxState.PENDING,
                 transitions: set = None):
        self.state = initial
        self.transitions = transitions or TRANSITIONS

    def transition(self, to: SandboxState) -> None:
        if to == self.state:
            return
        if (self.state, to) not in self.transitions:
            raise RuntimeErrorBase(f"非法状态转移: {self.state.value} -> {to.value}")
        self.state = to

    @property
    def is_cold(self) -> bool:
        return self.state in COLD_STATES


class Lifecycle:
    """生命周期管理：包装状态机 + 提供语义化动作方法。"""

    def __init__(self, initial: SandboxState = SandboxState.PENDING):
        self._sm = StateMachine(initial)

    @property
    def state(self) -> SandboxState:
        return self._sm.state

    def mark_running(self) -> None:
        self._sm.transition(SandboxState.RUNNING)

    def mark_paused(self) -> None:
        self._sm.transition(SandboxState.PAUSED)

    def mark_suspending(self) -> None:
        self._sm.transition(SandboxState.SUSPENDING)

    def mark_suspended(self) -> None:
        self._sm.transition(SandboxState.SUSPENDED)

    def mark_resuming(self) -> None:
        self._sm.transition(SandboxState.RESUMING)

    def mark_stopping(self) -> None:
        self._sm.transition(SandboxState.STOPPING)

    def mark_stopped(self) -> None:
        self._sm.transition(SandboxState.STOPPED)

    def mark_destroyed(self) -> None:
        # destroy 是任意态的终态清理动作，绕过转移表
        self._sm.state = SandboxState.DESTROYED

    def mark_failed(self) -> None:
        # 失败是任意态的兜底，绕过转移表
        self._sm.state = SandboxState.FAILED


__all__ = ["Lifecycle", "StateMachine", "TRANSITIONS"]
