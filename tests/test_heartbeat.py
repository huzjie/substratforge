# -*- coding: utf-8 -*-
import time

from substratforge.runtime.heartbeat import HeartbeatWatchdog


def test_idle_candidate():
    w = HeartbeatWatchdog(idle_timeout=0.01, dead_timeout=100)
    w.beat("a")
    time.sleep(0.02)
    assert "a" in w.idle_candidates()
