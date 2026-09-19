# -*- coding: utf-8 -*-
"""钩子演示：在挂起/恢复前后注入日志。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge import Substrate
from substratforge.core.hooks import Hooks


def main():
    hooks = Hooks()
    hooks.on("after_suspend", lambda sid: print(f"[hook] {sid} 已挂起"))
    hooks.on("after_resume", lambda sid: print(f"[hook] {sid} 已恢复"))

    s = Substrate.from_config({"storage": {"backend": "memory"}, "snapshot": {"compression": "gzip"}})
    name = "hooks-demo"
    s.spawn(name, command=["python", "-c", "import time; time.sleep(86400)"])
    s.suspend(name)
    hooks.emit("after_suspend", name)
    s.resume(name)
    hooks.emit("after_resume", name)
    s.destroy(name)


if __name__ == "__main__":
    main()
