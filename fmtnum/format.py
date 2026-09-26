"""``format_fixed``：定点数字格式化的对外入口。"""

from .grouping import GROUPINGS, group_digits
from .rounding import FmtNumError, MODES, round_digits, to_decimal


def _check_digits(digits):
    if isinstance(digits, bool) or not isinstance(digits, int):
        raise FmtNumError("digits 必须是整数：%r" % (digits,))
    if digits < 0:
        raise FmtNumError("digits 不能为负：%r" % (digits,))


def _check_mode(mode):
    if mode not in MODES:
        raise FmtNumError("不支持的舍入模式：%r" % (mode,))


def _check_grouping(grouping):
    if grouping not in GROUPINGS:
        raise FmtNumError("不支持的分组方式：%r" % (grouping,))


def _split(number):
    """把 Decimal 拆成 (是否负号, 整数位串, 小数位串)，用无指数表示。"""
    text = format(number, "f")
    neg = text.startswith("-")
    if neg:
        text = text[1:]
    if "." in text:
        int_part, frac_part = text.split(".", 1)
    else:
        int_part, frac_part = text, ""
    return neg, int_part, frac_part


def format_fixed(value, digits, mode, grouping=None):
    """把 ``value`` 按 ``digits`` 位小数、``mode`` 舍入，可选千分位分组。"""
    _check_digits(digits)
    _check_mode(mode)
    _check_grouping(grouping)

    number = to_decimal(value)
    if number.is_nan():
        return "NaN"
    if number.is_infinite():
        return "-Infinity" if number.is_signed() else "Infinity"

    neg, int_part, frac_part = _split(number)
    int_part, frac_part = round_digits(int_part, frac_part, digits, mode)
    if not int_part:
        int_part = "0"

    body = group_digits(int_part, grouping) + ("." + frac_part if digits > 0 else "")
    if neg:
        body = "-" + body
    return body
