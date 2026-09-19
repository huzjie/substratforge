# -*- coding: utf-8 -*-
"""FastAPI REST 服务：暴露 Substrate 的完整能力。

端点：
    GET  /health                        健康检查
    GET  /api/v1/sandboxes              列出沙箱
    POST /api/v1/sandboxes              创建沙箱
    GET  /api/v1/sandboxes/{id}         查询沙箱
    POST /api/v1/sandboxes/{id}/suspend 挂起（返回快照）
    POST /api/v1/sandboxes/{id}/resume  恢复
    DELETE /api/v1/sandboxes/{id}       销毁
    GET  /api/v1/snapshots              列出快照
    GET  /api/v1/stats                  调度器统计
"""
from __future__ import annotations

from typing import Any

from ..config import Config
from ..core.substrate import Substrate
from ..errors import (
    NotFoundError, AlreadyExistsError, SubstrateError, QuotaExceededError,
)

try:
    from fastapi import FastAPI, HTTPException  # type: ignore
    from pydantic import BaseModel  # type: ignore
    _HAS_FASTAPI = True
except ImportError:  # pragma: no cover
    _HAS_FASTAPI = False
    FastAPI = object
    HTTPException = Exception
    BaseModel = object


def _as_dict(obj: Any) -> Any:
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    if hasattr(obj, "dict"):
        return obj.dict()
    return obj


def create_app(config: Config | None = None, substrate: Substrate | None = None) -> Any:
    """构建 FastAPI 应用。"""
    if not _HAS_FASTAPI:
        raise RuntimeError("需要安装 fastapi/uvicorn：pip install substratforge[api]")

    app = FastAPI(title="SubstratForge", version="0.1.0",
                  description="高密度智能体基板运行时（Agent Substrate）")
    s = substrate or Substrate.from_config(config)

    @app.get("/health")
    def health():
        return {"status": "ok", "suspended": s.scheduler.stats().suspended}

    @app.get("/api/v1/sandboxes")
    def list_sandboxes():
        return [_as_dict(x) for x in s.list_sandboxes()]

    @app.post("/api/v1/sandboxes", status_code=201)
    def create_sandbox(body: dict):
        try:
            handle = s.spawn(
                name=body["name"], image=body.get("image", "python:3.12"),
                command=body.get("command", []), env=body.get("env", {}),
                isolation=body.get("isolation", "process"),
                memory_mb=body.get("memory_mb", 256),
            )
            return _as_dict(handle)
        except AlreadyExistsError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except QuotaExceededError as e:
            raise HTTPException(status_code=429, detail=str(e))
        except SubstrateError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/v1/sandboxes/{sid}")
    def get_sandbox(sid: str):
        try:
            return _as_dict(s.get(sid))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.post("/api/v1/sandboxes/{sid}/suspend")
    def suspend(sid: str, body: dict | None = None):
        try:
            snap = s.suspend(sid, tags=(body or {}).get("tags", {}))
            return _as_dict(snap)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.post("/api/v1/sandboxes/{sid}/resume")
    def resume(sid: str, body: dict | None = None):
        try:
            snap_id = (body or {}).get("snapshot_id") or None
            return _as_dict(s.resume(sid, snapshot_id=snap_id))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.delete("/api/v1/sandboxes/{sid}", status_code=204)
    def destroy(sid: str):
        try:
            s.destroy(sid)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.get("/api/v1/snapshots")
    def list_snapshots():
        return [_as_dict(x) for x in s.list_snapshots()]

    @app.get("/api/v1/stats")
    def stats():
        return _as_dict(s.scheduler.stats())

    return app


__all__ = ["create_app"]
