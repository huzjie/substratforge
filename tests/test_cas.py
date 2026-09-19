# -*- coding: utf-8 -*-
from pathlib import Path

from substratforge.storage.cas import ContentAddressedStore


def test_cas_roundtrip(tmp_path: Path):
    cas = ContentAddressedStore(tmp_path)
    refs = cas.put_snapshot("s1", b"hello world", chunk=5)
    assert len(refs) == 3  # "hello", " worl", "d"
    assert cas.get_snapshot("s1") == b"hello world"
