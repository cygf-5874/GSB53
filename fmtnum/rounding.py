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
    if isinstance(value, float):
        # float 按最短往返十进制表示使用，绝不取二进制浮点的精确值。
        return Decimal(str(value))
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        try:
            return Decimal(value.strip())
        except InvalidOperation:
            raise FmtNumError("无法解析的数值：%r" % (value,))
    raise FmtNumError("不支持的数值类型：%s" % type(value).__name__)


def _increment_magnitude(last_kept, rest, mode):
    """``rest`` 是被丢弃的小数位串（至少一位），返回绝对值末位是否加一。"""
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
    # head == "5"：后面还有非零位说明严格大于半位，一律进位。
    if rest[1:].strip("0"):
        return True
    if mode == "HALF_UP":
        return True
    # HALF_EVEN：恰好半位，末位为奇数时进位。
    return int(last_kept) % 2 == 1


def round_digits(int_part, frac_part, digits, mode):
    """把 ``int_part.frac_part``（绝对值的十进制位串）舍入到 ``digits`` 位小数。

    返回 ``(int_part, frac_part)``，均为字符串。
    """
    if digits >= len(frac_part):
        return int_part, frac_part + "0" * (digits - len(frac_part))

    keep = frac_part[:digits]
    last_kept = keep[-1] if keep else int_part[-1]
    if not _increment_magnitude(last_kept, frac_part[digits:], mode):
        return int_part, keep

    # 在「整数位 + 保留位」拼成的整数上加一，进位自然一路传播。
    total = len(int_part) + digits
    scaled = str(int(int_part + keep) + 1).zfill(total)
    if digits == 0:
        return scaled, ""
    return scaled[:-digits], scaled[-digits:]
