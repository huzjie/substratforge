# -*- coding: utf-8 -*-
"""审计日志：记录每一次敏感操作（spawn/suspend/resume/destroy）。

审计事件以 append-only JSONL 落盘，便于合规审查与事后追溯。
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from ..utils import ensure_dir


@dataclass
class AuditEvent:
    """一条审计事件。"""
    action: str
    sandbox_id: str = ""
    actor: str = "system"
    detail: dict = field(default_factory=dict)
    ts: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def as_dict(self) -> dict:
        return {"id": self.id, "ts": self.ts, "action": self.action,
                "sandbox_id": self.sandbox_id, "actor": self.actor, "detail": self.detail}


class AuditLog:
    """JSONL 审计日志。"""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        ensure_dir(self.path.parent)

    def record(self, action: str, sandbox_id: str = "", **detail) -> AuditEvent:
        ev = AuditEvent(action=action, sandbox_id=sandbox_id, detail=detail)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev.as_dict(), ensure_ascii=False) + "\n")
        return ev

    def iter_events(self):
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)


__all__ = ["AuditLog", "AuditEvent"]
