# -*- coding: utf-8 -*-
"""Python SDK：面向远程 REST 服务的客户端。

支持两种用法：
- 远程：`Client(base_url="http://host:8080")` 走 HTTP
- 本地：`Client(substrate=Substrate(...))` 直接调用本地引擎（无网络）

两种用法共享同一套方法签名，业务代码无需改动即可在本地/远程切换。
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any, Optional

from ..types import SandboxSpec


class Client:
    """SubstratForge 客户端。"""

    def __init__(self, base_url: str | None = None, substrate=None):
        if base_url is None and substrate is None:
            raise ValueError("必须提供 base_url 或 substrate 之一")
        self.base_url = base_url
        self._sub = substrate

    # ---- HTTP 辅助 ----
    def _req(self, method: str, path: str, body: dict | None = None) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"{self.base_url}{path}", data=data, method=method,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None

    # ---- 统一接口 ----
    def spawn(self, spec: SandboxSpec | dict) -> dict:
        if self._sub is not None:
            spec = spec.as_dict() if isinstance(spec, SandboxSpec) else spec
            handle = self._sub.spawn(**spec)
            return handle.as_dict()
        return self._req("POST", "/api/v1/sandboxes", spec)

    def suspend(self, sandbox_id: str, tags: dict | None = None) -> dict:
        if self._sub is not None:
            return self._sub.suspend(sandbox_id, tags=tags).as_dict()
        return self._req("POST", f"/api/v1/sandboxes/{sandbox_id}/suspend", {"tags": tags or {}})

    def resume(self, sandbox_id: str, snapshot_id: str | None = None) -> dict:
        if self._sub is not None:
            return self._sub.resume(sandbox_id, snapshot_id=snapshot_id).as_dict()
        return self._req("POST", f"/api/v1/sandboxes/{sandbox_id}/resume", {"snapshot_id": snapshot_id})

    def destroy(self, sandbox_id: str) -> None:
        if self._sub is not None:
            self._sub.destroy(sandbox_id)
            return
        self._req("DELETE", f"/api/v1/sandboxes/{sandbox_id}")

    def stats(self) -> dict:
        if self._sub is not None:
            return self._sub.scheduler.stats().as_dict()
        return self._req("GET", "/api/v1/stats")

    def health(self) -> dict:
        if self._sub is not None:
            return {"status": "ok"}
        return self._req("GET", "/health")


__all__ = ["Client"]
