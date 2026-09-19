# -*- coding: utf-8 -*-
"""沙箱网络策略：出口带宽限制与 ACL 描述（数据模型 + 校验）。

真正的流量整形依赖宿主侧 tc / nftables，本模块提供策略数据模型、
合法性校验，以及生成 tc/nftables 规则文本的纯函数，便于接入宿主网络层。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..errors import ConfigurationError


@dataclass
class NetworkPolicy:
    """网络策略：默认拒绝或默认允许，配合规则列表。"""
    default_allow: bool = False
    allow_egress_cidrs: list[str] = field(default_factory=list)
    deny_egress_cidrs: list[str] = field(default_factory=list)
    egress_kbps: int = 0          # 0 = 不限
    ingress_kbps: int = 0
    dns_allow: bool = True


def validate(policy: NetworkPolicy) -> None:
    """校验策略合法性，非法抛 ConfigurationError。"""
    if policy.egress_kbps < 0 or policy.ingress_kbps < 0:
        raise ConfigurationError("带宽限制不能为负")
    for cidr in policy.allow_egress_cidrs + policy.deny_egress_cidrs:
        if "/" not in cidr:
            raise ConfigurationError(f"非法的 CIDR: {cidr!r}")


def tc_rules(iface: str, policy: NetworkPolicy) -> list[str]:
    """生成 tc 限速规则文本（供宿主执行）。"""
    rules: list[str] = []
    if policy.egress_kbps:
        kbps = policy.egress_kbps
        rules.append(f"tc qdisc add dev {iface} root handle 1: htb default 10")
        rules.append(f"tc class add dev {iface} parent 1: classid 1:10 htb rate {kbps}kbit")
    if policy.ingress_kbps:
        kbps = policy.ingress_kbps
        rules.append(f"tc qdisc add dev {iface} handle ffff: ingress")
        rules.append(f"tc filter add dev {iface} parent ffff: protocol ip u32 match u32 0 0 police rate {kbps}kbit drop")
    return rules


def nft_rules(policy: NetworkPolicy) -> list[str]:
    """生成 nftables 规则文本（等价语义）。"""
    rules: list[str] = []
    action = "accept" if policy.default_allow else "drop"
    rules.append(f"chain substratforge-egress {{ type filter hook output priority 0; policy {action}; }}")
    for cidr in policy.allow_egress_cidrs:
        rules.append(f"ip daddr {cidr} accept")
    for cidr in policy.deny_egress_cidrs:
        rules.append(f"ip daddr {cidr} drop")
    return rules


__all__ = ["NetworkPolicy", "validate", "tc_rules", "nft_rules"]
