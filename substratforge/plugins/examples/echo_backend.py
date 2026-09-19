# -*- coding: utf-8 -*-
"""可独立运行的 echo 后端示例：注册后 spawn 一个 echo 沙箱。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from substratforge import Substrate
from substratforge.plugins.sandbox.example_backend import setup

def main():
    setup(None)  # 注册 echo 后端
    s = Substrate.from_config({"sandbox": {"default_isolation": "process"}})
    # echo 后端在 spawn 时不真正跑进程，仅登记
    s.backend = __import__("substratforge.sandbox", fromlist=["backend_registry"]).backend_registry.get("echo")()
    h = s.spawn("echo-demo")
    print("spawned:", h.as_dict()["sandbox_id"], h.as_dict()["state"])

if __name__ == "__main__":
    main()
