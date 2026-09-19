# -*- coding: utf-8 -*-
"""配置加载：优先 PyYAML，缺失时退回内置极简 YAML 解析器（零依赖可用）。"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import ConfigurationError
from .utils import deep_merge


DEFAULTS: dict[str, Any] = {
    "server": {"host": "127.0.0.1", "port": 8080, "workers": 1},
    "sandbox": {
        "default_isolation": "process",
        "default_image": "python:3.12",
        "workdir": "/workspace",
        "max_idle_seconds": 300,
        "auto_suspend": True,
        "root_dir": "~/.substratforge/sandboxes",
    },
    "snapshot": {
        "format": "tar",
        "compression": "zstd",
        "delta": True,
        "dir": "~/.substratforge/snapshots",
    },
    "storage": {"backend": "local", "root": "~/.substratforge/store"},
    "scheduler": {
        "eviction_policy": "lru",
        "max_suspended_per_host": 1000,
        "max_running_per_host": 64,
        "idle_suspend_after": 300,
        "resume_budget_ms": 500,
    },
    "observability": {"metrics_enabled": True, "metrics_port": 9090},
    "security": {"min_isolation": "process", "default_quota": {"memory_mb": 256, "disk_mb": 512, "pids": 64}},
}


def _simple_yaml(text: str) -> dict[str, Any]:
    """极简 YAML 子集解析：仅支持标量、两层嵌套映射、内联列表、注释与引号。

    这是 PyYAML 的退化替代，覆盖本项目 config.yaml 的全部用法。
    复杂 YAML 请安装 PyYAML 后走标准路径。
    """
    out: dict[str, Any] = {}
    stack: list[dict[str, Any]] = [out]
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        level = indent // 2
        stripped = line.strip()
        if stripped.startswith("- "):
            # 内联列表项，挂到当前层级最近的 list 键
            item = _parse_scalar(stripped[2:])
            cur = stack[-1]
            # 找到最近一个值为 list 的键
            for d in reversed(stack):
                if isinstance(d.get("__list__"), list):
                    d["__list__"].append(item)
                    break
            continue
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip().strip("\"'")
        val = val.strip()
        # 回退栈到对应层级
        while len(stack) - 1 > level:
            stack.pop()
        cur = stack[-1]
        if val == "" or (val.startswith("[") and val.endswith("]")):
            child: dict[str, Any] = {}
            if val.startswith("["):
                child["__list__"] = [_parse_scalar(x.strip()) for x in val[1:-1].split(",") if x.strip()]
            cur[key] = child
            stack.append(child)
        else:
            cur[key] = _parse_scalar(val)
    return _unwrap(out)


def _unwrap(d: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for k, v in d.items():
        if k == "__list__":
            continue
        if isinstance(v, dict) and "__list__" in v and set(v.keys()) == {"__list__"}:
            result[k] = v["__list__"]
        elif isinstance(v, dict):
            result[k] = _unwrap(v)
        else:
            result[k] = v
    return result


def _parse_scalar(s: str) -> Any:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    if s in ("true", "True", "yes"):
        return True
    if s in ("false", "False", "no"):
        return False
    if s in ("null", "None", "~"):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text) or {}
    except ImportError:
        data = _simple_yaml(text)
    except Exception as exc:  # PyYAML 报错则退回极简解析
        data = _simple_yaml(text)
        if not data:
            raise ConfigurationError(f"无法解析配置 {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"配置 {path} 顶层必须是映射")
    return data


def load_config(path: str | Path = "config.yaml") -> dict[str, Any]:
    """加载配置并合并默认值。文件不存在则用默认值。"""
    p = Path(path)
    if p.exists():
        user = _load_yaml(p)
    else:
        user = {}
    return deep_merge(DEFAULTS, user)


class Config:
    """带属性访问的配置封装。"""

    def __init__(self, data: dict[str, Any] | None = None, path: str | Path | None = None):
        self._data = data if data is not None else load_config(path or "config.yaml")

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def section(self, name: str) -> dict[str, Any]:
        return dict(self._data.get(name, {}))

    @property
    def raw(self) -> dict[str, Any]:
        return self._data


__all__ = ["Config", "load_config", "DEFAULTS"]
