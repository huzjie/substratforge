# -*- coding: utf-8 -*-
"""护栏：对进入沙箱的动作做准入 / 拦截。

默认提供 deny_all / allow_all，以及一个可组合的 Guardrail 基类。
生产可基于此实现命令白名单、网络域名白名单等（见 docs/security-guardrails.md）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Guardrail:
    """动作护栏。"""
    name: str
    predicate: Callable[[dict], bool] = field(default=lambda action: True)
    message: str = "action blocked by guardrail"

    def allows(self, action: dict) -> bool:
        return bool(self.predicate(action))


def deny_all(action: dict) -> bool:
    """默认拒绝一切（最严格）。"""
    return False


def allow_all(action: dict) -> bool:
    """默认允许一切（最宽松）。"""
    return True


def command_whitelist(allowed: set[str]) -> Guardrail:
    """构造一个命令白名单护栏。"""
    def pred(action: dict) -> bool:
        cmd = (action.get("command") or [""])[0]
        return cmd in allowed
    return Guardrail(name="command_whitelist", predicate=pred,
                     message=f"command not in whitelist {allowed}")


__all__ = ["Guardrail", "deny_all", "allow_all", "command_whitelist"]
