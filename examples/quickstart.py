# -*- coding: utf-8 -*-
"""快速上手：零依赖跑一遍挂起/恢复。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge import Substrate

def main():
    s = Substrate.from_config()
    s.demo()

if __name__ == "__main__":
    main()
