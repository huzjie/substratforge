# -*- coding: utf-8 -*-
import pytest

from substratforge.types import (
    SandboxState, IsolationLevel, ResourceQuota, SandboxSpec,
    SnapshotInfo, new_id,
)


def test_sandbox_state_values():
    assert SandboxState.RUNNING.value == "running"
    assert SandboxState.SUSPENDED.value == "suspended"


def test_quota_defaults():
    q = ResourceQuota()
    assert q.memory_mb == 256
    assert q.pids == 64


def test_spec_as_dict():
    spec = SandboxSpec(name="x", isolation=IsolationLevel.PROCESS)
    d = spec.as_dict()
    assert d["isolation"] == "process"
    assert d["name"] == "x"


def test_new_id():
    a, b = new_id("t-"), new_id("t-")
    assert a != b and a.startswith("t-")
