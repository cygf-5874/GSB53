"""fmtnum —— 定点数字格式化（仅标准库）。

对外入口是 :func:`format_fixed`；参数不合法时抛 :class:`FmtNumError`。
"""

from .format import format_fixed
from .grouping import GROUPINGS, group_digits
from .rounding import FmtNumError, MODES, round_digits, to_decimal

__all__ = [
    "format_fixed",
    "FmtNumError",
    "MODES",
    "GROUPINGS",
    "group_digits",
    "round_digits",
    "to_decimal",
]

__version__ = "0.4.2"
