# -*- coding: utf-8 -*-
"""主引擎端到端（进程级后端，零依赖）。"""
from substratforge import Substrate
from substratforge.types import SandboxState


def test_spawn_suspend_resume_destroy(tmp_path):
    s = Substrate.from_config({
        "sandbox": {"root_dir": str(tmp_path / "sb")},
        "storage": {"backend": "memory"},
        "snapshot": {"dir": str(tmp_path / "snap"), "compression": "gzip"},
    })
    name = "e2e-demo"
    s.spawn(name, command=["python", "-c", "import time; time.sleep(86400)"])
    assert s.get(name).state == SandboxState.RUNNING

    snap = s.suspend(name)
    assert snap.sandbox_id == name
    assert s.get(name).state == SandboxState.SUSPENDED

    s.resume(name)
    assert s.get(name).state == SandboxState.RUNNING

    s.destroy(name)
    assert len(s.list_sandboxes()) == 0
