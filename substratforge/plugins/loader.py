# -*- coding: utf-8 -*-
"""插件发现与动态加载。"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path


def discover_plugins(plugin_dir: str | Path) -> list[Path]:
    """扫描目录下的插件模块（*.py，排除 _ 开头）。"""
    d = Path(plugin_dir)
    if not d.exists():
        return []
    return sorted(p for p in d.glob("*.py") if not p.name.startswith("_"))


def load_plugin_module(path: Path):
    """动态加载一个插件模块。"""
    name = f"_substratforge_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载插件 {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


__all__ = ["discover_plugins", "load_plugin_module"]
