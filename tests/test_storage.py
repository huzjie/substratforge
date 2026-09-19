# -*- coding: utf-8 -*-
import tempfile
from pathlib import Path

from substratforge.storage.local import LocalStore
from substratforge.storage.memory import MemoryStore
from substratforge.storage.gc import GarbageCollector


def test_memory_store():
    s = MemoryStore()
    s.put("a", b"data", {"id": "a"})
    assert s.get_bytes("a") == b"data"
    s.delete("a")
    assert s.get_bytes("a") is None


def test_local_store(tmp_path: Path):
    s = LocalStore(tmp_path)
    s.put("snap1", b"hello", {"id": "snap1"})
    assert s.get_bytes("snap1") == b"hello"
    assert len(s.list()) == 1


def test_gc_protects_referenced():
    meta = [{"id": "s1", "created_at": 100.0}, {"id": "s2", "created_at": 200.0}]
    gc = GarbageCollector(keep=0)
    collected = gc.collect(meta, referenced_ids={"s1"})
    assert "s1" not in collected
    assert "s2" in collected
