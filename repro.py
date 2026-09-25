"""调用方给的最小复现，别改。

调用方的原话是「同一个数字两次格式化出来不一样」：
同一个字面量，从浮点来源和从十进制来源进来，格式化结果对不上。
"""

import sys
from decimal import Decimal

from fmtnum import format_fixed

CASES = ("1.005", "2.675", "0.145")
DIGITS = 2
MODE = "HALF_UP"


def main():
    mismatched = 0
    for literal in CASES:
        from_float = format_fixed(float(literal), DIGITS, MODE)
        from_decimal = format_fixed(Decimal(literal), DIGITS, MODE)
        tag = "一致" if from_float == from_decimal else "不一致"
        print("%s 保留 %d 位 %s：float -> %s ；Decimal -> %s  [%s]"
              % (literal, DIGITS, MODE, from_float, from_decimal, tag))
        if from_float != from_decimal:
            mismatched += 1

    print("不一致 %d/%d" % (mismatched, len(CASES)))
    return 1 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
