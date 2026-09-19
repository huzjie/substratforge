# -*- coding: utf-8 -*-
from substratforge.plugins.sandbox.example_backend import EchoBackend


def test_echo_backend_spawn():
    b = EchoBackend()
    from substratforge.types import SandboxSpec
    h = b.spawn(SandboxSpec(name="e"))
    assert h.sandbox_id == "e"
