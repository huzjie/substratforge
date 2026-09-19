# -*- coding: utf-8 -*-
import pytest

from substratforge.security.policy import SecurityPolicy, enforce_min_isolation
from substratforge.security.guardrails import command_whitelist
from substratforge.security.audit import AuditLog
from substratforge.errors import IsolationError
from substratforge.types import SandboxSpec, IsolationLevel


def test_command_whitelist():
    g = command_whitelist({"python", "node"})
    assert g.allows({"command": ["python", "x.py"]})
    assert not g.allows({"command": ["rm", "-rf", "/"]})


def test_enforce_min_isolation():
    assert enforce_min_isolation("gvisor", "process")
    assert not enforce_min_isolation("process", "gvisor")


def test_audit_log(tmp_path):
    log = AuditLog(tmp_path / "audit.jsonl")
    log.record("spawn", sandbox_id="x")
    events = list(log.iter_events())
    assert len(events) == 1
    assert events[0]["action"] == "spawn"
