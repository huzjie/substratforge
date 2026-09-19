# -*- coding: utf-8 -*-
import pytest

from substratforge.runtime.lifecycle import Lifecycle
from substratforge.errors import RuntimeError as RuntimeErrorBase
from substratforge.types import SandboxState


def test_happy_path():
    lc = Lifecycle()
    lc.mark_running()
    lc.mark_suspending()
    lc.mark_suspended()
    lc.mark_resuming()
    lc.mark_running()
    assert lc.state == SandboxState.RUNNING


def test_illegal_transition():
    lc = Lifecycle()
    lc.mark_running()
    with pytest.raises(RuntimeErrorBase):
        lc.mark_destroyed()  # RUNNING -> DESTROYED 非法
