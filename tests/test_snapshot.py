# -*- coding: utf-8 -*-
from pathlib import Path

from substratforge.snapshot.fs import FilesystemLayer
from substratforge.snapshot.delta import DeltaEncoder
from substratforge.snapshot.compress import Compressor


def test_fs_roundtrip(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    (src / "sub").mkdir()
    (src / "sub" / "b.txt").write_text("world")
    data = FilesystemLayer().tar(src)
    dst = tmp_path / "dst"
    FilesystemLayer().untar(data, dst)
    assert (dst / "a.txt").read_text() == "hello"
    assert (dst / "sub" / "b.txt").read_text() == "world"


def test_delta_roundtrip():
    parent = b"hello world " * 1000
    new = b"hello world " * 1000 + b"EXTRA"
    delta = DeltaEncoder.encode(new, parent)
    assert len(delta) < len(new)
    assert DeltaEncoder.decode(delta, parent) == new


def test_compressor_gzip():
    c = Compressor("gzip")
    data = b"x" * 1000
    assert c.decompress(c.compress(data)) == data
