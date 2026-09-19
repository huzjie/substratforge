# -*- coding: utf-8 -*-
from substratforge.core.hooks import Hooks


def test_hooks():
    h = Hooks()
    calls = []
    h.on("after_suspend", lambda sid: calls.append(sid))
    h.emit("after_suspend", "x")
    assert calls == ["x"]
