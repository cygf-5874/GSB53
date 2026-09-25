"""整数部分的千分位分组。"""

from .rounding import FmtNumError

GROUPINGS = (None, "thousand", "indian")


def _groups_from_right(digits, size):
    groups = []
    while digits:
        groups.append(digits[-size:])
        digits = digits[:-size]
    return ",".join(reversed(groups))


def group_digits(int_part, grouping):
    """给整数位串加千分位分隔符。``int_part`` 只含数字，不含符号。"""
    if grouping is None:
        return int_part
    if grouping == "thousand":
        return _groups_from_right(int_part, 3)
    if grouping == "indian":
        if len(int_part) <= 3:
            return int_part
        head, tail = int_part[:-3], int_part[-3:]
        groups = [tail]
        while head:
            groups.append(head[-3:])
            head = head[:-3]
        return ",".join(reversed(groups))
    raise FmtNumError("不支持的分组方式：%r" % (grouping,))
