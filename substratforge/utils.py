# -*- coding: utf-8 -*-
"""通用工具函数。"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    """计算字节串的 SHA-256 十六进制摘要。"""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """分块计算文件 SHA-256，避免大文件整体载入内存。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_dumps_compact(obj: Any) -> str:
    """紧凑 JSON 序列化（默认 ASCII 关闭，保证中文不转义）。"""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def ensure_dir(path: Path) -> Path:
    """确保目录存在并返回。"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def monotonic_ms() -> int:
    """单调时钟毫秒，用于计时挂起/恢复耗时。"""
    return int(time.perf_counter() * 1000)


def human_bytes(n: int) -> str:
    """把字节数转成人类可读字符串。"""
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{int(n)}B"
        n /= 1024
    return f"{n:.1f}TB"


def parse_duration(s: str) -> float:
    """解析如 ``300ms`` / ``2s`` / ``5m`` 的时长字符串为秒。"""
    s = s.strip().lower()
    table = {"ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0}
    for suffix, factor in table.items():
        if s.endswith(suffix):
            return float(s[: -len(suffix)]) * factor
    return float(s)


def deep_merge(base: dict, override: dict) -> dict:
    """递归合并 dict，override 优先。"""
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def sanitize_name(name: str) -> str:
    """把字符串规整成合法的沙箱名（小写字母/数字/连字符）。"""
    out = []
    for ch in name.lower():
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        else:
            out.append("-")
    s = "".join(out).strip("-_")
    return s or "sandbox"


def atomic_write(path: Path, data: bytes) -> None:
    """原子写文件（先写临时文件再 rename，避免写一半损坏）。"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


__all__ = [
    "sha256_bytes", "sha256_file", "json_dumps_compact", "ensure_dir",
    "monotonic_ms", "human_bytes", "parse_duration", "deep_merge",
    "sanitize_name", "atomic_write",
]
