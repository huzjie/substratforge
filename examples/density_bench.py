# -*- coding: utf-8 -*-
"""密度基准：测量挂起/恢复耗时与冷停靠密度。

跑 N 个沙箱，逐个挂起，统计：总耗时、单次平均挂起/恢复耗时、
以及「单机冷停靠密度」（挂起的沙箱数）。
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from substratforge import Substrate

N = 20  # 沙箱数量


def main():
    s = Substrate.from_config()
    names = [f"bench-{i}" for i in range(N)]

    print(f"[density] 创建 {N} 个沙箱 ...")
    for n in names:
        s.spawn(n, command=["python", "-c", "import time; time.sleep(86400)"])

    print("[density] 逐个挂起 ...")
    t0 = time.perf_counter()
    for n in names:
        s.suspend(n)
    suspend_total = (time.perf_counter() - t0) * 1000

    print("[density] 逐个恢复 ...")
    t1 = time.perf_counter()
    for n in names:
        s.resume(n)
    resume_total = (time.perf_counter() - t1) * 1000

    print("[density] 清理 ...")
    for n in names:
        s.destroy(n)

    print("=" * 60)
    print(f"沙箱数        : {N}")
    print(f"挂起总耗时     : {suspend_total:.0f} ms（平均 {suspend_total/N:.1f} ms）")
    print(f"恢复总耗时     : {resume_total:.0f} ms（平均 {resume_total/N:.1f} ms）")
    print(f"冷停靠密度     : {N} 个休眠环境 / 单机")
    print("=" * 60)


if __name__ == "__main__":
    main()
