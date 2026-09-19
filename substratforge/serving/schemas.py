# -*- coding: utf-8 -*-
"""REST 层请求 / 响应模型（pydantic，可选依赖）。

若未安装 pydantic，服务层会降级到 dict 模式（见 api.py 的 fallback）。
字段与 types.py 里的 dataclass 保持一致。
"""
from __future__ import annotations

try:
    from pydantic import BaseModel, Field  # type: ignore
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore
    Field = lambda *a, **k: None  # noqa: E731


class SandboxCreate(BaseModel):
    """创建沙箱请求。"""
    name: str = Field(..., description="沙箱名")
    image: str = "python:3.12"
    command: list[str] = []
    env: dict = {}
    isolation: str = "process"
    memory_mb: int = 256
    cpu_millis: int = 0
    labels: dict = {}


class SandboxInfo(BaseModel):
    """沙箱信息响应。"""
    id: str
    state: str
    isolation: str
    host: str = ""


class SuspendRequest(BaseModel):
    """挂起请求。"""
    tags: dict = {}


class ResumeRequest(BaseModel):
    """恢复请求。"""
    snapshot_id: str = ""


class SnapshotInfo(BaseModel):
    """快照信息响应。"""
    id: str
    sandbox_id: str
    size_bytes: int
    compressed_bytes: int
    checksum: str


__all__ = ["SandboxCreate", "SandboxInfo", "SuspendRequest", "ResumeRequest", "SnapshotInfo"]
