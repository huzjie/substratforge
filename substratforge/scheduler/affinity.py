# -*- coding: utf-8 -*-
"""亲和规则：约束沙箱放置（同租户聚合、反亲和隔离）。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AffinityRule:
    """一条亲和规则。"""
    key: str                 # 标签键
    operator: str            # in | notin
    values: list[str] = field(default_factory=list)


class AffinityEngine:
    """亲和规则匹配。"""

    def __init__(self, rules: list[AffinityRule] | None = None):
        self.rules = rules or []

    def matches(self, labels: dict[str, str]) -> bool:
        for rule in self.rules:
            val = labels.get(rule.key)
            if rule.operator == "in":
                if val not in rule.values:
                    return False
            elif rule.operator == "notin":
                if val in rule.values:
                    return False
        return True


__all__ = ["AffinityRule", "AffinityEngine"]
