"""舍入模式与定点舍入。

只暴露 ``MODES``、``FmtNumError``、``to_decimal``、``round_digits``。
"""

from decimal import Decimal, InvalidOperation

MODES = ("HALF_UP", "HALF_EVEN", "DOWN", "UP")


class FmtNumError(ValueError):
    """入参不合法（位数、模式、分组方式或数值本身）。"""


def to_decimal(value):
    """把 ``str`` / ``int`` / ``float`` / ``Decimal`` 统一成 ``Decimal``。"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise FmtNumError("不支持的数值类型：bool")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value.strip())
        except InvalidOperation:
            raise FmtNumError("无法解析的数值：%r" % (value,))
    raise FmtNumError("不支持的数值类型：%s" % type(value).__name__)


def _should_round_up(rest, mode, last_kept):
    """rest 是被丢弃的小数位串（至少一位），last_kept 是保留部分末位数字。"""
    if not rest or not rest.strip("0"):
        return False
    if mode == "DOWN":
        return False
    if mode == "UP":
        return True
    head = rest[0]
    if head > "5":
        return True
    if head < "5":
        return False
    if rest[1:].strip("0"):
        return True
    if mode == "HALF_UP":
        return True
    return last_kept in "13579"


def round_digits(int_part, frac_part, digits, mode):
    """把 ``int_part.frac_part`` 舍入到 ``digits`` 位小数。

    返回 ``(int_part, frac_part)``，均为字符串。
    """
    if digits >= len(frac_part):
        return int_part, frac_part + "0" * (digits - len(frac_part))

    keep = frac_part[:digits]
    rest = frac_part[digits:]
    last_kept = (keep or int_part or "0")[-1]
    if not _should_round_up(rest, mode, last_kept):
        return int_part, keep

    if digits == 0:
        return str(int(int_part or "0") + 1), ""

    bumped = str(int(keep) + 1)
    if len(bumped) > len(keep):
        int_part = str(int(int_part or "0") + 1)
        bumped = bumped[1:]
    return int_part, bumped.zfill(len(keep))
