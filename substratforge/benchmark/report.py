# -*- coding: utf-8 -*-
"""报告生成：把基准结果渲染成 Markdown / JSON。"""
from __future__ import annotations

import json
from typing import Any


class ReportGenerator:
    """报告生成器。"""

    @staticmethod
    def to_markdown(results: list) -> str:
        lines = ["# 基准测试报告", ""]
        lines.append("| 基准 | 耗时(s) | 结果 |")
        lines.append("|---|---|---|")
        for r in results:
            status = "✅" if r.passed else f"❌ {r.error}"
            lines.append(f"| {r.name} | {r.duration_seconds} | {status} |")
        lines.append("")
        for r in results:
            if r.metrics:
                lines.append(f"## {r.name}")
                lines.append("```")
                lines.append(json.dumps(r.metrics, ensure_ascii=False, indent=2))
                lines.append("```")
                lines.append("")
        return "\n".join(lines)

    @staticmethod
    def to_json(results: list) -> str:
        return json.dumps([r.as_dict() for r in results], ensure_ascii=False, indent=2)


__all__ = ["ReportGenerator"]
