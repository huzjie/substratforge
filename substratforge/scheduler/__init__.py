# -*- coding: utf-8 -*-
"""密度感知调度器：在「活跃数」与「驻留密度」之间做权衡。

核心思路（对应 Agent Substrate 的 10x 密度）：

1. 装箱（packing）：把活跃沙箱尽量压到少数宿主上，腾出整机做冷停靠
2. 空闲挂起（idle suspend）：超过 idle 阈值的沙箱自动 SUSPEND -> 快照落盘
3. 驱逐（eviction）：冷停靠区超限时按策略淘汰最久未用的快照
4. 晋升（promotion）：resume 请求到达时在 resume 预算（默认 500ms）内从冷恢复

策略对象统一走 registry，新增策略只需注册一个类。
"""
from ..core.registry import make_registry

policy_registry = make_registry("eviction_policy")

from .packing import BinPacker  # noqa: E402,F401
from .eviction import (  # noqa: E402,F401
    LRUEviction, LFUEviction, FIFOEviction, NoEviction,
)
from .promotion import PromotionEngine  # noqa: E402,F401
from .placement import PlacementEngine  # noqa: E402,F401
from .scheduler import DensityScheduler  # noqa: E402,F401

__all__ = [
    "DensityScheduler", "BinPacker", "PromotionEngine", "PlacementEngine",
    "LRUEviction", "LFUEviction", "FIFOEviction", "NoEviction", "policy_registry",
]
