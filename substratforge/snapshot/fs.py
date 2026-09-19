# -*- coding: utf-8 -*-
"""文件系统层：把沙箱可写层打包成 tar 流，以及还原。

零依赖、流式、支持大目录；打包时跳过 .snap / 套接字 / 特殊设备文件，
避免 tar 报错或把无关文件纳入快照。
"""
from __future__ import annotations

import io
import os
import tarfile
from pathlib import Path

from ..errors import SnapshotError

SKIP_NAMES = {".git", "__pycache__", ".snap"}


class FilesystemLayer:
    """文件系统打包 / 还原。"""

    def tar(self, root: Path) -> bytes:
        """把 root 目录打包成 tar 字节流。"""
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            for path in sorted(root.rglob("*")):
                rel = path.relative_to(root)
                if any(part in SKIP_NAMES for part in rel.parts):
                    continue
                if path.is_symlink():
                    ti = tarfile.TarInfo(str(rel))
                    ti.type = tarfile.SYMTYPE
                    ti.linkname = os.readlink(path)
                    tf.addfile(ti)
                elif path.is_file():
                    tf.add(str(path), arcname=str(rel), recursive=False)
                elif path.is_dir():
                    ti = tarfile.TarInfo(str(rel) + "/")
                    ti.type = tarfile.DIRTYPE
                    tf.addfile(ti)
        return buf.getvalue()

    def untar(self, data: bytes, target: Path) -> None:
        """把 tar 字节流还原到 target 目录。"""
        target.mkdir(parents=True, exist_ok=True)
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as tf:
                # 防路径穿越
                for member in tf.getmembers():
                    dest = (target / member.name).resolve()
                    if not str(dest).startswith(str(target.resolve())):
                        raise SnapshotError(f"快照含非法路径: {member.name}")
                tf.extractall(str(target))
        except tarfile.TarError as exc:
            raise SnapshotError(f"快照还原失败: {exc}") from exc


__all__ = ["FilesystemLayer"]
