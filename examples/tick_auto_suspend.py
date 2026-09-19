# -*- coding: utf-8 -*-
"""自动挂起演示：心跳看门狗发现空闲 -> tick() 自动挂起。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge import Substrate


def main():
    s = Substrate.from_config({
        "sandbox": {"max_idle_seconds": 0.05},
        "scheduler": {"idle_suspend_after": 0.05},
        "storage": {"backend": "memory"},
        "snapshot": {"compression": "gzip"},
    })
    name = "auto-suspend-demo"
    s.spawn(name, command=["python", "-c", "import time; time.sleep(86400)"])
    print("初始状态:", s.get(name).state.value)
    time.sleep(0.1)  # 超过空闲阈值
    s.tick()
    print("tick 后状态:", s.get(name).state.value)
    s.destroy(name)


if __name__ == "__main__":
    main()
