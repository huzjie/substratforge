# -*- coding: utf-8 -*-
from substratforge.storage.retention import RetentionPolicy


def test_retention_keeps_latest():
    meta = [{"id": f"s{i}", "created_at": 1000 + i} for i in range(20)]
    to_delete = RetentionPolicy(keep_latest=5).decide(meta)
    assert len(to_delete) == 0  # 无 max_age 时不删
    to_delete = RetentionPolicy(keep_latest=5, max_age_seconds=1).decide(meta)
    assert "s0" in to_delete
