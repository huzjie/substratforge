# -*- coding: utf-8 -*-
"""远程 SDK 示例：连接 REST 服务并操作沙箱（需先 substratforge serve）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge.serving import Client


def main():
    client = Client(base_url="http://127.0.0.1:8080")
    print("health:", client.health())
    spec = {"name": "remote-demo", "image": "python:3.12", "command": ["python", "-c", "import time; time.sleep(86400)"]}
    print("spawn:", client.spawn(spec))
    print("suspend:", client.suspend("remote-demo"))
    print("resume:", client.resume("remote-demo"))
    print("stats:", client.stats())


if __name__ == "__main__":
    main()
