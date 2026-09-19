# -*- coding: utf-8 -*-
"""本地 SDK 示例：直接调用引擎（无网络）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge import Substrate
from substratforge.serving import Client


def main():
    c = Client(substrate=Substrate.from_config())
    print("health:", c.health())
    c.spawn({"name": "local-demo"})
    print("suspend:", c.suspend("local-demo")["id"])
    c.resume("local-demo")
    print("stats:", c.stats())
    c.destroy("local-demo")


if __name__ == "__main__":
    main()
