# -*- coding: utf-8 -*-
"""运行时专用异常（重导出，便于按域捕获）。"""
from ..errors import RuntimeError as RuntimeErrorBase

__all__ = ["RuntimeErrorBase"]
